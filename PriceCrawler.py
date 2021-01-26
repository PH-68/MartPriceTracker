import asyncio
import base64
import json
import os
import re
import time
import threading

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

root_dict = dict({})
base_url = "https://online.carrefour.com.tw"


def get_item_model(item_model):
    required_keys = ["Id", "Name", "PictureUrl", "SeName", "SpecialPrice", "Price", "PromotionActivityType", "PromotionActivityTypeId"]
    required_item_model = {}
    for i in range(len(required_keys)):
        required_item_model[required_keys[i]] = item_model[required_keys[i]]
    return required_item_model
    # https://stackoverflow.com/questions/11294535/verify-if-a-string-is-json-in-python
    # 把需要的Key抓出來


def is_json(json_data):
    try:
        json.loads(json_data)
    except:
        return False
    return True


def get_and_add_item(categoryId, menu_object, i, v, n, str_first_class, str_second_class, str_third_class):
    # 爬取並加入dict
    print(str_third_class)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4386.0 Safari/537.36 Edg/89.0.767.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = "categoryId=" + categoryId + "&orderBy=21&pageIndex=1&pageSize=1000"
    # 進去class之後拿categoryId爬API
    while True:
        # 錯誤處理 如果不是json就一直重爬
        response = requests.request("POST", base_url+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
        if is_json(response.text):
            item_object = json.loads(response.text)
            # 如果品項大於1000的話就去爬第二頁
            if int(item_object["content"]["Count"]) > 1000:
                payload = "categoryId=" + str(menu_object["content"][i]["SubCategories"][v]["SubCategories"][n]["Id"]) + "&orderBy=21&pageIndex=2&pageSize=1000"
                response_1 = requests.request("POST", base_url+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
                item_object_1 = json.loads(response_1.text)
                for item in item_object_1["content"]["ProductListModel"]:
                    item_object["content"]["ProductListModel"].append(item)
                    # 合併item_object 跟 item_object_1
            break
    for item_list in item_object["content"]["ProductListModel"]:
        root_dict[str_first_class][str_second_class][str_third_class].append(get_item_model(item_list))
        # 最後加入主root_dict


def main():
    payload = "langId=1&langCode=zh-tw"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4386.0 Safari/537.36 Edg/89.0.767.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    menu_object = json.loads(requests.request("POST", base_url+"/ProductShowcase/Catalog/GetMenuJson", headers=headers, data=payload).text)
    for i in range(len(menu_object["content"])):
        str_first_class = menu_object["content"][i]["Name"]
        root_dict[str_first_class] = dict({})
        # 第一類
        for v in range(len(menu_object["content"][i]["SubCategories"])):
            str_second_class = menu_object["content"][i]["SubCategories"][v]["Name"]
            root_dict[str_first_class][str_second_class] = dict({})
            # 第二類
            for n in range(len(menu_object["content"][i]["SubCategories"][v]["SubCategories"])):
                str_third_class = menu_object["content"][i]["SubCategories"][v]["SubCategories"][n]["Name"]
                root_dict[str_first_class][str_second_class][str_third_class] = []
                # 第三類
                t = threading.Thread(target=get_and_add_item, args=(str(menu_object["content"][i]["SubCategories"][v]["SubCategories"][n]["Id"]), menu_object, i,
                                                                    v, n, str_first_class, str_second_class, str_third_class,))
                # 建立執行緒
                t.start()

    # 最後上傳github
    url = "https://api.github.com/repos/ph-68/MartPriceTracker/contents/"+str(int(time.time()))+".json"

    # Serialize dict to json
    payload = "{\"message\":\"File uploaded from python in AWS Lambda!\",\"content\":\""+str(base64.b64encode((json.dumps(root_dict).encode("utf-8")))).replace("b'", "").replace("'", "")+"\",\"branch\":\"data\"}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'Basic '+os.environ["MartPriceTracker_Github_Token"],
        'Content-Type': 'text/plain'
    }
    response = requests.request("PUT", url, headers=headers, data=payload)
    print(response)
    return response.status_code
# 最後上傳github https://docs.github.com/en/rest/reference/repos#create-or-update-file-contents 檔名用unix time


if __name__ == "__main__":
    main()
