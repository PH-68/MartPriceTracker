import requests
from bs4 import BeautifulSoup
import threading
import json
import re

root_dict = dict({})
baseUrl = "https://online.carrefour.com.tw"


def get_item_model(item_model):
    required_keys = ["Id", "Name", "PictureUrl", "SeName", "SpecialPrice", "Price", "PromotionActivityType", "PromotionActivityTypeId"]
    required_item_model = {}
    for i in range(len(required_keys)):
        required_item_model[required_keys[i]] = item_model[required_keys[i]]
    return required_item_model


r = requests.get(baseUrl+"/tw")
soup = BeautifulSoup((r.text), "html.parser")
# 首頁爬進去找class
for i in soup.select("body > section > div.index-show.clearfix.commodities-list > div.detailed-class.hidden-xs.fleft > ul > li > div > div > div > a > span"):
    print(i.contents[0] + "  " + baseUrl + i.parent.attrs["href"])
    # 爬到class裡面(為了拿categoryId跟分類名)
    r = requests.get(baseUrl + i.parent.attrs["href"])
    soup = BeautifulSoup((r.text), "html.parser")
    # 因為categoryId在script裡面 這裡是爬進去script https://stackoverflow.com/questions/27040823/beautifulsoup-get-url-from-javascript-variable
    for individual_script in soup.find_all("script", {"src": False}):
        all_value = individual_script.string
        if all_value:
            m = re.compile('var categoryId = (.*)').search(all_value)
            if m != None:
                print(str(m.group(1)).replace(";\r", ""))

                payload = "categoryId=" + \
                    str(m.group(1)).replace(";\r", "") + \
                    "&orderBy=21&pageIndex=1&pageSize=9999999"
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                # 進去class之後拿categoryId爬API
                response = requests.request(
                    "POST", baseUrl+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
                item_object = json.loads(response.text)
                # 拿分類名當dict的key
                str_first_class = soup.select("#proList > div.category.hidden-xs > div.crumbs > a:nth-child(2)")[0].text.replace("/ ", "").replace(" /", "")
                str_second_class = soup.select("#proList > div.category.hidden-xs > div.crumbs > a:nth-child(3)")[0].text.replace("/ ", "").replace(" /", "")
                str_third_class = soup.select("#proList > div.category.hidden-xs > div.crumbs > a:nth-child(4)")[0].text.replace("/ ", "").replace(" /", "")

                # 判斷第一類key是否在裡面
                if str_first_class in root_dict:
                    pass
                   # Todo:判斷第二 第三類是否還在裡面沒有的話init一個 有的話用append加入
                   # 有的話用append加入
                else:
                   # 沒有的話init一個
                    root_dict[str_first_class] = dict({str_second_class: dict({str_third_class: []})})

                    for item_list in item_object["content"]["ProductListModel"]:
                        root_dict[str_first_class][str_second_class][str_third_class].append(get_item_model(item_list))

# Serialize dict to json
json.dumps(root_dict)
# Todo:最後上傳github https://docs.github.com/en/rest/reference/repos#create-or-update-file-contents 檔名用unix time