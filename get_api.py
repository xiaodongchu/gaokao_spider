import math
import os
from time import sleep, time
from random import random
import requests
from urllib.parse import urlencode
from my_json import load_json, save_json
from spider_url import head
import hashlib
import hmac
import base64
import urllib.parse

download_limit = 3
retry = 500
proxy_set = set()


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


def get_paged_api_data(file_path, url, url_params, next_time, proxy=None):
    if os.path.exists(file_path):
        j = load_json(file_path)
        if j["code"] == "1069":
            os.remove(file_path)
        else:
            print(file_path.split('/')[-1] + "exist")
            return {
                "data": load_json(file_path),
                "proxy": proxy,
                "next_time": next_time
            }
    time_now = time()
    sleep(max(0, int(next_time - time_now)))
    next_time = time_now + download_limit + random() * 4
    url1 = url + "?" + urlencode(url_params)
    url_params["signsafe"] = signsafe(url1)
    try:
        response = get_response(url, url_params, proxy)
        res_d = response.json()
    except Exception as e:
        print(e)
        response = None
        res_d = {"code": "1069"}
    max_retry = retry
    while (res_d["code"] == "1069" or not response or response.status_code != 200) and max_retry > 0:
        max_retry -= 1
        if response and response.status_code == 404:
            return {
                "data": {"data": {"numFound": 0, "item": []}},
                "proxy": proxy,
                "next_time": next_time
            }
        if proxy:
            delete_proxy(proxy)
            proxy = get_proxy()
        else:
            return {"error": 1}
        try:
            response = get_response(url, url_params, proxy)
            res_d = response.json()
        except Exception as e:
            print(e)
            res_d = {"code": "1069"}
    if max_retry == 0:
        return {"error": 1}
    save_json(file_path, res_d)
    print("downloaded " + file_path.split("/")[-1] + " finish")
    return {
        "data": res_d,
        "proxy": proxy,
        "next_time": next_time
    }


def get_api_data(file_path, url, url_params, add_dict={}, proxy=None):
    try:
        file_path_page = file_path.split('.')[0] + "_{}.json"
        url_params["page"] = 1
        page_n = get_paged_api_data(
            file_path_page.format(url_params["page"]),
            url,
            url_params,
            0,
            proxy
        )
        if "error" in page_n:
            return None
        proxy = page_n["proxy"]
        next_time = page_n["next_time"]
        page_n = page_n["data"]["data"]
        numFound = page_n["numFound"]
        special_plan = page_n["item"]
        for i_page in range(2, math.ceil(numFound / 10) + 1):
            url_params["page"] = i_page
            page_n = get_paged_api_data(
                file_path_page.format(i_page),
                url,
                url_params,
                next_time,
                proxy
            )
            if "error" in page_n:
                return None
            proxy = page_n["proxy"]
            next_time = page_n["next_time"]
            page_n = page_n["data"]["data"]
            special_plan.extend(page_n["item"])
        for i in special_plan:
            i.update(add_dict)
        return {
            "data": special_plan,
            "proxy": proxy,
        }
    except Exception as e:
        print(e)
        return None


def get_proxy():
    try:
        proxy = requests.get("http://127.0.0.1:5010/get/?type=https").json().get("proxy")
        while proxy in proxy_set:
            sleep(random())
            proxy = requests.get("http://127.0.0.1:5010/get/?type=https").json().get("proxy")
        proxy_set.add(proxy)
        print(proxy)
    except:
        sleep(random() * 10)
        return get_proxy()
    return proxy


def delete_proxy(proxy):
    try:
        if "http://" in proxy:
            proxy = proxy.split("http://")[-1]
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
    except:
        pass


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
            proxies={
                "http": "http://" + proxy,
                "https": "http://" + proxy
            }
        )
    return response
