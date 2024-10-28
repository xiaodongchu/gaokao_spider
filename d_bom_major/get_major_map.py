from my_json import download_json, bulid_download_path
from my_mongo import client
from spider_url import bom_major_map_url

download_path = bulid_download_path("major")


def init():
    url = bom_major_map_url()
    db = client.gaokao.major
    map0 = download_json(url.url_1, download_path + "bom_major_map_1.json", True)
    for map0i in map0["msg"]:
        code0 = map0i["key"]
        name0 = map0i["name"]
        map1 = download_json(url.url0_to_string(map0i["key"]),
                             download_path + "bom_major_map0_" + map0i["key"] + ".json", True)
        for map1i in map1["msg"]:
            code1 = map1i["key"]
            name1 = map1i["name"]
            map2 = download_json(url.url1_to_string(map1i["key"]),
                                 download_path + "bom_major_map1_" + map1i["key"] + ".json", True)
            for map2i in map2["msg"]:
                code2 = map2i["key"]
                name2 = map2i["name"]
                map3 = download_json(url.url2_to_string(map2i["key"]),
                                     download_path + "bom_major_map2_" + map2i["key"] + ".json", True)
                for map3i in map3["msg"]:
                    code = map3i["zydm"]
                    if db.find_one({"code_bom": code}):
                        continue
                    map4 = download_json(url.url3_to_string(map3i["specId"]),
                                         download_path + "bom_major_map3_" + map3i["zydm"] + ".json", True)
                    map4 = map4["msg"]
                    map4["code0"] = code0
                    map4["code1"] = code1
                    map4["code2"] = code2
                    map4["name0"] = name0
                    map4["name1"] = name1
                    map4["name2"] = name2
                    # 标记完成
                    map4["code_bom"] = code
                    # 去重
                    map4['code'] = code
                    db.update_one({"code": code}, {"$set": map4}, upsert=True)
                    print(code)


init()
