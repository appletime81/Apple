import requests
from bs4 import BeautifulSoup,NavigableString
import re

def urlvoid():
    url = "https://www.pilio.idv.tw/ltobig/list.asp"
    res = requests.get(url)
    text = res.text

    soup = BeautifulSoup(text,"lxml").find("table",class_="auto-style1")
    all_tr = soup.find_all("tr")
    value = { tr.find_all("td")[0].text :
                tr.find_all("td")[1].text.replace("\xa0","")
                for tr in all_tr}
    print(value)

urlvoid()