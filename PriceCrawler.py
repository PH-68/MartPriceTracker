import requests
from bs4 import BeautifulSoup
import threading



baseUrl = "https://online.carrefour.com.tw/tw/"
r = requests.get(baseUrl)
soup = BeautifulSoup((r.text), "html.parser")
for i in soup.select("body > section > div.index-show.clearfix.commodities-list > div.detailed-class.hidden-xs.fleft > ul > li > div > div > div > a > span"):
    print(i.contents[0]+ "  " + baseUrl + i.parent.attrs["href"])
    r = requests.get(baseUrl + i.parent.attrs["href"])
    

    
