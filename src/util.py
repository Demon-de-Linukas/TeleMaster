import os
import logging
import time
import csv
import onedrivesdk
import sys
import requests as rq
import re
sys.path.append("D:\Workspace\TeleMaster/")


import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src import cypter as cp
from csv import Error

logPath = 'cache.csv'
fieldnames = ['userID','status','summary','time','star','comment']
#path_of_logindata = '/home/pi/loginData.csv'
path_of_logindata = 'D:/Workspace/loginData.csv'


def login(username, password,headless,linux):
    options = Options()
    options.add_argument('window-size=1200x600')
    options.add_argument('--lang=zh-CN')
    options.add_argument('--dns-prefetch-disable')
    if headless:
        options.add_argument('headless')
    if linux:
        browser = webdriver.Chrome(chrome_options=options)#, executable_path='/usr/lib/chromium-browser/chromedriver')
    else:
        browser = webdriver.Chrome(chrome_options=options)
    browser.get("https://www.ticktick.com/signin")
    time.sleep(2)
    usernameBox = browser.find_element_by_name('email')
    passwordBox = browser.find_element_by_name('password')
    usernameBox.send_keys(username)
    passwordBox.send_keys(password)
    browser.find_element_by_xpath('//*[@id="submit-btn"]').click()
    time.sleep(2)
    return browser


def get_week(driver):
    driver.get('https://www.ticktick.com/#q/all/summary')
    days=driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[1]/div[1]/div/a/span')
    if '本周' not in days.text:
        days.click()
        driver.find_element_by_xpath('/html/body/div[10]/div/div/ul/li[1]/a').click()
        time.sleep(1)
    driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[1]/a').click()
    driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[1]/ul/li[3]').click()
    suma=driver.find_element_by_xpath('//*[@id="summary-text"]')
    ttt = suma.get_property('value')
    return ttt


def get_Summary(driver, timeRef):
    driver.get('https://www.ticktick.com/#q/all/summary')
    time.sleep(5)
    days=driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[1]/div[1]/div/a/span')
    i=1
    while i<6:
        if timeRef not in days.text:
            days.click()
            driver.find_element_by_xpath('/html/body/div[11]/div/div/ul/li[%s]/a'%i).click()
            time.sleep(1)
            days = driver.find_element_by_xpath(
                '//*[@id="container-main"]/div[3]/div/div[1]/div/div[1]/div[1]/div/a/span')
            i+=1
        else:
            break
    #打开选项表
    driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[2]/div[2]/a').click()
    #得到选项表信息
    detailslist = driver.find_element_by_xpath("//*[contains(@class, 'list-wrapper antiscroll-wrap')]")
    #Check the shown property
    attrib_list=['Detail','Progress','List']
    for attrib in attrib_list:
        xpath = "//li[text()='%s']" % attrib
        element = detailslist.find_element_by_xpath(xpath)
        if 'option-item-selected' not in element.get_attribute('class'):
            element.click()
    #点击确认
    driver.find_element_by_xpath("//*[contains(@class, 'btn btn-confirm btn-primary btn-tny')]").click()
    #更改排序方式
    driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[2]/div[1]/a').click()
    driver.find_element_by_xpath("//a[text()='By Completion']").click()
    #得到文本目标
    suma_td=driver.find_element_by_xpath('//*[@id="summary-text"]')
    today = suma_td.get_property('value')

    return today


def get_thiswk(driver):
    driver.get('https://www.ticktick.com/#q/all/summary')
    time.sleep(5)
    days=driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[1]/div[1]/div/a/span')
    if '本周' not in days.text:
        days.click()
        driver.find_element_by_xpath('/html/body/div[10]/div/div/ul/li[3]/a').click()
        time.sleep(1)
    # 打开选项表
    driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[2]/div[2]/a').click()
    # 得到选项表信息
    detailslist = driver.find_element_by_xpath("//*[contains(@class, 'list-wrapper antiscroll-wrap')]")
    # Check the shown property
    attrib_list = ['完成日期', '进度', '所属清单']
    for attrib in attrib_list:
        xpath = "//li[text()='%s']" % attrib
        element = detailslist.find_element_by_xpath(xpath)
        if 'option-item-selected' not in element.get_attribute('class'):
            element.click()
    # 点击确认
    driver.find_element_by_xpath("//*[contains(@class, 'btn btn-confirm btn-primary btn-tny')]").click()
    # 更改排序方式
    driver.find_element_by_xpath('//*[@id="container-main"]/div[3]/div/div[1]/div/div[2]/div[1]/a').click()
    driver.find_element_by_xpath("//a[text()='按完成度']").click()
    # 得到文本目标
    suma_wk = driver.find_element_by_xpath('//*[@id="summary-text"]')
    thisweek = suma_wk.get_property('value')
    return thisweek



def initlog():
    today = datetime.date.today()
    logadress='./logs/%s/'%today
    try:
        os.mkdir(logadress)
    except (FileExistsError,FileNotFoundError) as e:
        print(e)
    # create logger with 'spam_application'
    logger = logging.getLogger('RecoBot')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('%sRecoBotlog.log'%(logadress))
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger



