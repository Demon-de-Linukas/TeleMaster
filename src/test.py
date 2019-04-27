import time
from TeleMaster.src import util as ut
path = ut.path_of_logindata

username, password=ut.getUserData(path,'tick')

driver = ut.login(username, password, headless=False, linux=False)
time.sleep(8)
ut.get_today(driver)
ut.get_week(driver)