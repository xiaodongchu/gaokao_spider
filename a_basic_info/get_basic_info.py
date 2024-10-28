from my_json import bulid_download_path, download_json
from my_mongo import client
from spider_url import id_json_url, map_id_url

download_path = bulid_download_path("basic")
db = client.gaokao


def init_special_and_school():
    j = download_json(id_json_url, download_path + "special_school_id.json")
    special = []
    for i in j["data"]["special"]:
        special.append({"id": i["id"], "name": i["name"]})
    db.special_id.drop()
    db.special_id.insert_many(special)
    school = []
    for i in j["data"]["school"]:
        school.append({"id": i["school_id"], "name": i["name"]})
    db.school_id.drop()
    db.school_id.insert_many(school)


def init_province():
    province_dict = {
        "11": "北京",
        "12": "天津",
        "13": "河北",
        "14": "山西",
        "15": "内蒙古",
        "21": "辽宁",
        "22": "吉林",
        "23": "黑龙江",
        "31": "上海",
        "32": "江苏",
        "33": "浙江",
        "34": "安徽",
        "35": "福建",
        "36": "江西",
        "37": "山东",
        "41": "河南",
        "42": "湖北",
        "43": "湖南",
        "44": "广东",
        "45": "广西",
        "46": "海南",
        "50": "重庆",
        "51": "四川",
        "52": "贵州",
        "53": "云南",
        "54": "西藏",
        "61": "陕西",
        "62": "甘肃",
        "63": "青海",
        "64": "宁夏",
        "65": "新疆"
    }
    db.province_id.drop()
    province_list = [{"id": k, "name": v} for k, v in province_dict.items()]
    db.province_id.insert_many(province_list)


def get_other_id():
    j = download_json(map_id_url, download_path + "dicname2id.json")

    db.pici_batch_id.drop()
    batch_id = j["data"]["batch"]
    batch_id = [{"id": v, "name": k} for k, v in batch_id.items()]
    db.pici_batch_id.insert_many(batch_id)

    db.xuanke_type_id.drop()
    type_id = j["data"]["type"]
    type_id = [{"id": v, "name": k} for k, v in type_id.items()]
    db.xuanke_type_id.insert_many(type_id)

    db.zhaosheng_zslx_id.drop()
    zslx_id = j["data"]["zslx"]
    zslx_id = [{"id": v, "name": k} for k, v in zslx_id.items()]
    db.zhaosheng_zslx_id.insert_many(zslx_id)


if __name__ == "__main__":
    init_special_and_school()
    init_province()
    get_other_id()
