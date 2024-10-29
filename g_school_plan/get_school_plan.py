import os

from get_api import get_api_data, get_proxy, proxy_set
from my_json import download_json, bulid_download_path, clean_dict
from my_mongo import client, school_id, get_id_dict, province_id
from spider_url import school_plan_url

download_path = bulid_download_path("school_plan")
batch_id = get_id_dict("pici_batch_id")
type_id = get_id_dict("xuanke_type_id")
zslx_id = get_id_dict("zhaosheng_zslx_id")
url = school_plan_url()
db = client.gaokao.school_plan_sim


# from pymongo import ASCENDING, DESCENDING
# db = client.gaokao.school_plan_sim
# print(list(db.list_indexes()))
# db.create_index(
#     [
#         ("year", DESCENDING),
#         ("province_id", ASCENDING),
#         ("school_id", ASCENDING),
#         ("min_section", ASCENDING),
#         ("type_id", ASCENDING),
#         ("batch_id", ASCENDING),
#     ]
# )


def get_year(school1):
    file_name = download_path + "school_plan_mata" + school1 + ".json"
    school0 = download_json(url.mata_to_string(school1), file_name, exist=True)
    school0 = school0["data"]["newsdata"]["groups"]
    school_list = []
    for k1, v1 in school0.items():
        k = k1.split("_")
        school_list.append({
            "school_id": str(school1),
            "province_id": str(k[0]),
            "year": str(k[1]),
            "type_id": str(k[2]),
            "batch_id": str(k[3]),
            "finish_plan": 1,
        })
    return school_list


def init_before_2023(school1):
    print(school1)
    # file_name = download_path + "school_plan_mata" + school1 + ".json"
    # school0 = download_json(url.mata_to_string(school1), file_name, exist=True)
    # school0 = school0["data"]["newsdata"]["year"]
    # for province1, years in school0.items():
    #     school_plan_2023(school1, province1, years)
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023]
    for province1 in province_id.keys():
        school_plan_2023(school1, province1, years)


def school_plan_2023(school1, province1, years):
    for year in years:
        if year > 2023:
            continue
        year = str(year)
        temp_dict = {
            "school_id": str(school1),
            "province_id": str(province1),
            "year": str(year),
            "province": province_id[province1],
            "finish_plan": 1,
        }
        if db.find_one(temp_dict):
            continue
        try:
            file_name = download_path + "school_plan_" + province1 + "_" + school1 + "_" + str(year) + ".json"
            school0 = download_json(url.to_string_before_2023(school1, province1, year), file_name, exist=True,
                                    only_exist=True)
            if not school0:
                continue
            if school0['code'] != "0000":
                print(school0)
                os.remove(file_name)
                continue
            school0 = school0["data"]
            for k1, v1 in school0.items():
                v2 = v1['item']
                for v3 in v2:
                    v3.update(temp_dict)
                    try:
                        v3["type_id"] = str(v3["type"])
                        del v3["type"]
                        v3["batch_id"] = str(v3["batch"])
                        del v3["batch"]
                        v3["special_id"] = str(v3["special_id"])
                        d1 = clean_dict(v3)
                        d = {
                            "school_id": school1,
                            "province_id": province1,
                            "year": year,
                            "special_id": v3["special_id"],
                            "type_id": v3["type_id"],
                            "batch_id": v3["batch_id"],
                        }
                        db.update_one(d, {"$set": d1}, upsert=True)
                    except:
                        continue
        except Exception as e:
            print(str(e) + province1 + school1 + year)
            continue


def get_school_plan(school1):
    try:
        proxy = get_proxy()
        print(school1)
        years = get_year(school1)
        for i in years:
            if int(i["year"]) < 2024 or db.find_one(i):
                continue
            file_name = download_path + "school_plan_" + school1 + "_" + i["province_id"] + "_" + i["year"] + "_" + i[
                "type_id"] + "_" + i["batch_id"] + ".json"
            params = url.get_params(i["school_id"], i["province_id"], i["year"], i["type_id"], i["batch_id"])
            school0 = get_api_data(file_name, url.url, params, i, proxy)
            if not school0:
                continue
            proxy = school0["proxy"]
            school0 = school0["data"]
            for j in school0:
                if "special_id" not in j:
                    if "spcode" in j:
                        j["special_id"] = str(j["spcode"])
                    else:
                        j["special_id"] = str(j["spname"])
                d = {
                    "school_id": school1,
                    "province_id": i["province_id"],
                    "year": i["year"],
                    "special_id": j["special_id"],
                    "type_id": i["type_id"],
                    "batch_id": i["batch_id"],
                }
                d1 = clean_dict(j)
                db.update_one(d, {"$set": d1}, upsert=True)
            print("inserted " + str(i))
        proxy_set.remove(proxy)
        print("remove " + proxy)
    except Exception as e:
        print(e)


def run_in_pool():
    # from concurrent.futures import ThreadPoolExecutor
    # pool = ThreadPoolExecutor(4)
    db_school = client.gaokao.school
    for school1 in school_id.keys():
        # pool.submit(init_before_2023, school1)
        school2 = db_school.find_one({"school_id": school1})
        if not school2 or not school2.get("f985", 0) == '1':
            continue
        print(school1 + school2['name'])
        get_school_plan(school1)
        # pool.submit(get_school_plan, school1)


if __name__ == "__main__":
    run_in_pool()
