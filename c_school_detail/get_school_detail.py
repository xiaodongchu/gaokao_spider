from my_json import download_json, bulid_download_path
from my_mongo import client, school_id
from spider_url import school_json_url, school_detail_json_url

download_path = bulid_download_path("school_detail")


def init():
    db = client.gaokao.school
    school_dict = download_json(school_json_url, download_path + "school.json", exist=True)
    school_dict = school_dict["data"]
    url = school_detail_json_url()
    for k, v in school_id.items():
        if db.find_one({"id": k}):
            continue
        school0 = download_json(url.to_string(k), download_path + "school_" + k + ".json", exist=True)
        school0 = school0["data"]
        school0.update(school_dict[k])
        school0["id"] = k
        school0["name"] = v
        db.update_one({"id": k}, {"$set": school0}, upsert=True)


init()
