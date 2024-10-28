import os

import requests

from my_mongo import school_id
from spider_url import school_ico_url, head

basic_path = str(os.path.dirname(__file__)) + "/"
download_ico_path = basic_path + "ico/"
download_pho_path = basic_path + "pho/"


def init_ico():
    url = school_ico_url()
    for k, v in school_id.items():
        file_path = download_ico_path + k + ".jpg"
        if os.path.exists(file_path):
            continue
        try:
            ico = requests.get(url.ico_to_string(k), headers=head)
            if ico.status_code != 200:
                print("download error " + k + " " + str(ico.status_code))
                continue
            with open(download_ico_path + k + ".jpg", 'wb') as f:
                f.write(ico.content)
            print("downloaded " + k + ".jpg" + " finish")
        except ValueError:
            print("school score error: " + k)
            continue


def init_pho():
    url = school_ico_url()
    for k, v in school_id.items():
        file_path = download_pho_path + k + ".jpg"
        if os.path.exists(file_path):
            continue
        try:
            pho = requests.get(url.pho_to_string(k), headers=head)
            if pho.status_code != 200:
                print("download error " + k + " " + str(pho.status_code))
                continue
            with open(download_pho_path + k + ".jpg", 'wb') as f:
                f.write(pho.content)
            print("downloaded " + k + ".jpg" + " finish")
        except ValueError:
            print("school score error: " + k)
            continue


init_pho()
init_ico()
