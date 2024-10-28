import os
import itertools
from my_json import load_json
from my_mongo import client, province_id, school_id
from concurrent.futures import ThreadPoolExecutor

basic_path = str(os.path.dirname(__file__)) + "/"
map_path = basic_path + "map_new.json"
map_new = load_json(map_path)
db = client.gaokao.school_special_index
db_plan = client.gaokao.school_plan_sim
db_school = client.gaokao.school
cnt = 0
pool = ThreadPoolExecutor(12)


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


def dict_to_choose_list(d):
    choose_list = []
    if d['n'] == 0:
        choose_list.append(get_dict_by_list(d['r']))
    elif d['n'] == 1:
        for i in d['o']:
            choose_list.append(get_dict_by_list(d['r'] + [i]))
    elif d['n'] == 2:
        t = list(itertools.combinations(d['o'], 2))
        for i in t:
            choose_list.append(get_dict_by_list(d['r'] + list(i)))
    return choose_list


def get_dict_by_list(choose_list):
    if len(choose_list) == 0:
        return {
            "n": 0,
            "choose1": "",
            "choose2": "",
            "choose3": ""
        }
    if len(choose_list) == 1:
        return {
            "n": 1,
            "choose1": choose_list[0],
            "choose2": "",
            "choose3": ""
        }
    subject_sort(choose_list)
    if len(choose_list) == 2:
        return {
            "n": 2,
            "choose1": choose_list[0],
            "choose2": choose_list[1],
            "choose3": ""
        }
    if len(choose_list) == 3:
        return {
            "n": 3,
            "choose1": choose_list[0],
            "choose2": choose_list[1],
            "choose3": choose_list[2]
        }


def get_map_help(result_i):
    global cnt
    try:
        min_rank = int(result_i["max_section"])
        if min_rank < 1:
            return
        add_list = []
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
            d.update(get_dict_by_list(["物理", "化学", "生物"]))
            add_list.append(d)
        elif result_i["type_id"] == "2":
            d["sk_info"] = "文科"
            d.update(get_dict_by_list(["历史", "政治", "地理"]))
            add_list.append(d)
        elif "sg_info" in result_i and result_i["sg_info"] and result_i["sg_info"] in map_new:
            d["sk_info"] = result_i["sg_info"]
            choose_list = dict_to_choose_list(map_new[result_i["sg_info"]])
            for j in choose_list:
                add_list.append(d.copy())
                add_list[-1].update(j)
        else:
            d.update({
                "n": 0,
                "choose1": "",
                "choose2": "",
                "choose3": ""
            })
            add_list.append(d)
        db_plan.update_many(
            {
                "special_id": result_i["special_id"],
                "school_id": result_i["school_id"],
                "province_id": result_i["province_id"],
            },
            {"$set": {"finish_map": 1}}
        )
        print(str(cnt) + " " + result_i["school_id"] + " " + result_i["province_id"] + " " + result_i["special_id"])
        db.insert_many(add_list)
    except Exception as e:
        print(str(e)+str(result_i))


if __name__ == "__main__":
    get_map_json()
    get_map()
