from my_json import download_json, bulid_download_path
from my_mongo import client,get_id_dict
from spider_url import major_detail_json_url

download_path = bulid_download_path("major")
special_id = get_id_dict("special_id")


def init():
    url = major_detail_json_url()
    db = client.gaokao.major
    for k, v in special_id.items():
        if db.find_one({"zs_id": k}):
            continue
        major0 = download_json(url.to_string(k), download_path + "special_" + str(k) + ".json", exist=True)
        major0 = major0["data"]
        if 'id' in major0:
            major0.pop('id')
        major0['name'] = v
        # 标记完成
        major0['zs_id'] = k
        # 去重
        code = major0['code']
        db.update_one({"code": code}, {"$set": major0}, upsert=True)


init()
