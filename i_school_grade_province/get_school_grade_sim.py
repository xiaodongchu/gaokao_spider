import sys
sys.path.append('..')

from concurrent.futures import ThreadPoolExecutor

from my_json import download_json, bulid_download_path
from spider_url import school_province_grade_url, years
from my_mongo import client, province_id, school_id

download_path = bulid_download_path("school_grade_sim")


# from pymongo import ASCENDING
# db = client.gaokao.school_grade_sim
# db.create_index(
#     [
#         ("school_id", ASCENDING),
#         ("province_id", ASCENDING),
#         ("year", ASCENDING),
#         ("type_id", ASCENDING),
#         ("batch_id", ASCENDING)
#     ]
# )


def init():
    pool = ThreadPoolExecutor(16)
    sl = list(school_id.keys())
    sl.sort()
    pl = list(province_id.keys())
    pl.sort(reverse=True)
    for province1 in pl:
        for school1 in sl:
            pool.submit(school_province, school1, province1)
            # school_province(school1, province1)
    pool.shutdown()


def school_province(school1, province1):
    url = school_province_grade_url()
    db = client.gaokao.school_grade_sim
    l = []
    for year in years:
        year = str(year)
        d = {
            "school_id": school1,
            "province_id": province1,
            "year": year,
        }
        if db.find_one(d):
            continue
        try:
            file_path = download_path + "school_grade_province_" + school1 + "_" + province1 + "_" + year + ".json"
            school0 = download_json(url.to_string_before_2022(school1, province1, year), file_path, exist=True)
            if not school0:
                l.append(d)
                continue
            school0 = school0["data"]
            for k1, v1 in school0.items():
                d1 = v1["item"]
                for i in d1:
                    i.update(d)
                l.extend(d1)
        except Exception as e:
            print(str(e) + province1 + school1 + year)
            continue
    if l:
        db.insert_many(l)
        print("inserted " + school1 + province1)


init()
