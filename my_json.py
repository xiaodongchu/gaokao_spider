import json
import os
from time import sleep, time

import requests

from spider_url import head

download_limit = 0.5
next_download_time = 0

base_path = os.path.dirname(__file__)
temp_path = os.path.join(base_path, "temp")


def load_json(file_path):
    f = open(file_path, 'r', encoding='utf-8')
    j = json.load(f)
    f.close()
    return j


def save_json(file_path, j: dict):
    f = open(file_path, 'w', encoding='utf-8')
    json.dump(j, f, ensure_ascii=False, indent=4)
    f.close()


def download_json(url, file_path, exist=False, only_exist=False):
    if (only_exist or exist) and os.path.exists(file_path):
        return load_json(file_path)
    if only_exist:
        return {}
    global next_download_time
    if next_download_time - time() > 0:
        sleep(min(next_download_time - time(), download_limit))
    j = requests.get(url, headers=head)
    if j.status_code == 404:
        return {}
    next_download_time = time() + download_limit
    max_retry = 3
    while j.status_code == 429:
        print("download error 429")
        sleep(5)
        j = requests.get(url, headers=head)
    while j.status_code == 418 or j.status_code == 403 and max_retry > 0:
        print("download error 403")
        sleep(5)
        max_retry -= 1
        j = requests.get(url, headers=head)
    if j.status_code != 200:
        raise ValueError(str(j.status_code))
    j = j.content
    j = json.loads(j)
    save_json(file_path, j)
    print("downloaded " + file_path.split("/")[-1] + " finish")
    return j


def bulid_download_path(extra):
    download_path = os.path.join(temp_path, extra)
    if not os.path.exists(download_path):
        os.makedirs(download_path, exist_ok=True)
    download_path = str(download_path)
    if download_path[-1] != "/":
        download_path += "/"
    return download_path


def clean_dict(d):
    # 使用字典推导式递归处理字典项
    return {k: clean_dict(v) if isinstance(v, dict) else v
            for k, v in d.items() if v or (isinstance(v, dict) and clean_dict(v))}