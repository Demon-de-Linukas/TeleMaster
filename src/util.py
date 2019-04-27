import os
import logging
import time
import csv
import onedrivesdk


import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from TeleMaster.src import cypter as cp
from csv import Error

logPath = 'cache.csv'
fieldnames = ['userID','status','today','week','starTD','starWK','commentTD','commentWK']
path_of_logindata = 'D:\Workspace_Pycharm/loginData.csv'


def login(username, password,headless,linux):
    options = Options()
    options.add_argument('window-size=1200x600')
    options.add_argument('--lang=zh-CN')
    options.add_argument('--dns-prefetch-disable')
    if headless:
        options.add_argument('headless')
    if linux:
        browser = webdriver.Chrome(chrome_options=options, executable_path='/usr/lib/chromium-browser/chromedriver')
    else:
        browser = webdriver.Chrome(chrome_options=options, executable_path='D:\Apps\Chromedriver\chromedriver_win32/chromedriver.exe')
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
    days=driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[1]/div[1]/a/span')
    if '本周' not in days.text:
        days.click()
        driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[1]/div[1]/ul/li[3]/a').click()
        time.sleep(1)
    driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[1]/a').click()
    driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[1]/ul/li[3]').click()
    suma=driver.find_element_by_xpath('//*[@id="summary-text"]')
    ttt = suma.get_property('value')
    return ttt

def get_today(driver):
    driver.get('https://www.ticktick.com/#q/all/summary')
    time.sleep(5)
    days=driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[1]/div[1]/a/span')
    if days.text!='今天':
        days.click()
        driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[1]/div[1]/ul/li[1]/a').click()
        time.sleep(1)
    driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[2]/a').click()
    list=driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[2]/div/div[3]/div[1]/div[1]')
    #Check the shown property
    attrib_list=['detail','progress','list']
    for attrib in attrib_list:
        element = list.find_elements_by_css_selector("[data-key ='%s']"%attrib)
        if 'selected-item' not in element[0].get_attribute('class'):
            element[0].click()
    driver.find_element_by_xpath('//*[@id="summary-detail-control-confirm"]').click()

    driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[1]/a').click()
    driver.find_element_by_xpath('//*[@id="summary-view"]/div/div/div[1]/div/div[2]/div[1]/ul/li[1]').click()

    suma=driver.find_element_by_xpath('//*[@id="summary-text"]')
    ttt = suma.get_property('value')
    return ttt


def initlog():
    today = datetime.date.today()
    logadress='logs/%s/'%today
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

# path = 'D:\Workspace_Pycharm/loginData.csv'
# newUserData(path)
