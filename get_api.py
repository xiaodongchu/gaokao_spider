import math
import os
from time import sleep, time
import requests
from urllib.parse import urlencode
from my_json import load_json, save_json
from spider_url import head
import hashlib
import hmac
import base64
import urllib.parse

download_limit = 2.5
next_time = time()
retry = 500


def signsafe(url):
    sign = b"D23ABC@#56"
    url = str(url)
    url = url.lstrip('/').replace('https://', '').replace('http://', '')
    url = urllib.parse.unquote(url)
    # 生成 HMAC-SHA1 签名
    signature = hmac.new(sign, url.encode('utf-8'), hashlib.sha1).digest()
    # 将签名进行 Base64 编码
    sign_b64 = base64.b64encode(signature).decode('utf-8')
    # 计算 MD5 哈希值
    hash_md5 = hashlib.md5(sign_b64.encode('utf-8')).hexdigest()
    return hash_md5


def get_paged_api_data(file_path, url, url_params, proxy=None):
    if os.path.exists(file_path):
        j = load_json(file_path)
        if j["code"] == "1069":
            os.remove(file_path)
        else:
            print(file_path.split('/')[-1] + "exist")
            return load_json(file_path)
    time_now = time()
    global next_time
    sleep(max(0, int(next_time - time_now)))
    next_time = time_now + download_limit
    url1 = url + "?" + urlencode(url_params)
    url_params["signsafe"] = signsafe(url1)
    response = None
    try:
        response = get_response(url, url_params, proxy)
        res_d = response.json()
    except Exception as e:
        print("Error" + str(e) + str(url_params))
        res_d = {"code": "1069"}
    max_retry = retry
    while (res_d["code"] == "1069" or not response or response.status_code != 200) and max_retry > 0:
        max_retry -= 1
        if response.status_code == 404:
            return {"data": {"numFound": 0, "item": []}}
        print("download error ", response.status_code)
        sleep(6000)
        try:
            response = get_response(url, url_params, proxy)
            res_d = response.json()
        except Exception as e:
            print("Error" + str(e) + str(url_params))
            res_d = {"code": "1069"}
        if max_retry - retry == 2 and proxy:
            proxy = get_proxy()
    if max_retry == 0:
        raise ValueError("download error: " + str(response.status_code))
    save_json(file_path, res_d)
    print("downloaded " + file_path.split("/")[-1] + " finish")
    return res_d


def get_api_data(file_path, url, url_params, add_dict={}, proxy=None):
    try:
        file_path_page = file_path.split('.')[0] + "_{}.json"
        url_params["page"] = 1
        page_n = get_paged_api_data(
            file_path_page.format(url_params["page"]),
            url,
            url_params,
            proxy
        )
        numFound = page_n["data"]["numFound"]
        special_plan = page_n["data"]["item"]
        for i_page in range(2, math.ceil(numFound / 10) + 1):
            url_params["page"] = i_page
            page_n = get_paged_api_data(
                file_path_page.format(i_page),
                url,
                url_params,
                proxy
            )
            special_plan.extend(page_n["data"]["item"])
        for i in special_plan:
            i.update(add_dict)
        return special_plan
    except Exception as e:
        print("Error" + str(e) + str(url_params))


def get_proxy():
    proxy = requests.get("http://127.0.0.1:5010/get/?type=https").json().get("proxy")
    return proxy


def delete_proxy(proxy):
    if "http://" in proxy:
        proxy = proxy.split("http://")[-1]
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def get_response(url, url_params, proxy=None):
    if not proxy:
        response = requests.post(
            url=url,
            params=url_params,
            headers=head
        )
    else:
        response = requests.post(
            url=url,
            params=url_params,
            headers=head,
            proxies=proxy
        )
    return response