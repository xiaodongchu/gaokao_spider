from my_json import download_json, bulid_download_path
from my_mongo import school_id, client
from spider_url import school_score_url

download_path = bulid_download_path("school_job_score")


def init():
    url = school_score_url()
    db = client.gaokao.school
    for k, v in school_id.items():
        if db.find_one({"id": k, "score": {"$exists": True}}):
            continue
        try:
            school0 = download_json(url.to_string(k), download_path + "school_score_" + k + ".json", exist=True)
            school0 = school0["data"]
            db.update_one({"id": k}, {"$set": {"score": school0}}, upsert=True)
        except ValueError:
            print("school score error: " + k)
            continue


init()
