import json
import os
import random
import re
import time

import jieba
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

sign_in_url = "https://www.zhihu.com/signin"
test_url = ["https://www.zhihu.com/api/v3/oauth/sms/supported_countries"]
doming = "https://www.zhihu.com"
special_url = "https://www.zhihu.com/special/1259823335602290688"
answer_url = "api/v4/questions/{id}/feeds"
answer_main_url = "https://www.zhihu.com/question/{id}"
answer_limit = 1000
basic_path = str(os.path.dirname(__file__)) + "/"
download_path = basic_path + "download/"
if not os.path.exists(download_path):
    os.makedirs(download_path)
driver_path = basic_path + "chromedriver.exe"
js = "var q=document.documentElement.scrollTop=100"
save_json = {"question": {}, "article": []}
save_json_path = basic_path + "zhihu.json"
cookies_path = basic_path + "cookies.json"
if os.path.exists(save_json_path):
    f = open(save_json_path, "r", encoding="utf-8")
    save_json = json.load(f)
    f.close()


def init():
    if not os.path.exists(cookies_path):
        zhihu_login()
    driver = get_standard_driver()
    content = get_end(special_url, driver, "//*[@id=\"root\"]/div[3]/div[2]/div/div[3]/div[2]/section[1]")
    tab_list = []
    re_list = re.findall('<a class="css-1ainv20" href=.*?>', content)
    for i in range(len(re_list)):
        j = re_list[i].find("href=")
        j = re_list[i][j + 6:].split(' ')[0]
        while j[-1] == '"' or j[-1] == "'" or j[-1] == ">":
            j = j[:-1]
        tab_list.append(doming + j)
    link_list = []
    re_list = re.findall('<div class="css-70dlgi"><a href=.*?>', content)
    for i in range(len(re_list)):
        j = re_list[i].find("href=")
        j = re_list[i][j + 6:].split(' ')[0]
        while j[-1] == '"' or j[-1] == "'" or j[-1] == ">":
            j = j[:-1]
        link_list.append(j)
    for i in tab_list:
        content = get_end(i, driver, "//*[@id=\"root\"]/div[3]/div[2]/div/div[3]/div[1]/div[1]/div/div/a[1]")
        re_list = re.findall('<div class="css-70dlgi"><a href=.*?>', content)
        for j in range(len(re_list)):
            k = re_list[j].find("href=")
            k = re_list[j][k + 6:].split(' ')[0]
            while k[-1] == '"' or k[-1] == "'" or k[-1] == ">":
                k = k[:-1]
            link_list.append(k)
    random.shuffle(link_list)
    for link in link_list:
        try:
            if "/question/" in link:
                zhihu_question(link, driver)
            elif "/answer/" in link:
                zhihu_answer(driver, link)
            elif "/p/" in link:
                zhihu_article(link, driver)
        except:
            continue
    f = open(save_json_path, "w", encoding="utf-8")
    json.dump(save_json, f, indent=4, ensure_ascii=False)
    f.close()


def zhihu_article(link, driver):
    s = "<div class=\"css-376mun\">.+?class=\"ContentItem-time\".*?于.*?<"
    pid = link.split("/")[-1]
    if pid in save_json["article"]:
        return
    content = get_end(link, driver, "//*[@id=\"root\"]/div/main/div/article/div[1]/div/div/div")
    content = re.findall(s, content)[0]
    pyear = content[-17:-13]
    pcontant = re.findall("[\u4e00-\u9fa5]+", content[:-30])
    content = []
    for i in pcontant:
        j = jieba.lcut(i)
        content.extend(j)
    save_json["article"].append(pid)
    with open(download_path + pyear + "_p" + pid + ".txt", "w", encoding="utf-8") as f:
        f.write(" ".join(content))
    print("article: " + pid + " success")


def zhihu_answer(driver, link):
    driver.get(link)
    re_try = 5
    while "/question/" not in driver.current_url and re_try > 0:
        if driver.current_url.split("/")[-1] in ["40", "404"]:
            return
        re_try -= 1
        time.sleep(1)
    if driver.current_url.split("/")[-1] in ["40", "404"]:
        return
    s = driver.current_url.find("/answer")
    link = driver.current_url[:s]
    print(link)
    zhihu_question(link, driver)


