#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import telebot as tb
import requests
import urllib3
import socket
import time
import csv
import sys
import os
sys.path.append("D:\Workspace\TeleMaster/")
sys.path.append("/home/pi/TeleMaster/")

from src import util as ut
from src import onedrive
from src.template import head,td_html,wk_html
path_of_log='D:\Workspace\TeleMaster'
path = ut.path_of_logindata

time.sleep(30)
sttarttime=time.time()
us,tk=ut.getUserData(path,'teleToken')
token = tk
bot = tb.TeleBot(token)
logger = ut.initlog()
cachePath='cache.csv'
command_list = ['today', 'yesterday','thiswk','lastwk','start','library','film']
fieldnames = ut.fieldnames
head_ch = head.replace('<br>', '')

username, password=ut.getUserData(path,'tick')
logger.info('--> Initiating OneDrive Client')
client = onedrive.init_onedrive()
logger.info('--> Initiating Ticktick Client')
driver = ut.login(username, password, headless=False, linux=True)
time.sleep(8)


@bot.message_handler(commands=['start', 'help'])
def sartInfo(message):
    userid = str(message.from_user.id)
    for cmd in command_list:
        bot.send_message(userid,'/%s'%cmd)
    return


@bot.message_handler(commands=['library'])
def lib(message):
    userid = str(message.from_user.id)
    info=ut.get_seat_info()
    bot.send_message(userid,'%s'%info)
    return


@bot.message_handler(commands=['film'])
def lib(message):
    userid = str(message.from_user.id)
    os.system('python3 /home/pi/FilmScrap/src/thefilmwacher.py')
    bot.send_message(userid,'Sending EMail...')
    return

@bot.message_handler(commands=['today'])
def today(message):
    userid = str(message.from_user.id)
    td = ut.get_Summary(driver, 'Today')
    ut.write_user_cache(userid, 'summary', td)
    bot.send_message(message.chat.id,'今日总结:\n%s'%td)
    bot.send_message(message.chat.id, '请评价今日(⭐)!')
    ut.write_user_cache(userid,'status','starsTD')
    ut.write_user_cache(userid,'time',datetime.date.today())
    return


@bot.message_handler(commands=['thisWK','thiswk'])
def thisWK(message):
    userid = str(message.from_user.id)
    td = ut.get_Summary(driver, 'This Week')
    ut.write_user_cache(userid, 'summary', td)
    bot.send_message(message.chat.id,'本周周报:\n%s'%td)
    bot.send_message(message.chat.id, '请评价本周(⭐)!')
    i=td.index('Completed')  
    wk = td[:i - 2]
    ut.write_user_cache(userid, 'time', wk)
    ut.write_user_cache(userid,'status','starsWK')
    return


@bot.message_handler(commands=['lastWK','lastwk'])
def lastWK(message):
    userid = str(message.from_user.id)
    td = ut.get_Summary(driver, 'Last Week')
    ut.write_user_cache(userid, 'summary', td)
    bot.send_message(message.chat.id, '上周周报:\n%s' %td)
    bot.send_message(message.chat.id, '请评价上周(⭐)!')
    i=td.index('Completed')  
#    i = 8
#    while td[i] != '日':
#        i += 1
    wk = td[:i - 2]
    ut.write_user_cache(userid, 'time', wk)
    ut.write_user_cache(userid, 'status', 'starsWK')
    return


@bot.message_handler(commands=['yesterday','yd'])
def yesterdAY(message):
    userid = str(message.from_user.id)
    td = ut.get_Summary(driver, 'Yesterday')
    ut.write_user_cache(userid, 'summary', td)
    bot.send_message(message.chat.id, '今日总结:\n%s' % td)
    bot.send_message(message.chat.id, '请评价今日(⭐)!')
    ut.write_user_cache(userid, 'status', 'starsTD')
    ut.write_user_cache(userid, 'time', ut.get_yesterday())
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
           ut.write_user_cache(userid,'star',ut.convert_star(message.text))
           ut.write_user_cache(userid, 'status', 'commentTD')
           bot.send_message(message.chat.id, '评论与小结!')
           return
        if ut.get_user_cache(userid,'status')=='commentTD':
            ut.write_user_cache(userid, 'comment', message.text)
            tody = ut.get_user_cache(userid, 'summary')
            stars = ut.get_user_cache(userid, 'star')
            sumi = 'Summary of today:\n\n%s\n---------\nStars:\n%s\n\n---------\n\nComment:\n\n%s' % (tody, stars, message.text)
            bot.send_message(userid,sumi)
            ut.write_user_cache(userid, 'status', 'svTD')
            bot.send_message(message.chat.id, '是否保存?')
            return
        if ut.get_user_cache(userid,'status')=='svTD' and ('是' in message.text or '保存' in message.text or '好' in message.text):
            td = ut.get_user_cache(userid, 'summary')
#            i=0
#            while wkk[i]!='日':
#                i+=1
#            wk = wkk[:i+1]
            i=td.index('Completed')  
            wk = td[:i - 2]
            month_num = datetime.datetime.today().month
            time = ut.get_user_cache(userid, 'time')
            tody = ut.get_user_cache(userid, 'summary')
            stars = ut.get_user_cache(userid, 'star')
            comm=ut.get_user_cache(userid, 'comment')
            content = '%s\n---------\n<b>Stars</b>:\n%s\n\n---------\n\n<b>Comment</b>:\n\n%s'%(tody,stars,comm)
            content_td=content.replace('\n','<br>')
            susu = td_html.format(content_td=content_td)
            sumi = head_ch + susu
            ut.saveFile('%s月' % month_num, '每日回顾-%s'%time,sumi,client)
            bot.send_message(userid,'Succeed!')
            ut.write_user_cache(userid, 'status', '0')
            bot.send_message(message.chat.id, 'It is done.')
            return
        if ut.get_user_cache(userid,'status')=='starsWK':
           ut.write_user_cache(userid,'star',ut.convert_star(message.text))
           ut.write_user_cache(userid, 'status', 'commentWK')
           bot.send_message(message.chat.id, '评论与小结!')
           return
        if ut.get_user_cache(userid,'status')=='commentWK':
            ut.write_user_cache(userid, 'comment', message.text)
            tody = ut.get_user_cache(userid, 'summary')
            stars = ut.get_user_cache(userid, 'star')
            sumi = 'Summary of week:\n\n%s\n---------\nStars:\n%s\n\n---------\n\nComment:\n\n%s' % (tody, stars, message.text)
            bot.send_message(userid,sumi)
            ut.write_user_cache(userid, 'status', 'svWK')
            bot.send_message(message.chat.id, '是否保存?')
            return
        if ut.get_user_cache(userid,'status')=='svWK' and ('是' in message.text or '保存' in message.text or '好' in message.text):
            wkk = ut.get_user_cache(userid, 'summary')
            wk = ut.get_user_cache(userid, 'time')
            month_num = datetime.datetime.today().month
            stars = ut.get_user_cache(userid, 'star')
            comm = ut.get_user_cache(userid, 'comment')
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


