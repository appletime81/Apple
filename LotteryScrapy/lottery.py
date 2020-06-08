from bs4 import BeautifulSoup
import requests
#001
head_Html_lotto='https://www.pilio.idv.tw/ltobig/list.asp'
res = requests.get(head_Html_lotto, timeout=30)
print(res.text)