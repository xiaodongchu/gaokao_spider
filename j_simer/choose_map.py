import itertools
import os
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from my_json import load_json
from my_mongo import client, province_id, school_id

basic_path = str(os.path.dirname(__file__)) + "/"
map_path = basic_path + "map_new.json"
map_new = load_json(map_path)
db = client.gaokao.school_special_index
db_plan = client.gaokao.school_plan_sim
db_school = client.gaokao.school
cnt = 0
pool = ThreadPoolExecutor(12)


def get_all_subject_sort():
    order = {"物理": 1, "历史": 2, "化学": 3, "政治": 4, "生物": 5, "地理": 6, "技术": 7}
    subject_chooses = []
    subject_chooses.extend(list(itertools.combinations(order.keys(), 3)))
    subject_chooses_str = {}
    for i in subject_chooses:
        i = list(i)
        i.sort(key=lambda x: order[x])
        subject_chooses_str[''.join(i)] = i
    return subject_chooses_str


subject_chooses = get_all_subject_sort()
subject_choose_copy = {k: 0 for k in subject_chooses.keys()}
subject_choose_any = {k: 1 for k in subject_chooses.keys()}


def subject_sort(subjects):
    order = {"物理": 1, "历史": 2, "化学": 3, "政治": 4, "生物": 5, "地理": 6, "技术": 7}
    if not all(subject in order.keys() for subject in subjects):
        raise ValueError()
    return sorted(subjects, key=lambda x: order.get(x, float('inf')))


def get_map_json():
    data = db_plan.find({"sg_info": {"$exists": True}}, {"sg_info": 1})
    for i in data:
        if i["sg_info"] and i["sg_info"] not in map_new:
            print(i["sg_info"])
            raise ValueError()


def get_map():
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"finish_map": {"$exists": False}},
                    {"finish_map": {"$ne": 1}}
                ],
                "min_section": {"$exists": True, "$regex": "^\\d+$"}
            }
        },
        {
            "$addFields": {
                "min_section_int": {"$toInt": "$min_section"}
            }
        },
        {
            "$match": {
                "min_section_int": {"$exists": True, "$ne": None}
            }
        },
        {
            "$sort": {
                "year": -1  # 按 year 降序排列
            }
        },
        {
            "$group": {
                "_id": {
                    "special_id": "$special_id",
                    "school_id": "$school_id",
                    "province_id": "$province_id",
                },
                "max_section": {"$max": "$min_section_int"},
                "spname": {"$first": "$spname"},
                "sg_info": {"$first": "$sg_info"},
                "type_id": {"$first": "$type_id"},
            }
        },
        {
            "$project": {
                "special_id": "$_id.special_id",
                "school_id": "$_id.school_id",
                "province_id": "$_id.province_id",
                "max_section": 1,
                "spname": 1,
                "sg_info": 1,
                "type_id": 1,
            }
        }
    ]
    result = db_plan.aggregate(pipeline, maxTimeMS=600000)
    for i in result:
        pool.submit(get_map_help, i)


def get_map_help(result_i):
    global cnt
    try:
        min_rank = int(result_i["max_section"])
        if min_rank < 1:
            return
        cnt += 1
        school = db_school.find_one({"school_id": result_i["school_id"]})
        d = {
            "province_name": province_id[result_i["province_id"]],
            "school_name": school_id[result_i["school_id"]],
            "province_id": result_i["province_id"],
            "school_id": result_i["school_id"],
            "min_rank": min_rank,
            "special_name": result_i["spname"],
            "special_id": result_i["special_id"],
            "school_province": school.get("province_id", ""),
            "is_dual_class": school.get("dual_class", 0),
            "is_985": school.get("f_985", 0),
            "is_211": school.get("f_211", 0),
        }
        if result_i["type_id"] == "1":
            d["sk_info"] = "理科"
            d["物理化学生物"] = 1
        elif result_i["type_id"] == "2":
            d["sk_info"] = "文科"
            d["历史政治地理"] = 1
        elif "sg_info" in result_i and result_i["sg_info"] and result_i["sg_info"] in map_new:
            d.update(check_choose(map_new[result_i["sg_info"]]))
        else:
            d.update(subject_choose_any)
        db_plan.update_many(
            {
                "special_id": result_i["special_id"],
                "school_id": result_i["school_id"],
                "province_id": result_i["province_id"],
            },
            {"$set": {"finish_map": 1}}
        )
        print(str(cnt) + " " + result_i["school_id"] + " " + result_i["province_id"] + " " + result_i["special_id"])
        db.insert_one(d)
    except Exception as e:
        print(str(e) + str(result_i))


def check_choose(require_dict):
    all_choose = deepcopy(subject_choose_copy)
    for k, v in subject_chooses.items():
        all_choose[k] = check_choose_help(require_dict, v)
    return all_choose


def check_choose_help(require_dict, choose_list):
    if not all(i in choose_list for i in require_dict['r']):
        return 0
    if require_dict['n'] > 0 and len(set(require_dict['o']) & set(choose_list)) < require_dict['n']:
        return 0
    return 1


if __name__ == "__main__":
    # db_plan.update_many(
    #     {},
    #     {"$set": {"finish_map": 0}}
    # )
    get_map()
