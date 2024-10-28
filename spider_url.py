from datetime import datetime
from copy import deepcopy

cookie = "gr_user_id=313475a7-1164-4b65-84e7-c9f0a032e210; UM_distinctid=1890016497e44-0a3c78759769d5-7e565473-1bcab9-1890016497f1eee; strategy=common; _token.common=8c455812a760469ea6c379301ff28853; _token_expiration.common=1690602561543; _token.gaokao=8c455812a760469ea6c379301ff28853; originLoginKey=c559b9d58156b40fadfa4bc72a80215c43903185b3926a4d944954f4866790e3a259a164a2aeed786eb6eb2b8617d5405526e5a2bfb3d5ab6494101c850d7ac5dd96d045100571af17adca0be60b73c77f0f98c1fe3422ee91f96e887527e7c5b2a8e91e939e268fb80b26797b92ed84d127ee0029203c85d50725f7405f09231b70b6348b032cc81e01c3e25ba84e8bf21c60a53957a4c7bcb3b118fdebe516; parseLoginKey=%7B%22phone%22%3A%2218648268144%22%2C%22mac%22%3A%225496a7abbe37252238d42e13a5549ef7%22%2C%22agent%22%3A%226%22%2C%22time%22%3A%221688010561%22%2C%22is_perfect%22%3A%221%22%2C%22wx_uin%22%3A%22%22%2C%22openid%22%3A%22%22%2C%22random%22%3A%22f6ENirQm%22%2C%22pushcode%22%3A%22%22%2C%22invitecode%22%3A%225JO1NNZ%22%7D; fillVolunteerData=%7B%22year%22%3Anull%2C%22province%22%3A%22%E5%86%85%E8%92%99%E5%8F%A4%22%2C%22score%22%3A600%2C%22optional%22%3Anull%2C%22classify%22%3A%22%E7%90%86%E7%A7%91%22%2C%22ranks%22%3A1729%2C%22gradeType%22%3Anull%2C%22subjects%22%3Anull%2C%22batch%22%3Anull%2C%22entrantType%22%3A1%2C%22artRank%22%3Anull%2C%22artScore%22%3Anull%7D; userVipStatus=[{%22type%22:1%2C%22isVip%22:false%2C%22vipTime%22:null%2C%22orderId%22:null%2C%22userStatus%22:1}%2C{%22type%22:2%2C%22isVip%22:false%2C%22vipTime%22:null%2C%22orderId%22:null%2C%22userStatus%22:1}]; whitch_edit={%22year%22:null%2C%22province%22:%22%E5%86%85%E8%92%99%E5%8F%A4%22%2C%22score%22:600%2C%22optional%22:null%2C%22classify%22:%22%E7%90%86%E7%A7%91%22%2C%22ranks%22:1729%2C%22gradeType%22:null%2C%22subjects%22:null%2C%22batch%22:null%2C%22entrantType%22:1%2C%22artRank%22:null%2C%22artScore%22:null}; areaid=15; cityid=1501; Hm_lvt_17c8dee9c87e3ab669ce5dd4f88140ec=1688024950,1688026735,1688051060,1688088106; Hm_lpvt_17c8dee9c87e3ab669ce5dd4f88140ec=1688088106; 88025341dda01c5f_gr_session_id=c85833d9-0aff-4b7b-85d4-20c5e46dcc47; 88025341dda01c5f_gr_session_id_sent_vst=c85833d9-0aff-4b7b-85d4-20c5e46dcc47; userInfoExpires=true"
token = "c3311de070cd4f7bafa4527ed5d9ff80"
head = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "no-cache",
    "Dnt": b'1',
    "Origin": "https://www.gaokao.cn",
    "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Microsoft Edge\";v=\"114\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58}",
}

host = "https://www.gaokao.cn/"
id_json_url = "https://static-data.gaokao.cn/www/2.0/info/linkage.json"
school_json_url = "https://static-data.gaokao.cn/www/2.0/school/list_v2.json"
years = [str(i) for i in range(2018, datetime.now().year + 1)]
map_id_url = "https://static-data.gaokao.cn/www/2.0/config/dicprovince/dicname2id.json"


class major_detail_json_url:
    url = "https://static-data.gaokao.cn/www/2.0/special/{id}/pc_special_detail.json"

    def to_string(self, id):
        return self.url.format(id=id)


class school_detail_json_url:
    url = "https://static-data.gaokao.cn/www/2.0/school/{id}/info.json"

    def to_string(self, id):
        return self.url.format(id=id)


class school_special_json_url:
    url = "https://static-data.gaokao.cn/www/2.0/school/{id}/pc_special.json"

    def to_string(self, id):
        return self.url.format(id=id)


class school_job_json_url:
    url = "https://static-data.gaokao.cn/www/2.0/school/{id}/pc_jobdetail.json"

    def to_string(self, id):
        return self.url.format(id=id)


class bom_major_map_url:
    url_1 = "https://gaokao.chsi.com.cn/zyk/zybk/ccCategory"
    url0 = "https://gaokao.chsi.com.cn/zyk/zybk/mlCategory/{type}"
    url1 = "https://gaokao.chsi.com.cn/zyk/zybk/xkCategory/{type}"
    url2 = "https://gaokao.chsi.com.cn/zyk/zybk/specialityesByCategory/{type}"
    url3 = "https://gaokao.chsi.com.cn/zyk/zybk/specialityDetail/{type}"

    def url0_to_string(self, type):
        return self.url0.format(type=type)

    def url1_to_string(self, type):
        return self.url1.format(type=type)

    def url2_to_string(self, type):
        return self.url2.format(type=type)

    def url3_to_string(self, type):
        return self.url3.format(type=type)


