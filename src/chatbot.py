import datetime
import telebot as tb
import random
import re
import requests
import urllib3
import socket
import time
import csv

from TeleMaster.src import util as ut
from TeleMaster.src import onedrive

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
username, password=ut.getUserData(path,'tick')
logger.log('--> Initiating OneDrive Client')
client = onedrive.init_onedrive()
logger.log('--> Initiating Ticktick Client')
driver = ut.login(username, password, headless=True, linux=False)
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
    today=ut.get_today(driver)
    ut.write_user_cache(userid,'today',today)
    week = ut.get_week(driver)
    ut.write_user_cache(userid,'week',week)
    # driver.close()
    bot.send_message(message.chat.id, 'Finished Initiating!')
    ut.write_user_cache(userid,'status','1')
    return


@bot.message_handler(commands=['today'])
def today(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id,'Here is the summary of today:\n%s'%(ut.get_user_cache(userid,'today')))
    bot.send_message(message.chat.id, 'Please rate today with stars⭐!')
    ut.write_user_cache(userid,'status','starsTD')
    return

@bot.message_handler(commands=['thisWK','thiswk'])
def thisWK(message):
    userid = str(message.from_user.id)
    bot.send_message(message.chat.id,'Here is the summary of this week:\n%s'%(ut.get_user_cache(userid,'week')))
    bot.send_message(message.chat.id, 'Please rate this week with stars⭐!')
    ut.write_user_cache(userid,'status','starsWK')
    return


@bot.message_handler(commands=['lastWK','lastwk'])
def lastWK(message):
    userid = str(message.from_user.id)
    driver.get('https://www.ticktick.com/#q/all/summary')
    days = driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[1]/div[1]/a/span')
    if '上周' not in days.text:
        days.click()
        driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[1]/div[1]/ul/li[4]/a').click()
        time.sleep(1)
    suma = driver.find_element_by_xpath('//*[@id="summary-text"]')
    ttt = suma.get_property('value')
    bot.send_message(message.chat.id,'Here is the summary of last week:\n%s'%(ttt))
    bot.send_message(message.chat.id, 'Please rate last week with stars⭐!')
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
        logger.log(str(message.text))
        if message.from_user.first_name.lower() != 'joe':
            return
        for cmd in command_list:
            if message.text == '/%s' % cmd:
                return
        if ut.get_user_cache(userid,'status')=='starsTD':
           ut.write_user_cache(userid,'starTD',ut.convert_star(message.text))
           ut.write_user_cache(userid, 'status', 'commentTD')
           bot.send_message(message.chat.id, 'Now please write comment!')
           return
        if ut.get_user_cache(userid,'status')=='commentTD':
            ut.write_user_cache(userid, 'commentTD', message.text)
            tody = ut.get_user_cache(userid, 'today')
            stars = ut.get_user_cache(userid, 'starTD')
            sumi = '<b>Summary of today</b>:\n\n%s\n---------\n<b>Stars</b>:\n%s\n\n---------\n\n<b>Comment</b>:\n\n%s' % (tody, stars, message.text)
            bot.send_message(userid,sumi,parse_mode='HTML')
            ut.write_user_cache(userid, 'status', 'svTD')
            bot.send_message(message.chat.id, 'Do you want to save it?')
        if ut.get_user_cache(userid,'status')=='svTD' and 'yes' in message.text.lower():
            wkk = ut.get_user_cache(userid, 'week')
            i=8
            while wkk[i]!='日':
                i+=1
            wk = wkk[:i+1]
            today = datetime.date.today()
            tody = ut.get_user_cache(userid, 'today')
            stars = ut.get_user_cache(userid, 'starTD')
            comm=ut.get_user_cache(userid, 'commentTD')
            sumi = '<b>Summary of today</b>:\n\n%s\n---------\n<b>Stars</b>:\n%s\n\n---------\n\n<b>Comment</b>:\n\n%s' % (tody, stars, comm)
            ut.saveFile(wk,'DailyReview-%s'%today,sumi,client)
            bot.send_message(userid,'Succeed!')
            ut.write_user_cache(userid, 'status', '0')
            bot.send_message(message.chat.id, 'It is done.')


        if ut.get_user_cache(userid,'status')=='starsWK':
           ut.write_user_cache(userid,'starWK',ut.convert_star(message.text))
           ut.write_user_cache(userid, 'status', 'commentWK')
           bot.send_message(message.chat.id, 'Now please write comment!')
           return
        if ut.get_user_cache(userid,'status')=='commentWK':
            ut.write_user_cache(userid, 'commentWK', message.text)
            tody = ut.get_user_cache(userid, 'week')
            stars = ut.get_user_cache(userid, 'starWK')
            sumi = '<b>Summary of week</b>:\n\n%s\n---------\n<b>Stars</b>:\n%s\n\n---------\n\n<b>Comment</b>:\n\n%s' % (tody, stars, message.text)
            bot.send_message(userid,sumi,parse_mode='HTML')
            ut.write_user_cache(userid, 'status', 'svWK')
            bot.send_message(message.chat.id, 'Do you want to save it?')
        if ut.get_user_cache(userid,'status')=='svWK' and 'yes' in message.text.lower():
            wkk = ut.get_user_cache(userid, 'week')
            i = 8
            while wkk[i] != '日':
                i += 1
            wk = wkk[:i + 1]
            stars = ut.get_user_cache(userid, 'starWK')
            comm=ut.get_user_cache(userid, 'commentWK')
            sumi = '<b>Summary of week</b>:\n\n%s\n---------\n<b>Stars</b>:\n%s\n\n------\n\n<b>Comment</b>:\n\n%s' % (tody, stars, comm)
            ut.saveFile(wk,'WeeklyReview-%s'%wk,sumi,client)
            bot.send_message(userid,'Succeed!')
            ut.write_user_cache(userid, 'status', '0')
            bot.send_message(message.chat.id, 'It is done.')


def init_cache(userid):
    global cachePath
    with open(cachePath, "a+", encoding='utf-8') as log:
        writer = csv.writer(log)
        writer.writerow([userid, '0','','','',''])


with open(cachePath, 'w', newline='',encoding='utf-8') as csvfile:
    spamwriter = csv.writer(csvfile)
    spamwriter.writerow(fieldnames )
ti = datetime.datetime.now()
logger.log('--> Bot started!')
print("Bot started: " + str(ti))
print(str(time.time()-sttarttime))
bot.set_update_listener(get_input)
try:
    bot.polling(none_stop=True, interval=0, timeout=3)
except (OSError, TimeoutError, ConnectionResetError, requests.exceptions.ReadTimeout, urllib3.exceptions.ReadTimeoutError,
        socket.timeout, RecursionError, urllib3.exceptions.ProtocolError,requests.exceptions.ConnectionError) as e:
    logger.error('---> %s' % str(e))
    time.sleep(0.5)

