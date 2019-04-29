# -*- coding: utf-8 -*-
import datetime
import telebot as tb
import requests
import urllib3
import socket
import time
import csv

from src import util as ut
from src import onedrive
from src.template import head,td_html,wk_html
path_of_log='D:/Workspace/logs'
path = ut.path_of_logindata


sttarttime=time.time()
us,tk=ut.getUserData(path,'teleToken')
token = tk
bot = tb.TeleBot(token)
logger = ut.initlog()
cachePath='cache.csv'
command_list = ['review', 'today', 'thiswk','lastwk','start', 'help','restart']
fieldnames = ut.fieldnames
head_ch = head.replace('<br>', '')

username, password=ut.getUserData(path,'tick')
logger.info('--> Initiating OneDrive Client')
client = onedrive.init_onedrive()
logger.info('--> Initiating Ticktick Client')
driver = ut.login(username, password, headless=False, linux=False)
time.sleep(8)


@bot.message_handler(commands=['start', 'help'])
def sartInfo(message):
    userid = str(message.from_user.id)
    for cmd in command_list:
        bot.send_message(userid,'/%s'%cmd)
    return


@bot.message_handler(commands=['restart'])
def sartInfo(message):
    userid = str(message.from_user.id)
    init_cache(userid)
    for cmd in command_list:
        bot.send_message(userid,'/%s'%cmd)
    return


@bot.message_handler(commands=['review'])
def sartInfo(message):
    global driver
    userid = str(message.from_user.id)
    # time.sleep(2)
    td, week =ut.get_today_and_thiswk(driver)
    ut.write_user_cache(userid,'today',td)
    ut.write_user_cache(userid,'week',week)
    # driver.close()
    bot.send_message(message.chat.id, 'Finished Initiating!')
    ut.write_user_cache(userid,'status','1')
    return


@bot.message_handler(commands=['getlog'])
def getlog(message):
    global driver
    userid = str(message.from_user.id)
    # time.sleep(2)
    today=ut.get_today(driver)
    week = ut.get_week(driver)
    # driver.close()
    bot.send_message(message.chat.id, 'Finished Initiating!')
    ut.write_user_cache(userid,'status','1')
    return


@bot.message_handler(commands=['today'])
def today(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id,'今日总结:\n%s'%(ut.get_user_cache(userid,'today')))
    bot.send_message(message.chat.id, '请评价今日(⭐)!')
    ut.write_user_cache(userid,'status','starsTD')
    return

@bot.message_handler(commands=['thisWK','thiswk'])
def thisWK(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id,'本周周报:\n%s'%(ut.get_user_cache(userid,'week')))
    bot.send_message(message.chat.id, '请评价本周(⭐)!')
    ut.write_user_cache(userid,'status','starsWK')
    return


@bot.message_handler(commands=['lastWK','lastwk'])
def lastWK(message):
    userid = str(message.from_user.id)
    driver.get('https://www.ticktick.com/#q/all/summary')
    time.sleep(5)
    days = driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[1]/div[1]/div/a/span')
    if '上周' not in days.text:
        days.click()
        driver.find_element_by_xpath('/html/body/div[10]/div/div/ul/li[4]/a').click()
        time.sleep(1)
    suma = driver.find_element_by_xpath('//*[@id="summary-text"]')
    ttt = suma.get_property('value')
    bot.send_message(message.chat.id,'上周周报:\n%s'%(ttt))
    bot.send_message(message.chat.id, '请评价上周(⭐)!')
    ut.write_user_cache(userid,'week',ttt)
    ut.write_user_cache(userid,'status','starsWK')
    return