def zhihu_question(link, old_driver):
    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
    service = Service(driver_path)
    options.add_argument('--disable-extensions')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options, service=service)
    f = open(cookies_path, "r", encoding="utf-8")
    cookies = json.load(f)
    f.close()
    driver.get(random.choice(test_url))
    for i in cookies:
        driver.add_cookie(i)
    try:
        qid = link.split("/")[-1]
        if qid not in save_json["question"]:
            save_json["question"][qid] = []
        link = answer_main_url.format(id=qid)
        content = get_end(link, driver, "//*[@id=\"QuestionAnswers-answers\"]/div/div/div/div[2]/div/div[2]/div/div")
        s = "<div class=\"ContentItem AnswerItem\".*?<div class=\"ContentItem-time\"><a.*?><span.*?</span></a></div>"
        re_list = re.findall(s, content)
        for i in re_list:
            try:
                answer_time = re.findall("<meta itemprop=\"dateModified\" content=\".*?\">", i)[0]
                answer_time = answer_time[answer_time.find("content=") + 9:-2]
                answer_time = answer_time[:4]
                answer_id = re.findall("name=\"[0-9]*?\"", i)[0]
                answer_id = answer_id[6:-1]
                if answer_id in save_json["question"][qid]:
                    continue
                answer_word = re.findall("<div class=\"css-376mun\">.*?<div class=\"ContentItem-time\">", i)[0]
                answer_word = re.findall("[\u4e00-\u9fa5]+", answer_word)
                content = []
                for j in answer_word:
                    k = jieba.lcut(j)
                    content.extend(k)
                save_json["question"][qid].append(answer_id)
                with open(download_path + answer_time + "_a" + answer_id + ".txt", "w", encoding="utf-8") as f:
                    f.write(" ".join(content))
            except:
                continue
        link = answer_url.format(id=qid)
        re_try = 20
        while re_try > 0:
            logs = str(driver.get_log('performance'))
            logs = re.findall(r'"url"\s*:\s*"([^"]*' + link + r'[^"]*)"', logs)
            if len(logs) == 0:
                re_try -= 1
                driver.find_element(By.XPATH, '/html/body').send_keys(Keys.END)
                time.sleep(random.random() * 2)
                continue
            driver.quit()
            print("question: " + qid + " success")
            get_data(logs[0], qid, old_driver)
            f = open(save_json_path, "w", encoding="utf-8")
            json.dump(save_json, f, indent=4, ensure_ascii=False)
            f.close()
            return
    except:
        driver.quit()


def get_data(my_url, qid, driver):
    try:
        limit = answer_limit
        while my_url != "" and limit > 0:
            if "api" not in my_url or "unhuman" in my_url:
                raise ValueError("418")
            limit -= 1
            driver.get(my_url)
            content = driver.find_element(By.XPATH, "//*").get_attribute("outerHTML")
            content = re.sub(r"<.*?>", "", content)
            resp = json.loads(content)
            for i in resp["data"]:
                t = 0
                if "created_time" in i["target"]:
                    t = i["target"]["created_time"]
                if "updated_time" in i["target"]:
                    t = i["target"]["updated_time"]
                t = time.gmtime(int(t))
                t = str(t.tm_year)
                tid = str(i["target"]["id"])
                if tid in save_json["question"][qid]:
                    continue
                save_json["question"][qid].append(tid)
                content = i["target"]["content"]
                answer_word = re.findall("[\u4e00-\u9fa5]+", content)
                content = []
                for j in answer_word:
                    k = jieba.lcut(j)
                    content.extend(k)
                with open(download_path + t + "_a" + tid + ".txt", "w", encoding="utf-8") as f:
                    f.write(" ".join(content))
                print("answer: " + tid + " success")
            if resp["paging"]["next"] == my_url or my_url in resp["paging"]["next"]:
                return
            my_url = resp["paging"]["next"]
    except:
        return


def zhihu_login():
    options = Options()
    service = Service(driver_path)
    options.add_argument('--disable-extensions')
    driver = webdriver.Chrome(options=options, service=service)
    driver.get(sign_in_url)
    qr_code = WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
        (By.XPATH, '//*[@id="root"]/div/main/div/div/div/div/div[1]/div[1]/div[3]/div[1]/img')))
    with open("qr_code.png", "wb") as f:
        f.write(qr_code.screenshot_as_png)
    print("请扫描二维码登录")
    WebDriverWait(driver, 1000).until(expected_conditions.presence_of_element_located(
        (By.XPATH, '//*[@id="Popover15-toggle"]/img')))
    cookies = driver.get_cookies()
    f = open(cookies_path, "w", encoding="utf-8")
    json.dump(cookies, f)
    f.close()
    driver.close()
    driver.quit()


def get_end(url, driver, wait_xpath=""):
    driver.get(url)
    retury = 3
    while retury > 0:
        driver.find_element(By.XPATH, '/html/body').send_keys(Keys.END)
        try:
            curl = driver.current_url
            if curl != url:
                retury -= 1
                if "unhuman" in curl or curl.split("/")[-1] in ["40", "404"]:
                    raise ValueError("418")
                driver.get(url)
            if wait_xpath != "":
                driver.find_element(By.XPATH, wait_xpath)
            driver.find_element(By.XPATH, '/html/body').send_keys(Keys.END)
            break
        except:
            continue
    time.sleep(random.random() * 2)
    content = driver.find_element(By.XPATH, "//*").get_attribute("outerHTML")
    return content


def get_standard_driver():
    options = Options()
    service = Service(driver_path)
    options.add_argument('--disable-extensions')
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=options, service=service)
    f = open(cookies_path, "r", encoding="utf-8")
    cookies = json.load(f)
    f.close()
    driver.get(random.choice(test_url))
    for i in cookies:
        driver.add_cookie(i)
    return driver


init()