def get_user_cache(userid, key):
    global logPath
    with open(logPath, "rt", encoding='utf-8') as log:
        reader = csv.DictReader(log)
        for row in reader:
            if row['userID'] == userid:
                return row[key]


def write_user_cache(userid, key, value):
    global logPath,fieldnames
    csvdict = csv.DictReader(open(logPath, 'rt', encoding='utf-8', newline=''))
    dictrow = []
    for row in csvdict:
        if row['userID'] == userid:
            row[key] = value
        # rowcache.update(row)
        dictrow.append(row)

    with open(logPath, "w+", encoding='utf-8', newline='') as lloo:
        # lloo.write(new_a_buf.getvalue())
        wrier = csv.DictWriter(lloo, fieldnames)
        wrier.writeheader()
        for wowow in dictrow:
            wrier.writerow(wowow)


def saveFile(foldername,fileName, tt,client):
    filp='%s.html'%fileName
    with open(filp, 'w', encoding='utf-8') as file:
        file.write(tt)

    summary_id='ED1A0D88BB2A445F%218025'
    fold_id=get_folder_id(client, foldername, summary_id)
    if fold_id is None:
        f = onedrivesdk.Folder()
        i = onedrivesdk.Item()
        i.name = foldername
        i.folder = f
        client.item(drive='me', id=summary_id).children.add(i)
        fold_id = get_folder_id(client, foldername, summary_id)

    client.item(drive='me', id=fold_id).children[filp].upload(filp)
    os.remove(filp)


def get_folder_id(client, foldername, summary_id):
    root_folder = client.item(drive='me', id=summary_id).children.get()
    for fold in root_folder:
        if fold.name == foldername:
            return fold.id
    return None


def convert_star(text):
    stars=''
    try:
        number=int(text)
        for i in range(number):
            stars +='⭐'
        return stars
    except ValueError as e:
        print(e)


def getUserData(fpath,key):
    with open(fpath, 'rt', encoding='utf-8') as myFile:
        reader = csv.DictReader(myFile)
        try:
            for row in reader:
                if row['key'] == key:
                    return deCode(row['username']), deCode(row['password'])
        except Error as e:
            print(e)


def newUserData(fpath, username=None, password=None,key=None):
    if username==None and password==None:
        key = input('Key name:\n')
        username = input('Username:\n')
        password = input('Pass word:\n')
    cusername = enCode(username)
    cpassword = enCode(password)
    with open(fpath, "a+") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([key,cusername,cpassword])

def enCode(code):
    return cp.enCode(code)


def deCode(code):
    return cp.deCode(code)


def get_seat_info():
    html=rq.get('https://seatfinder.bibliothek.kit.edu/karlsruhe/getdata.'
                'php?callback=jQuery21407451994564516051_1559296485007&location%5B0%5D=LSG%2CLSM%2CLST%'
                '2CLSN%2CLSW%2CLBS%2CBIB-N%2CFBC%2CFBP%2CLAF%2CFBA%2CFBI%2CFBM%2CFBW%2CFBH%2CFBD%2CTheaBib%2CBLB%2CWIS&values'
                '%5B0%5D=seatestimate%2Cmanualcount&after%5B0%5D=-10800seconds&before%5B0%5D=now&limit%5B0%5D=-17&location%5'
                'B1%5D=LSG%2CLSM%2CLST%2CLSN%2CLSW%2CLBS%2CBIB-N%2CFBC%2CFBP%2CLAF%2CFBA%2CFBI%2CFBM%2CFBW%2CFBH%2CFBD%2CTheaBib%2CBLB%2C'
                'WIS&values%5B1%5D=location&after%5B1%5D=&before%5B1%5D=now&limit%5B1%5D=1&refresh=&_=1559296485011')

    stage_tag={'LSG':'3rd floor new','LSM':'3rd floor old','LST':'2nd floor new','LSN':'2nd floor old','LSW':'1st floor new','LBS':'1st floor old'}
    infodict={}
    total=0
    tfree=0

    for stage in stage_tag:
        pattern = r'name":"%s","occ.*?{"timestamp":'%stage
        seatinfo=re.findall(pattern,html.text)
        if len(seatinfo) >0:
            occupied=re.findall(r'"occupied_seats".*?,',seatinfo[0])[0]
            onumber=re.findall(r'[0-9]{1,2}',occupied)[0]
            total+=int(onumber)
            free=re.findall(r'"free_seats".*?}',seatinfo[0])[0]
            fnumber=re.findall(r'[0-9]{1,2}',free)[0]
            total+=int(fnumber)
            tfree+=int(fnumber)
            percent=int(int(fnumber)*100/(int(fnumber)+int(onumber)))
            infodict[stage_tag[stage]]=str(percent)+'%'
        else:
            infodict[stage_tag[stage]]='No info'


    result='Available seats in library:\n'
    for text in infodict:
        result+='%s: %s.\n'%(text,infodict[text])
    result+='Total available seats: %s'%(str(int(tfree*100/total))+'%')
    return result


def get_yesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    return yesterday

# path = 'D:\Workspace_Pycharm/loginData.csv'
# newUserData(path)
