import time
import datetime
from src import util as ut
#print(datetime.datetime.today().month)
# path = ut.path_of_logindata
# #
# username, password=ut.getUserData(path,'tick')
# #
# driver = ut.login(username, password, headless=False, linux=False)
# time.sleep(8)
# ut.get_today_and_thiswk(driver)
# ut.get_week(driver)
tody='asdasd'
stars='asdasd'
comm='comm'
td_html='''<body>
<div id="wrapper">
    <div>
          <h2></h2>
          <div class="content">
             <div class="title">每日回顾</div>
             <div class="inner_content">{content_td}</div>
          </div>
    </div>
</div>
</body>
</html>'''
content = f'{tody}\n---------\n<b>Stars</b>:\n{stars}\n\n---------\n\n<b>Comment</b>:\n\n{comm}'
content_td=content.replace('\n','<br>')
susu = td_html.format(content_td=content_td)
print(susu)