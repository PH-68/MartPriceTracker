import requests
from bs4 import BeautifulSoup
import threading
import json
import re
from requests.adapters import HTTPAdapter
import os



root_dict = dict({})
base_url = "https://online.carrefour.com.tw"


def get_item_model(item_model):
    required_keys = ["Id", "Name", "PictureUrl", "SeName", "SpecialPrice", "Price", "PromotionActivityType", "PromotionActivityTypeId"]
    required_item_model = {}
    for i in range(len(required_keys)):
        required_item_model[required_keys[i]] = item_model[required_keys[i]]
    return required_item_model
    # https://stackoverflow.com/questions/11294535/verify-if-a-string-is-json-in-python


def is_json(json_data):
    try:
        json.loads(json_data)
    except:
        return False
    return True


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

        for v in range(len(menu_object["content"][i]["SubCategories"])):
            str_second_class = menu_object["content"][i]["SubCategories"][v]["Name"]
            root_dict[str_first_class][str_second_class] = dict({})

            for n in range(len(menu_object["content"][i]["SubCategories"][v]["SubCategories"])):
                str_third_class = menu_object["content"][i]["SubCategories"][v]["SubCategories"][n]["Name"]
                root_dict[str_first_class][str_second_class][str_third_class] = []

                print(str_third_class)
                payload = "categoryId=" + str(menu_object["content"][i]["SubCategories"][v]["SubCategories"][n]["Id"]) + "&orderBy=21&pageIndex=1&pageSize=1000"
                # 進去class之後拿categoryId爬API
                while True:
                    response = requests.request("POST", base_url+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
                    if is_json(response.text):
                        item_object = json.loads(response.text)
                        item_object_1 = None
                        if int(item_object["content"]["Count"]) > 1000:
                            payload = "categoryId=" + str(menu_object["content"][i]["SubCategories"][v]["SubCategories"][n]["Id"]) + "&orderBy=21&pageIndex=2&pageSize=1000"
                            response_1 = requests.request("POST", base_url+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
                            item_object_1 = json.loads(response_1.text)
                            for item in item_object_1["content"]["ProductListModel"]:
                                item_object["content"]["ProductListModel"].append(item)
                        break
                for item_list in item_object["content"]["ProductListModel"]:
                    root_dict[str_first_class][str_second_class][str_third_class].append(get_item_model(item_list))

   

    json.dumps(root_dict)
# Serialize dict to json
# Todo:最後上傳github https://docs.github.com/en/rest/reference/repos#create-or-update-file-contents 檔名用unix time


if __name__ == "__main__":
    main()

def old_func():
     # Todo 改成async不然我要等到瘋掉了
    r = requests.get(base_url+"/tw")
    soup = BeautifulSoup((r.text), "html.parser")
    # 首頁爬進去找class
    for i in soup.select("body > section > div.index-show.clearfix.commodities-list > div.detailed-class.hidden-xs.fleft > ul > li > div > div > div > a > span"):
        print(i.contents[0] + "  " + base_url + i.parent.attrs["href"])
      # 爬到class裡面(為了拿categoryId跟分類名)
        r = requests.get(base_url + i.parent.attrs["href"])
        soup = BeautifulSoup((r.text), "html.parser")
      # 因為categoryId在script裡面 這裡是爬進去script https://stackoverflow.com/questions/27040823/beautifulsoup-get-url-from-javascript-variable
        for individual_script in soup.find_all("script", {"src": False}):
            all_value = individual_script.string
            if all_value:
                m = re.compile("var categoryId = (.*)").search(all_value)
                if m != None:
                    print(str(m.group(1)).replace(";\r", ""))

                    payload = "categoryId=" + str(m.group(1)).replace(";\r", "") + "&orderBy=21&pageIndex=1&pageSize=1000"
                    headers = {"Content-Type": "application/x-www-form-urlencoded"}
                # 進去class之後拿categoryId爬API
                    while True:
                        response = requests.request("POST", base_url+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
                        if is_json(response.text):
                            item_object = json.loads(response.text)
                            item_object_1 = None
                            if int(item_object["content"]["Count"]) > 1000:
                                payload = "categoryId=" + str(m.group(1)).replace(";\r", "") + "&orderBy=21&pageIndex=2&pageSize=1000"
                                response_1 = requests.request("POST", base_url+"/ProductShowcase/Catalog/CategoryJson", headers=headers, data=payload)
                                item_object_1 = json.loads(response_1.text)
                        break

                # 拿分類名當dict的key
                    str_first_class = soup.select("#proList > div.category.hidden-xs > div.crumbs > a:nth-child(2)")[0].text.replace("/ ", "").replace(" /", "")
                    str_second_class = soup.select("#proList > div.category.hidden-xs > div.crumbs > a:nth-child(3)")[0].text.replace("/ ", "").replace(" /", "")
                    str_third_class = soup.select("#proList > div.category.hidden-xs > div.crumbs > a:nth-child(4)")[0].text.replace("/ ", "").replace(" /", "")

                # 判斷第一類key是否在裡面
                    if str_first_class in root_dict:
                        if str_second_class in root_dict[str_first_class]:
                            if str_third_class in root_dict[str_first_class][str_second_class]:
                                pass
                            # 不會進到這裡
                            else:
                                root_dict[str_first_class][str_second_class][str_third_class] = []
                            # 第三類有了 最後在指派list進去(因為下面直接用append)
                        else:
                            root_dict[str_first_class][str_second_class] = dict({str_third_class: []})
                        # 有的話用append加入
                        # 第二類有了
                    else:
                        # 全部沒有的話init一個
                        root_dict[str_first_class] = dict({str_second_class: dict({str_third_class: []})})

                    for item_list in item_object["content"]["ProductListModel"]:
                        root_dict[str_first_class][str_second_class][str_third_class].append(get_item_model(item_list))

                    if item_object_1 != None:
                        for item_list in item_object_1["content"]["ProductListModel"]:
                            root_dict[str_first_class][str_second_class][str_third_class].append(get_item_model(item_list))