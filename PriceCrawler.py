import requests
from bs4 import BeautifulSoup
import threading
import json
import re

root_list1 = dict({"d": dict({"rg", "rg"}), "f": dict({"fd", "fd"})})
root_list = dict({})
print(json.dumps(root_list))
baseUrl = "https://online.carrefour.com.tw"

r = requests.get(baseUrl+"/tw")
soup = BeautifulSoup((r.text), "html.parser")
for i in soup.select("body > section > div.index-show.clearfix.commodities-list > div.detailed-class.hidden-xs.fleft > ul > li > div > div > div > a > span"):
    print(i.contents[0] + "  " + baseUrl + i.parent.attrs["href"])
    r = requests.get(baseUrl + i.parent.attrs["href"])
    soup = BeautifulSoup((r.text), "html.parser")
    p = re.compile('var categoryId = (.*)')
    all_script = soup.find_all("script", {"src": False})
    for individual_script in all_script:
        all_value = individual_script.string
        if all_value:
            m = p.search(all_value)
            if m != None:
                print(str(m.group(1)).replace(";\r", ""))

                payload = "categoryId=" + \
                    str(m.group(1)).replace(";\r", "") + \
                    "&orderBy=21&pageIndex=1&pageSize=9999999"
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}

                response = requests.request(
                    "POST", baseUrl+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
                print(response.text)
