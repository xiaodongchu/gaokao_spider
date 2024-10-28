from my_json import download_json, bulid_download_path
from my_mongo import school_id, client
from spider_url import school_job_json_url

download_path = bulid_download_path("school_job_score")


def init():
    url = school_job_json_url()
    db = client.gaokao.school
    for k, v in school_id.items():
        if db.find_one({"id": k, "job": {"$exists": True}}):
            continue
        try:
            school0 = download_json(url.to_string(k), download_path + "school_job_" + k + ".json", exist=True)
            school0 = school0["data"]
            db.update_one({"id": k}, {"$set": {"job": school0}}, upsert=True)
        except ValueError:
            print("school job error: " + k)
            continue


init()
