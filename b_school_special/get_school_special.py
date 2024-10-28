from my_json import download_json, bulid_download_path
from my_mongo import client, school_id
from spider_url import school_special_json_url

download_path = bulid_download_path("school_special")


def init():
    url = school_special_json_url()
    db = client.gaokao.school_special
    for k, v in school_id.items():
        if db.find_one({"school_id": k}):
            continue
        try:
            school0 = download_json(url.to_string(k), download_path + "school_" + k + ".json", exist=True)
            if '1' in school0["data"]['special_detail']:
                school0 = school0["data"]['special_detail']['1']
                for i in school0:
                    i["school_name"] = v
                    special_id = i["special_id"]
                    db.update_one({"special_id": special_id, "school_id": k}, {"$set": i}, upsert=True)
            else:
                print("school special error: " + k)
        except ValueError or KeyError:
            print("school special error: " + k)
            continue


init()