def get_input(messages):
    global status
    for message in messages:
        with open(cachePath, "rt", encoding='utf-8') as log:
            reader = csv.DictReader(log)
            userList = [row['userID'] for row in reader]
        userid=str(message.from_user.id)
        if userid not in userList:
            init_cache(userid)
        logger.info(u'%s'%str(message.text))
        if message.from_user.first_name.lower() != 'joe':
            return
        for cmd in command_list:
            if message.text == '/%s' % cmd:
                return
        if ut.get_user_cache(userid,'status')=='starsTD':
           ut.write_user_cache(userid,'starTD',ut.convert_star(message.text))
           ut.write_user_cache(userid, 'status', 'commentTD')
           bot.send_message(message.chat.id, '评论与小结!')
           return
        if ut.get_user_cache(userid,'status')=='commentTD':
            ut.write_user_cache(userid, 'commentTD', message.text)
            tody = ut.get_user_cache(userid, 'today')
            stars = ut.get_user_cache(userid, 'starTD')
            sumi = '*Summary of today*:\n\n%s\n---------\n*Stars*:\n%s\n\n---------\n\n*Comment*:\n\n%s' % (tody, stars, message.text)
            bot.send_message(userid,sumi,parse_mode='Markdown')
            ut.write_user_cache(userid, 'status', 'svTD')
            bot.send_message(message.chat.id, '是否保存?')
            return
        if ut.get_user_cache(userid,'status')=='svTD' and ('是' in message.text or '保存' in message.text or '好' in message.text):
            wkk = ut.get_user_cache(userid, 'week')
            i=8
            while wkk[i]!='日':
                i+=1
            wk = wkk[:i+1]
            month_num = datetime.datetime.today().month
            today = datetime.date.today()
            tody = ut.get_user_cache(userid, 'today')
            stars = ut.get_user_cache(userid, 'starTD')
            comm=ut.get_user_cache(userid, 'commentTD')
            content = '%s\n---------\n<b>Stars</b>:\n%s\n\n---------\n\n<b>Comment</b>:\n\n%s'%(tody,stars,comm)
            content_td=content.replace('\n','<br>')
            susu = td_html.format(content_td=content_td)
            sumi = head_ch + susu
            ut.saveFile('%s月' % month_num, '每日回顾-%s'%today,sumi,client)
            bot.send_message(userid,'Succeed!')
            ut.write_user_cache(userid, 'status', '0')
            bot.send_message(message.chat.id, 'It is done.')
            return
        if ut.get_user_cache(userid,'status')=='starsWK':
           ut.write_user_cache(userid,'starWK',ut.convert_star(message.text))
           ut.write_user_cache(userid, 'status', 'commentWK')
           bot.send_message(message.chat.id, '评论与小结!')
           return
        if ut.get_user_cache(userid,'status')=='commentWK':
            ut.write_user_cache(userid, 'commentWK', message.text)
            tody = ut.get_user_cache(userid, 'week')
            stars = ut.get_user_cache(userid, 'starWK')
            sumi = '*Summary of week*:\n\n%s\n---------\n*Stars*:\n%s\n\n---------\n\n*Comment*:\n\n%s' % (tody, stars, message.text)
            bot.send_message(userid,sumi,parse_mode='Markdown')
            ut.write_user_cache(userid, 'status', 'svWK')
            bot.send_message(message.chat.id, '是否保存?')
            return
        if ut.get_user_cache(userid,'status')=='svWK' and ('是' in message.text or '保存' in message.text or '好' in message.text):
            wkk = ut.get_user_cache(userid, 'week')
            i = 8
            while wkk[i] != '日':
                i += 1
            wk = wkk[:i + 1]
            month_num = datetime.datetime.today().month
            stars = ut.get_user_cache(userid, 'starWK')
            comm = ut.get_user_cache(userid, 'commentWK')
            content = '%s\n---------\n<b>Stars</b>:\n%s\n\n---------\n\n<b>Comment</b>:\n\n%s'%(wkk,stars,comm)
            content_td = content.replace('\n', '<br>')
            susu = wk_html.format(week=wk,content_wk=content_td)
            sumi = head_ch + susu
            ut.saveFile('%s月' % month_num, '每周回顾-%s' %wk, sumi, client)
            bot.send_message(userid,'Succeed!')
            ut.write_user_cache(userid, 'status', '0')
            bot.send_message(message.chat.id, 'It is done.')
            return


def init_cache(userid):
    global cachePath
    with open(cachePath, "a+", encoding='utf-8') as log:
        writer = csv.writer(log)
        writer.writerow([userid, '0','','','',''])


with open(cachePath, 'w', newline='',encoding='utf-8') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(fieldnames )
ti = datetime.datetime.now()
logger.info('--> Bot started!')
print("Bot started: " + str(ti))
print(str(time.time()-sttarttime))
bot.set_update_listener(get_input)
try:
    bot.polling(none_stop=True, interval=0, timeout=3)
except (OSError, TimeoutError, ConnectionResetError, requests.exceptions.ReadTimeout, urllib3.exceptions.ReadTimeoutError,
        socket.timeout, RecursionError, urllib3.exceptions.ProtocolError,requests.exceptions.ConnectionError) as e:
    logger.error('---> %s' % str(e))
    time.sleep(0.5)


