import itertools
import os
from copy import deepcopy
from threading import Thread

from my_json import load_json
from my_mongo import client, province_id, school_id

basic_path = str(os.path.dirname(__file__)) + "/"
map_path = basic_path + "map_new.json"
map_new = load_json(map_path)
db = client.gaokao.school_plan_index
db_plan = client.gaokao.school_plan_sim
db_school = client.gaokao.school


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


def get_pipline():
    pipeline = [
        {
            "$match": {
                "min_section": {"$exists": True, "$regex": "^\\d+$"},
                "spname": {"$exists": True, "$ne": None},
                "level3": {"$exists": True, "$ne": None},
            }
        },
        {
            "$addFields": {
                "min_section_int": {"$toInt": "$min_section"}
            }
        },
        {
            "$match": {
                "min_section_int": {"$exists": True, "$ne": None, "$gt": 1}
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
                    "level3": "$level3",
                    "school_id": "$school_id",
                    "province_id": "$province_id",
                },
                "max_section": {"$avg": "$min_section_int"},
                "level3_name": {"$first": "$level3_name"},
                "sg_info": {"$first": "$sg_info"},
                "year_max": {"$max": "$year"},
                "batch_id": {"$first": "$batch_id"},
                "type_id": {"$first": "$type_id"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "level3": "$_id.level3",
                "school_id": "$_id.school_id",
                "province_id": "$_id.province_id",
                "max_section": 1,
                "level3_name": 1,
                "sg_info": 1,
                "year_max": 1,
                "type_id": 1,
            }
        },
        {
            "$sort": {
                "year_max": -1,
                "max_section": 1,
                "school_id": 1,
            }
        },
    ]
    result = list(db_plan.aggregate(pipeline, maxTimeMS=600000))
    return result


def get_map_help(result_list, insert_num=100):
    cnt = 0
    insert_list = []
    for result_i in result_list:
        try:
            d = {
                "school_id": result_i["school_id"],
                "province_id": result_i["province_id"],
                "level3": result_i["level3"],
                "year_max": int(result_i["year_max"]),
            }
            if db.find_one(d):
                continue
            cnt += 1
            school = db_school.find_one({"school_id": result_i["school_id"]})
            d = {
                "province_name": province_id[result_i["province_id"]],
                "school_name": school_id[result_i["school_id"]],
                "province_id": result_i["province_id"],
                "school_id": result_i["school_id"],
                "min_rank": int(result_i["max_section"]),
                "level3_name": result_i["level3_name"],
                "level3": result_i["level3"],
                "year_max": int(result_i["year_max"]),
                "school_province": school.get("province_id", ""),
                "is_dual_class": school.get("dual_class", 0),
                "is_985": school.get("f985", 0),
                "is_211": school.get("f211", 0),
            }
            if result_i["type_id"] == "1":
                d["sk_info"] = "理科"
                d["物理化学生物"] = 1
            elif result_i["type_id"] == "2":
                d["sk_info"] = "文科"
                d["历史政治地理"] = 1
            elif "sg_info" in result_i and result_i["sg_info"] and result_i["sg_info"] in map_new:
                d.update(check_choose(map_new[result_i["sg_info"]]))
                d["sk_info"] = result_i["sg_info"]
            else:
                d.update(subject_choose_any)
            insert_list.append(d)
            if len(insert_list) >= insert_num:
                db.insert_many(deepcopy(insert_list))
                print("insert" + str(cnt))
                insert_list = []
        except Exception as e:
            print(str(e) + str(result_i))
    if insert_list:
        db.insert_many(deepcopy(insert_list))


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


def run_in_pool():
    result = get_pipline()
    result_len = len(result)
    print(result_len)
    pool_num = 16
    result_len = result_len // pool_num
    thread_list = []
    result_new = []
    for i in range(pool_num - 1):
        result_new.append(deepcopy(result[i * result_len: (i + 1) * result_len]))
    result_new.append(deepcopy(result[(pool_num - 1) * result_len:]))
    result = None
    for result_i in result_new:
        t = Thread(target=get_map_help, args=(result_i,))
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()


def my_create_index():
    db.create_index(
        [
            ("year_max", -1),
            ("province_id", 1),
            ("school_id", 1),
            ("level3", 1),
        ]
    )
    db.create_index(
        [
            ("school_id", 1),
            ("province_id", 1),
            ("min_rank", 1),
        ]
    )


if __name__ == "__main__":
    my_create_index()
    run_in_pool()