class province_url:
    province = {
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
    news_url = "https://static-gkcx.gaokao.cn/www/2.0/json/pcnews/{id}.json"
    high_school_url = "https://static-data.gaokao.cn/www/2.0/school/data/{id}.json"

    def news_to_string(self, id):
        return self.news_url.format(id=id)

    def high_school_to_string(self, id):
        return self.high_school_url.format(id=id)


class school_score_url:
    url = "https://static-gkcx.gaokao.cn/www/2.0/json/school/{id}/vote/vote.json"

    def to_string(self, school_id):
        return self.url.format(id=school_id)


class school_ico_url:
    url_ico = "https://static-data.gaokao.cn/upload/logo/{id}.jpg"
    url_pho = "https://static-data.eol.cn/upload/svideo/piliang_{id}_thumb.jpg"

    def ico_to_string(self, school_id):
        return self.url_ico.format(id=school_id)

    def pho_to_string(self, school_id):
        return self.url_pho.format(id=school_id)


class school_rank_url:
    url = "https://static-data.gaokao.cn/www/2.0/school/{id}/rank.json"

    def to_string(self, school_id):
        return self.url.format(id=school_id)


class bom_school_satis_url:
    url = "https://gaokao.chsi.com.cn/wap/sch/yxmydinfo/{id}"

    def to_string(self, school_id):
        return self.url.format(id=school_id)


class school_grade_special_url:
    data = {
        "local_batch_id": 7,
        "local_province_id": 15,
        "local_type_id": 1,
        "page": 1,
        "school_id": 184,
        "size": 10,
        "sp_xuanke": "",
        "special_group": "",
        "uri": "apidata/api/gk/score/special",
        "year": 2024,
    }
    mata = "http://static-data.gaokao.cn/www/2.0/school/{school_id}/dic/specialscore.json"
    url = r"https://api.zjzw.cn/web/api/"
    url_before_2022 = "http://static-data.gaokao.cn/www/2.0/schoolspecialscore/{schoolid}/{year}/{provinceid}.json"

    def mata_to_string(self, school_id):
        return self.mata.format(school_id=school_id)

    def to_string_before_2022(self, school_id, province_id, year):
        return self.url.format(schoolid=school_id, provinceid=province_id, year=year)

    def get_params(self, school_id, province_id, year, type_id, batch_id):
        data = deepcopy(self.data)
        data["local_batch_id"] = batch_id
        data["local_province_id"] = province_id
        data["local_type_id"] = type_id
        data["school_id"] = school_id
        data["year"] = year
        return data


class school_plan_url:
    data = {
        "local_batch_id": 7,
        "local_province_id": 15,
        "local_type_id": 1,
        "page": 1,
        "school_id": 184,
        "size": 10,
        "sp_xuanke": "",
        "special_group": "",
        "uri": "apidata/api/gkv3/plan/school",
        "year": 2024,
    }
    mata = "http://static-data.gaokao.cn/www/2.0/school/{school_id}/dic/specialplan.json"
    url = r"https://api.zjzw.cn/web/api/"
    url_before_2023 = "http://static-data.gaokao.cn/www/2.0/schoolspecialplan/{schoolid}/{year}/{provinceid}.json"

    def mata_to_string(self, school_id):
        return self.mata.format(school_id=school_id)

    def to_string_before_2023(self, school_id, province_id, year):
        return self.url_before_2023.format(schoolid=school_id, provinceid=province_id, year=year)

    def get_params(self, school_id, province_id, year, type_id, batch_id):
        data = deepcopy(self.data)
        data["local_batch_id"] = batch_id
        data["local_province_id"] = province_id
        data["local_type_id"] = type_id
        data["school_id"] = school_id
        data["year"] = year
        return data


class school_province_grade_url:
    """
    学校省分数线数据表
    """
    data = {
        "e_sort": "zslx_rank, min",
        "e_sorttype": "desc, desc",
        "local_province_id": 15,
        "local_type_id": 1,
        "page": 1,
        "school_id": 184,
        "size": 10,
        "sp_xuanke": "",
        "special_group": "",
        "uri": "apidata/api/gkv3/plan/school",
        "year": 2024,
    }
    url = r"https://api.zjzw.cn/web/api/"
    mata = "http://static-data.gaokao.cn/www/2.0/school/{school_id}/dic/provincescore.json"
    url_before_2022 = "http://static-data.gaokao.cn/www/2.0/schoolprovincescore/{schoolid}/{year}/{provinceid}.json"

    def mata_to_string(self, school_id):
        return self.mata.format(school_id=school_id)

    def to_string_before_2022(self, school_id, province_id, year):
        return self.url_before_2022.format(schoolid=school_id, provinceid=province_id, year=year)

    def get_params(self, school_id, province_id, year, type_id, batch_id):
        data = deepcopy(self.data)
        data["local_batch_id"] = batch_id
        data["local_province_id"] = province_id
        data["local_type_id"] = type_id
        data["school_id"] = school_id
        data["year"] = year
        return data
