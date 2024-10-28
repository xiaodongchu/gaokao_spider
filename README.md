# 项目概述

本项目为高考志愿推荐系统，主要由两部分组成，其一为**高考志愿推荐管理系统**，其二为**大数据面板**。

本项目基于 FastAPI + Vue3 的前后端分离架构，使用 json 文件完成前后端通信。

我们主要实现了以下功能：

**登录注册**：为持久化存储考生的个人信息即选择的高校，我们实现了系统的登录、注册功能。

**高校信息查询**：实现了全国共 2891 所本科、专科高校的查询功能，可以查询其具体信息，包括但不限于高校类型（985/211/双一流）、办学性质、学习指数、生活指数、就业指数、综合评分、学术水平、毕业生去向、男女比例等详细信息，除此之外，我们还展示了该校各个专业在2017-2022年间在全国各省的分数线、最低排名及科目要求等信息。我们使用了丰富、美观的图表、文字展示了这些信息。

**专业信息查询**：实现了本科、专科（高职）高校中开设的共 1536 个专业的查询功能，可以查询其具体信息，包括但不限于人气值、修业年限、授予学位、专业简介、综合满意度、办学条件满意度、教学质量满意度、就业满意度、选考学科建议、开设课程、考研方向、社会名人、男女比例、薪酬、就业地区分布、就业岗位分布等信息。我们使用了丰富、美观的图表、文字展示了这些信息。

**个性化志愿推荐**：使用位次法，根据考生选择的的省份、选课科目、排名、高校层次、高校所在省份等信息为开始推荐高、中、低三种风险度的高校。同时考生可以随时将该高校存入志愿表中，方便考生下次登录时查看。

**大数据面板展示**：为了更加直观、美观地展示全国范围内与志愿填报相关地信息，我们制作了一个大数据面板，实现了2018-2022年内，全国各省市的高考人数柱状图、新高考下所选科目与可选专业的数目占比饼状图、与志愿填报相关的知乎话题中出现频次超过1000的热词的词云图、各省市985/211/双一流/本科/专科学校占比、各省市一本率水滴图、重庆市与全国平均气温的对比折线图等。

下面我们结合具体代码及数据，详细分析本项目的原理。



# 数据获取


### 目录树

```bash
├─basic_info # 掌上高考链接中所用id等基础信息
│      get_basic_info.py
│      get_basic_info_class.py
│
├─grade_rank # 一分一段
│      grade_rank.py
│
├─grade_school # 学校分数线
│      choose_map.py
│      get_school_grade.py
│
├─grade_school_plan # 学校分专业招生计划
│      get_school_plan.py
│
├─grade_school_sim # 学校分专业录取分数
│      get_school_grade_sim.py
│
├─major # 专业介绍
│      get_major.py
│
├─major_map # 专业类别数据，来自阳光高考网
│      get_major_map.py
│
├─my_class # 部分辅助类
│      grade_major_index.py
│      grade_sim.py
│      grade_sim_index.py
│      major.py
│      plan_grade.py
│      province.py
│      school.py
│
├─school_detail # 学校详细信息
│      get_school_detail.py
│
├─school_ico # 学校图片/标识
│      school_ico.py
│
├─school_job # 学校就业
│      get_school_job.py
│
├─school_rank # 学校排名
│      school_rank.py
│
├─school_score # 学校评价
│      school_score.py
│
├─school_special # 学校专业
│      get_school_special.py
│
├─simer # 信息整合
│  │  grade_index.py # 用于志愿推荐的数据整合
│  │  grade_simer.py # 学校分数线与专业分数线整合
│  │  map_new.json # 选课解析
│  │
│  ├─major # 专业信息整合
│  │      basics.py
│  │      detail.py
│  │      DetailRest.py
│  │      majorMap.py
│  │
│  └─school # 学校信息整合
│          schoolBasic.py
│          schoolDetail.py
│          schoolJobWhere.py
│
├─sql # 数据库存储以及部分检索代码
│  │  grade_plan.py # 专业成绩与招生计划
│  │  grade_plan_search.py # sql查询
│  │  grade_sim.py # 学校分数线
│  │  grade_sim_search.py # sql查询
│  │  grade_sim_index.py # 用于志愿推荐
│  │  grade_sim_index_search.py # 根据选课志愿推荐数据库操作
│  │
│  ├─major # 专业信息存入数据库
│  │      insert_majorBasic_into_sql.py
│  │
│  └─school # 学校信息存入数据库
│          insert_schoolBasic_into_sql.py
│          insert_schoolDetail_into_sql.py
│          insert_specialDetail_into_sql.py
│
├─whether
│      whether.py # 天气爬虫
│
└─zhihu
│       zhihu-spark.py #spark词频统计
│       zhihu-spider.py #知乎爬虫
│
├─big_data # 少量数据统计代码
│      count_choose.py
│      count_grade.py
│
│  check_version.py # 检查chrome版本并自动下载chromedriver
│  my_json.py # 多次使用的json操作函数
│  spider_url.py # 部分链接
│
```

### 数据来源与爬取方法

##### 阳光高考：

- request获取html；
- 正则匹配到所需数据。

##### 掌上高考：

- 对网页加载过程中访问的所有资源进行分析；

- 找出所需数据的请求连接，分析链接格式；

- 伪造请求头，获取并解析json；

- 根据网页内容猜测json中对应键值路径，得到数据。

- 在掌上高考中，所有链接中均使用了唯一的省份、学校、专业id来进行区分，省份id为身份证号前两位。在打开首页时，会从以下链接获取学校、专业id字典，解析可获得所需数据：

  ```python
  "https://static-data.gaokao.cn/www/2.0/info/linkage.json"
  ```

##### 知乎：

- 知乎在请求的过程中，内容来源多样，且并非一次性加载，获取方式最为复杂。

- 对于话题而言，每个话题下有若干tag；每个tag下有若干文章/回答/问题，只有点击tag才会加载。

- 对于文章而言，核心内容通常会包含在一个html内，随着页面滑动，再另行请求评论等更多信息。

  ```python
  "https://zhuanlan.zhihu.com/p/{文章id}"
  ```

- 对于回答而言，回答是问题下的一个回答，从链接中可分析出对应问题id。单一回答内容会直接包含在一个html内，随着页面滑动，再另行请求评论等更多信息。

  ```python
  "https://www.zhihu.com/question/{问题id}/answer/{回答id}"
  ```

- 对于问题而言，问题下有若干回答。在请求时，前1-6个回答会根据内容长度直接包含在html中。之后随着页面滑动，会依次请求json。每个json中包含几个回答内容、以及下一个请求json的短链接。个人猜测，知乎可能对token进行了严格限制，只有先完成对html的请求，获取到第一个json连接，再继续保证一定时间间隔请求next-json，否则会直接跳转到unhuman页面。

  ```python
  "https://www.zhihu.com/question/{问题id}"
  ```

- ![image-20230713105145514](./images/image-20230713105145514.jpg)

- ![image-20230713105106566](./images/image-20230713105106566.jpg)

- 为了尽可能稳定爬取，我选择使用chromedriver爬取知乎数据。使用

  ```python
  driver.find_element(By.XPATH, '/html/body').send_keys(Keys.END)
  ```

  模拟页面滑动；

  ```python
  driver.find_element(By.XPATH, "//*").get_attribute("outerHTML")
  ```

  获取html数据（需要先滑动页面，再获取）

  ```python
  options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
  ……
  logs = str(driver.get_log('performance'))
  ```

  记录请求记录，随页面滑动从中获取next-json。之后依次请求json。
  此外，为了避免校园网速带来的问题，我禁止chrome加载图片，并使用

  ```python
  WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(By.XPATH,""))
  ```

  来防止超时错误

### 分数信息获取 

分数信息来自掌上高考

共爬取**31**省，近**5-8**年，所有可获取的分数数据

共计爬取**549264**个json文件

##### 学校分数线

```python
"https://static-data.gaokao.cn/www/2.0/schoolprovincescore/{schoolid}/{year}/{provinceid}.json"
```

![image-20230713144514517](./images/image-20230713144514517.jpg)

##### 专业分数线

```python
"https://static-data.gaokao.cn/www/2.0/schoolspecialscore/{schoolid}/{year}/{provinceid}.json"
```

![image-20230713144545497](./images/image-20230713144545497.jpg)

##### 招生计划

```python
"https://static-data.gaokao.cn/www/2.0/schoolspecialplan/{schoolid}/{year}/{provinceid}.json"
```

![image-20230713150616561](./images/image-20230713150616561.jpg)

### 学校信息获取

学校基础信息主要源自掌上高考、学校满意度信息源自阳光高考；二者根据学校名称对应。

共获取**2891**所学校信息。共计**12666**个json文件

##### 学校简介

```python
"https://static-data.gaokao.cn/www/2.0/school/{id}/info.json"
```

![image-20230713101344764](./images/image-20230713101344764.jpg)

##### 学校开设专业

```python
"https://static-data.gaokao.cn/www/2.0/school/{id}/pc_special.json"
```

![image-20230713101420850](./images/image-20230713101420850.jpg)

##### 学校排名

```python
"https://static-data.gaokao.cn/www/2.0/school/{id}/rank.json"
```

![image-20230713114225915](./images/image-20230713114225915.jpg)

##### 学校就业信息

```python
"https://static-data.gaokao.cn/www/2.0/school/{id}/pc_jobdetail.json"
```

![image-20230713114445375](./images/image-20230713114445375.jpg)

### 专业信息获取

专业介绍信息来自掌上高考网；专业评价信息、专业所属一级学科来自阳光高考网；二者根据专业代码对应。

> 由于重庆大学在近年来采用大类招生，因此分数信息未与专业信息进行对应

共获取**1472**个专业信息，共计**3593**个文件。

##### 专业基本信息

```python
"https://static-data.gaokao.cn/www/2.0/special/{id}/pc_special_detail.json"
```

![image-20230713153337090](./images/image-20230713153337090.jpg)

##### 专业详细信息与满意度信息

```python
"https://gaokao.chsi.com.cn/zyk/zybk/ccCategory" #本科、专科id，对应下一链接的type
"https://gaokao.chsi.com.cn/zyk/zybk/mlCategory/{type}" #门类id，对应下一链接的type
"https://gaokao.chsi.com.cn/zyk/zybk/xkCategory/{type}" #专业类id，对应下一链接的type
"https://gaokao.chsi.com.cn/zyk/zybk/specialityesByCategory/{type}" #专业名称id，对应下一链接的type
"https://gaokao.chsi.com.cn/zyk/zybk/specialityDetail/{type}" #详细信息
```

![image-20230713153904575](./images/image-20230713153904575.jpg)

### 知乎问答信息获取

知乎共爬取了**41404**篇文章和回答。

提取出文章或回答中文正文，使用**jieba**进行分词。

按照utf-8格式txt存储分词结果，并按回答年分类，词语文本共计**52MB**

回答、文章主要来自以下话题：

```python
"https://www.zhihu.com/special/1259823335602290688"
```

![image-20230713160530653](./images/image-20230713160530653.jpg)

![3101859770回答的分词结果](./images/image-20230713160148857.jpg)

### 数据整合与存储

##### 知乎词频统计与分析

```python
word_counts = lines.flatMap(lambda line: line.split(" ")) \
	.filter(lambda word: word not in stopwords) \
	.map(lambda word: (word, 1)) \
	.reduceByKey(lambda a, b: a + b) \
	.sortBy(lambda x: x[1], ascending=False)
```

统计结果按年份展示在大数据面板中

##### 选课方案存储与匹配

学校分数线涉及到选课方案。部分省份采用传统文理分科；部分省份采用六选三；部分省份采用物理历史二选一+四选三；而浙江为七选三（另有技术）。为了便于处理，我们统一按如下顺序对选课排序：

```python
def subject_sort(subjects):
    order = {"物理": 1, "历史": 2, "化学": 3, "政治": 4, "生物": 5, "地理": 6, "技术": 7}
    if not all(subject in order.keys() for subject in subjects):
        raise ValueError()
    return sorted(subjects, key=lambda x: order.get(x, float('inf')))
```

由于各省市、各学校对新高考的表述差异很大，在我们获得的数据中，除浙江省和文理分科的省份外，对选课要求的表述有157种，实际选课方案只有{C_6^3}=20种，浙江省有42种表述，实际选课方案有35种。因此，我们对199种表述进行统一格式化，以便于数据统计、后端处理以及前端展示。

json格式：

```python
{
	"r": ["物理"], #必选科目列表
	"n": 1, #可选科目中最少选择数目
	"o": ["化学", "生物"] #可选科目列表
} # 该json表示物理必选，化学与生物二选一
```

sql格式：

```bash
choose1,choose2,choose3…… #三项严格按照上述排序函数排序，空字符串或null表示不限（每个专业可能对应多行）
"物理","化学","" #必选物理生物
"物理","生物","" #必选物理化学
# 两行共同表示“物理必选，化学/生物二选一”，此格式用于志愿推荐中选课的匹配

# 对文理分科的省份或当年未采用新高考的历史数据
"物理","化学","生物" #理科（必选物化生）
"历史","政治","地理" #文科（必选史政地）
```

sql匹配：

```python
choose_list = subject_sort(["物理","化学","地理"]) # 先按上述顺序排序
where = []
where.append("choose1 is null or choose1=''")
where.append("(choose1 = '{}' and (choose2 is null or choose2=''))".format(choose_list[2]))
where.append(
        "(choose1 = '{}' and "
        "(choose2 is null or choose2='' or choose2='{}'))".format(choose_list[1], choose_list[2]))
where.append("(choose1 = '{}' and "
                 "(choose2 is null or choose2='' or "
                 "(choose2='{}' and "
                 "(choose3 is null or choose3='' or choose3='{}')) or "
                 "(choose2='{}' and (choose3 is null or choose3=''))))".format(choose_list[0], choose_list[1],choose_list[2], choose_list[2]))
where = " or ".join(where)                                                        
```

字符串格式（用于前端展示，在整合时即存入数据库）

```python
def choose_to_string(require):
    if require["n"] == 0 and len(require["r"]) == 0:
        return "不限"
    s = ""
    if len(require["r"]) > 0:
        r = require["r"]
        s += "["
        for i in range(len(r)):
            s += r[i] + "、"
        s = s[:-1] + "]必选；"
    if len(require["o"]) > 0:
        o = require["o"]
        s += "["
        for i in range(len(o)):
            s += o[i] + "/"
        s = s[:-1]
        s += "]" + str(len(require["o"])) + "选" + str(require["n"]) + "；"
    return s
# 例如："[物理]必选；[化学/生物]2选1；"
```

##### 学校各选课方案排名汇总与预测

该表为志愿推荐设计。我们汇总了各学校在各省份各年的数据，并按上述格式存储选课方案，并对每种选课方案每年招生最低排名进行统计和预测。

在本表中，我为省份名、最低排名、以及三个选课要求建立mysql索引。建立索引后，后端对志愿推荐的相应速度提高超80%。

```sql
create index province_index on grade_sim_index(province_name)
create index min_rank_index on grade_sim_index(min_rank)
create index choose1_index on grade_sim_index(choose1)
create index choose2_index on grade_sim_index(choose2)
create index choose3_index on grade_sim_index(choose3)
```

##### 学校各专业分数线信息整合

该表数据展示在各学校详情页面首页。分年份和招生省份展示。整合了先前爬取的专业分数信息以及专业招生计划。

在本表中，我为（学校名、招生省份、年份）建立复合索引。以优化后端相应速度。

```sql
create index province_school_year on grade_plan(province_name,school_name,year)
```

##### 学校信息整合

学校信息整合了上述爬取的学校简介、学校排名、学校就业信息json。并分配新id，存储入数据库。

在学校信息表中，我们为学校名称建立了sql索引，以加快后端相应速度。

##### 专业信息整合

专业信息整合了上述爬取的专业基本信息、详细信息、满意度信息。并存入数据库。

在专业信息表中，我们为专业名称建立了sql索引，以加快后端相应速度。

# 前端：Vue3

### 登陆/注册页面

该前端页面分为三大部分，这也是Vue组件书写的三大部分：template、script、style scoped。

其中，登录页面tmplate部分使用了 Vue.js 和 Element Plus UI 组件，构建了最基本的登录框：用户名与输入密码以及登录注册按钮。当用户填写用户名及密码后，通过绑定`vmodel`可将`username`及`password`传递至表单`form`，登录和注册按钮则分别绑定了`clickLogin()`及`clickRegister()`函数，点击即触发对应函数行为；script部分包含了登录页面的逻辑，处理表单提交、验证、API 请求和页面导航等功能。

它调用了`/components/RegisterDialog.vue`，包含登录验证、注册验证及服务器验证。此外，它通过`.post`函数连接到本地网址：`http://192.168.197.190:8000/userlogin`，将form数据传递过去进行核对，通过后端验证即登录成功，跳转至/home路径；style部分则包含登录页面的 CSS 样式，主要调整了颜色、大小等。

登录页面通过后端 API 接口与后端服务器进行交互。以下是使用的后端 API 接口：
**接口：** `POST /userlogin`
**描述：** 用户登录接口
**参数：**
`username `(字符串)：用户输入的用户名。
`password` (字符串)：用户输入的密码。
**响应：**
`code` (数字)：响应代码，表示登录操作的成功或失败。
`data` (对象)：登录成功时返回的额外数据。
`message` (字符串)：描述登录操作结果的消息。

### **高校信息展示页面**

SchoolView.vue文件

**脚本部分**

**schoolName**

- 类型：`ref`
- 描述：学校名称。

**schoolClass**

- 类型：`ref`
- 描述：学校分类。

**query**

- 类型：`computed`
- 描述：计算属性，根据`schoolClass`和`schoolName`构造发送请求的参数。

**pageSchoolList**

- 类型：`ref`
- 描述：当前页显示的学校列表。

**getSchoolList**

- 类型：`function`
- 描述：发送请求获取学校列表的函数。

**handleSearch**

- 类型：`function`
- 描述：处理搜索操作的函数，调用`getSchoolList`函数获取学校列表。

当访问高校信息查询页面或者使用页面中的搜索功能时，最终都会调用`getSchoolList`函数。

```javascript
const getSchoolList = () => {
    request
        .post("http://192.168.111.190:8000/getSchoolList", query.value)
        .then((res) => {
        if (res.code == 200) {
            pageSchoolList.value = res.data;
            total.value = res.page_total;
            //ElMessage.success("获取学校列表成功");
        } else {
            ElMessage.error({
                message: "获取失败:" + res.message,
            });
        }
    })
        .catch((err) => {
        ElMessage.error({
            message: "服务器错误：" + err,
        });
    });
};
```

函数内部使用了`request`模块发送POST请求，向`http://192.168.111.190:8000/getSchoolList`地址发送请求。这个地址就是虚拟机上后端程序运行并向前端发送数据的地址。请求参数为`query.value`，其中`query`是一个计算属性，用于构造发送请求的参数，包括学校名称、学校分类、分页信息等。如果响应状态码`res.code`为200，表示请求成功，将获取到的学校列表数据赋值给`pageSchoolList`，将返回的总页数赋值给`total`。

### 高校信息详情页面

高校信息详情页主要分为分数线和高校信息两个选项卡，分数线部分展示该高校具体的专业录取分数线，高校信息部分展示该高校的相关数据。

**页面部分**

**intro**

- 类型：`div`
- 描述：高校综合评分指标的容器。

**level-chart**

- 类型：`div`
- 描述：高校等级图表的容器。

**rate-bar**

- 类型：`div`
- 描述：录取率条形图的容器。

**boy-girl**

- 类型：`div`
- 描述：男女比例的容器。

**score-chart**

- 类型：`div`

- 描述：高校分数线图表的容器。

**图表相关函数**

- `initRoundStudy`方法用于初始化学习指数的图表。

- `updateRoundStudy`方法用于更新学习指数的图表数据。

- `initRoundLife`方法用于初始化生活指数的图表。

- `updateRoundLife`方法用于更新生活指数的图表数据。

- `initRoundJob`方法用于初始化就业指数的图表。

- `updateRoundJob`方法用于更新就业指数的图表数据。

- `initRoundCompre`方法用于初始化综合评分的图表。

- `updateRoundCompre`方法用于更新综合评分的图表数据。

- `initScoreChart`方法用于初始化分数线图表。

- `updateScoreChart`方法用于更新分数线图表的数据。

- `initLevelChart`方法用于初始化高校等级图表。

- `updateRateBar`方法用于更新录取率条形图的数据。

- `initScaleBar`方法用于初始化男女比例条形图。

- `updateScaleBar`方法用于更新男女比例条形图的数据。

比较特殊的是`getSchoolDetail`函数和`getEachSp`函数，在这两个函数中`getSchoolDetail`函数用于发送请求获取学校的详细信息，并更新图表数据，`getEachSp`函数用于发送请求获取专业列表数据。它们都使用`request.post`方法发送POST请求，请求URL为`http://192.168.80.190:8000/getSchoolDetail`以及`http://192.168.80.190:8000/getEachSp`。通过这种方式获取学校专业信息和学校相关数据。

### 专业信息展示页面

该组件提供了一个专业搜索和列表展示的功能，用户可以根据专业名称、本科/专科分类以及具体的专业分类进行搜索，并展示相应的专业列表。用户还可以通过分页功能浏览不同页码的专业列表。

**数据和方法**

- `specialName`: 用于存储用户输入的专业名称。

- `specialLevel`: 用于存储用户选择的本科/专科分类。

- `specialClass`: 用于存储用户选择的具体的专业分类。

- `classList`: 根据`specialLevel`的值动态计算的本科/专科分类列表。

- `form`: 根据用户的搜索条件构造的POST请求Body，包含搜索关键字、本科/专科分类和具体的专业分类。

- `handleSearch`: 处理搜索按钮点击事件的方法。

`getSpecialList`函数是用于获取专业列表数据的方法。它会发送一个 POST 请求到服务器，并传递搜索条件和分页信息作为请求参数。具体实现如下：

```javascript
const getSpecialList = () => {
    request
        .post("http://192.168.111.190:8000/getSpecialList", form.value)
        .then((res) => {
        if (res.code == 200) {
            pageSpecialList.value = res.data;
            total.value = res.page_total;
            //ElMessage.success("获取学校列表成功");
        } else {
            ElMessage.error({
                message: "获取失败:" + res.message,
            });
        }
    })
        .catch((err) => {
        ElMessage.error({
            message: "服务器错误：" + err,
        });
    });

};
```

通过`request.post`方法向服务器发送一个 POST 请求。请求的 URL 是`http://192.168.111.190:8000/getSpecialList`，表示获取专业列表的接口地址。作为请求的参数，我们使用`form.value`，它是一个响应式的计算属性，包含了搜索条件和分页信息。这样可以确保在`form`的值发生变化时，请求的参数也会相应地更新。

### 专业详情页面

专业详情页面分为左右两部分，左边展示了专业的详细介绍，包括专业简介、专业详解、选考学科建议、开设课程、考研方向和社会名人等内容，右边展示了专业的相关图表，包括综合满意度、办学条件满意度、教学质量满意度、就业满意度的圆形图表，以及男女比例的柱状图和其他相关图表。

这部分的重点是`getSpecialDetial`函数，这个函数用于通过网络请求获取专业的详细信息。它调用了自定义的 `request` 模块的 `post` 方法，并将专业的 ID 作为请求的参数。请求成功后，将返回的数据赋值给 `detail` 引用，并调用 `updateChart` 方法更新图表。

```python
const getSpecialDetial = () => {
    request
        .post("http://192.168.111.190:8000/getSpecialDetail", { id: specialId })
        .then((res) => {
        if (res.code == 200) {
            detail.value = res.data;
            updateChart(detail.value);
        } else {
            ElMessage.error({
                message: "获取失败:" + res.message,
            });
        }
    })
        .catch((err) => {
        ElMessage.error({
            message: "服务器错误：" + err,
        });
    });
};
```

请求的参数是一个对象 `{ id: specialId }`，其中 `specialId` 是通过路由获取的当前专业的 ID。请求成功后，通过 `then` 方法处理响应结果。如果响应的状态码 `code` 等于 200，表示获取成功，将响应的数据 `res.data` 赋值给 `detail.value`，并调用 `updateChart` 方法更新图表。如果状态码不是 200，则通过 `ElMessage.error` 显示错误消息。如果请求过程中发生错误，则通过 `catch` 方法捕获错误，并通过 `ElMessage.error` 显示错误消息。

### 个性化志愿推荐页面

**模板部分**

- 使用了 Vue.js 和 Element Plus UI 组件，用`el-checkbox`生成科目多选框，通过`vmodel`绑定数据至`selectedSubjects`；

- 用`el-input`输入和记录分数和排名，传递至form表单；

- 使用`el-radio`单选所在省份、风险、学校省份、学校特色，数据同样传递至form表单。

- 定义推荐学校列表部分：从`https://static-data.gaokao.cn/upload/logo/`获取学校校徽图片，通过`school.id`可以跳转至该学校详情页面，同时展示最低排名、录取概率以及志愿表，点击志愿表按钮可触发`handleAddSelect`函数。

**脚本部分**

- 包含了推荐页面的逻辑,它处理表单提交、验证、API 请求和页面导航等功能。

- 定义函数handleAddSelect，通过`post`将数据传递至后端`http://192.168.80.190:8000/addselect`。

- 定义函数query，从后端返回数据。定义函数`getSchoolList`，从后端`http://192.168.80.190:8000/recommend`获取推荐学校信息（`query.value`）。

- 定义函数`handleSearch`，来判断科目选择，当选择三门科目时获取推荐学校，大于时报错进行提醒。

**样式部分**

- 包含推荐页面的 CSS 样式，调整了颜色、大小、位置等细节。



# 后端：FastAPI

### 高考志愿管理系统

##### 登录 & 注册功能

1. 登录

![](./images/login_fastapi.jpg)

上图为登录功能的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class User(BaseModel):
    username: str
    password: str
```

分别为用户名和密码，我们在数据库 user 中存储这些信息：

```sql
+-----------+-------------+------+-----+---------+-------+
| Field     | Type        | Null | Key | Default | Extra |
+-----------+-------------+------+-----+---------+-------+
| user_name | varchar(50) | YES  |     | NULL    |       |
| pass_word | varchar(50) | YES  |     | NULL    |       |
+-----------+-------------+------+-----+---------+-------+
```

对登录功能的处理逻辑如下：

```python
def check_credentials(username, password):
    cnx = connect_sql()
    cursor = cnx.cursor()
    query = ("SELECT pass_word FROM user WHERE user_name = %s")
    cursor.execute(query, (username, ))
    result = cursor.fetchone()
    cursor.close()
    cnx.close()
    if result is None:
        return False
    return result[0] == password

@app.post("/userlogin")
def user_login(user: User):
    """
        用户登录
    """
    if check_credentials(user.username, user.password):
        return {
            'code': 200,
            'data': {'message': '登录成功'}
        }
    else:
        return {
            'code': 201,
            'data': {'message': '登录失败'}
        }
```

即通过 python 连接 mysql 数据库，然后查询请求体中用户名是否存在对应密码，如果该密码不存在或与请求体中的密码不一致，则登录失败，反之登录成功，返回正确码 200.

2. 注册

![](./images/register_fastapi.jpg)

上图为注册功能的 FastAPI 接口，为 POST 请求。

其请求体与登录功能相同。对注册功能的处理逻辑如下：

```python
@app.post("/userregister")
def user_login(user: User):
    """
        用户注册
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    insert_query = "INSERT INTO user (user_name, pass_word) VALUES (%s, %s)"
    data = (user.username, user.password)
    cursor.execute(insert_query, data)
    cnx.commit()
    cursor.close()
    cnx.close()

    return {
        'code': 200,
        'data': {'message': '登录成功'}
    }
```

即通过 python 连接 mysql 数据库，将请求体中的用户名和密码存入 user 数据库中即可。



##### 高校信息查询功能

1. 高校列表展示

![](./images/schoolBasic_fastapi.jpg)

上图为高校列表展示功能的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class School(BaseModel):
    province: str
    school_name: str
    school_class: int
    page_size: int
    page_index: int
```

主要为高校所在的省份、高校的名称、高校的级别（985/211/双一流）以及配合前端分页展示所需要的页大小、索引。

根据前端页面的功能，其主要的处理逻辑如下：

**搜索功能**：使用 sql 语句中的 LIKE 子句和通配符实现模糊搜索的功能，找到所有名称中包含用户所输入的字符串的高校，并返回一个数组，数组中存入每一个高校的 json 数据，该 json 数据中包括高校的 id、名称、所在省份和所在城市名，用于前端展示。

```python
    # 搜索功能
    if school.school_name != "":
        cnx = connect_sql()
        cursor = cnx.cursor()
        # 模糊查询
        query = ("SELECT * FROM schoolBasic WHERE name LIKE %s")
        cursor.execute(query, ("%" + school.school_name + "%",))
        results = cursor.fetchall()
        cursor.close()
        cnx.close()
        for result in results:
            schools.append(
                {
                    'id': result[0],
                    'name': result[1],
                    'province': result[2],
                    'city': result[3]
                }
            )

        return {
            'code': 200,
            'data': schools,
            'page_total': 10,
        }
```

**筛选功能**：以筛选所有 985 大学为例：

```python
    # 985 高校
    if school.school_class == 3:
        cnx = connect_sql()
        cursor = cnx.cursor()
        query = ("SELECT * FROM schoolBasic WHERE school_class like '1%'")
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        cnx.close()
        for result in results:
            schools.append(
                {
                    'id': result[0],
                    'name': result[1],
                    'province': result[2],
                    'city': result[3]
                }
            )
```

2. 高校详细信息展示

**高校详细信息**

![](./images/schoolDetail_fastapi.jpg)

上图为高校详细信息展示功能的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class SchoolQuery(BaseModel):
    id: int
```

即为查询高校的 id.

其处理逻辑如下，即为根据 id 从数据库中取出对应字段组成 json 数组传出即可。 

```python
@app.post("/getSchoolDetail")
async def get_school_detail(query: SchoolQuery):
    """
        某一高校的详细信息
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    query_sql = ("SELECT * FROM schoolDetails WHERE id = %s")
    data = (query.id,)
    cursor.execute(query_sql, data)
    results = cursor.fetchall()
    cursor.close()
    cnx.close()

    for result in results:
        return {
            "code": 200,
            "data": {
                "id": result[0],                    # 高校 id    
                "name": result[1],                  # 高校名称    
                "nature": result[2],                # 高校办学性质 
                "level": result[3],                 # 高校等级   
                "f985": result[4],                  # 是否为985   
                "f211": result[5],                  # 是否为211   
                "dual_class": result[6],            # 是否为为双一流 
                "study": result[7],                 # 学习指数 
                "life": result[8],                  # 生活指数 
                "job": result[9],                   # 就业指数 
                "comprehensive": result[10],        # 综合评分 
                "content": result[11],              # 简介 
                "job_class": eval(result[12]),      # 毕业生去向
                "job_ratio": eval(result[13]),      # 去向比例
                "num_lab": result[14],              # 重点实验室数量 
                "num_subject": result[15],          # 国家重点学科数量 
                "num_master": result[16],           # 硕士点数量
                "num_doctor": result[17],           # 博士点数量 
                "jobrate": result[18],              # 就业率     
                "postgraduate": result[19],         # 深造率  
                "abroad": result[20],               # 出国率         
                "men_rate": result[21],             # 男生比例     
            }
        }
```

**高校各个专业分数线及排名**

![](./images/getEachSp_fastapi.jpg)

上图为高校各个专业分数线及排名展示功能的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class SpQuery(BaseModel):
    id: int
    year: str
    province: str
```

分别为学校的id、查询年份和省份，处理逻辑如下，先根据 id 从 schoolBasic 数据表中的找到学校名称，再根据学校名称从 grade_plan 表中获取对应的专业名、分数线、排名、需要的选科要求。

```python
@app.post("/getEachSp")
async def get_each_sp(query: SpQuery):
    """
        某一高校各个年份的专业分数线信息
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    query_sql = ("SELECT name FROM schoolBasic WHERE id = %s")
    data_sql = (query.id, )
    cursor.execute(query_sql, data_sql)
    results= cursor.fetchone()
    school_name=results[0]
    where = "province_name = '{}' and school_name = '{}' and year = '{}'".format(query.province, school_name, query.year)
    q = "select major_name,batch_name,require_str,min_grade,min_rank from grade_plan where " + where
    cursor.execute(q)
    results = cursor.fetchall()
    cursor.close()
    cnx.close()

    data = []
    for result in results:
        item = {
            "name": result[0],
            "batch": result[1],
            "score": result[3],
            "rank":  result[4],
            "require":  result[2],
        }
        if item['score'] != 0:
            data.append(item)

    return {
        "code": 200,
        "data": data
    }
```



##### 专业信息查询

1. 专业列表展示

![](./images/getSpecialList_fastapi.jpg)

上图为专业列表展示功能的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class Special(BaseModel):
    name: str
    level: str
    class_: str
    page_size: int
    page_index: int
```

主要为专业的名称、专业的级别（本科/专科）、专业的类别（理学/工学/文学）以及配合前端分页展示所需要的页大小、索引。

根据前端页面的功能，其主要的处理逻辑如下：

**搜索、筛选功能**：使用 sql 语句中的 LIKE 子句和通配符实现模糊搜索的功能，找到所有名称中包含用户所输入的字符串的专业；如果用户未输入名称则根据用户选择的筛选项（级别/类别）找到对应的专业，最后返回一个数组，数组中存入每一个专业的 json 数据，该 json 数据中包括专业的编码、名称、热度、修业年限、颁发学位，用于前端展示。

```python
@app.post("/getSpecialList")
async def get_special_list(special: Special):
    """
        获取专业列表
    """
    cursor = cnx.cursor()

    if special.name != "":
        query_sql = ("SELECT * FROM majorBasic WHERE name LIKE %s")
        data = ("%" + special.name + "%", )
    else:
        if special.class_ == '全部':
            query_sql = ("SELECT * FROM majorBasic where sp_level = %s")
            data = (special.level, )
        else:
            query_sql = ("SELECT * FROM majorBasic WHERE sp_level = %s AND belong = %s")
            data = (special.level, special.class_)
    
    cursor.execute(query_sql, data)
    results = cursor.fetchall()

    special_list = []
    for result in results:
        sp = {
            'id': result[0],
            'name': result[1],
            'hot': result[2],
            'code': result[0],
            'year': result[3],
            'degree': result[4],
        }
        if sp['name'] != '未知':
            special_list.append(sp)

    return {
        'code': 200,
        'data': special_list,
        'page_total': 1,
    }

```

2. 专业详细信息展示

![](./images/specialDetails_fastapi.jpg)

上图为专业详细信息展示功能的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class SpecialQuery(BaseModel):
    id: str
```

即为待查询专业的 id. 处理逻辑即通过 id 从 majorDetails 数据表中取出对应字段即可：

```python
@app.post("/getSpecialDetail")
async def get_special_detail(query: SpecialQuery):
    """
        获取专业详细信息
    """
    cnx = connect_sql()
    cursor = cnx.cursor()

    query_sql = ("SELECT * FROM majorDetails WHERE id = %s")
    data_sql = (query.id, )
    cursor.execute(query_sql, data_sql)
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    data = {
        "id": result[0],
        "name": result[1],
        "hot": result[2],
        "code": result[0],
        "year": result[3],
        "degree": result[4],
        "is_what": result[5],
        "learn_what": result[6],
        "do_what": result[7],
        "content": result[8],
        "recommend_subject": result[9],
        "postgraduate": result[10],
        "subject": result[11],
        "people": result[12],
        "Overall_satisfaction": result[13],      
        "EducationConditions_satisfaction": result[14],  
        "TeachingQuality_satisfaction": result[15], 
        "JobRate_satisfaction": result[16],  
        "salary_self": result[17],
        "salary_average": result[18],
        "Rate1": result[19],
        "Rate2": result[20],
        "Rate3": result[21],
        "Rate4": result[22],
        "Rate5": result[23],
        "Rate6": result[24],
        "Job1": result[25],
        "Job2": result[26],
        "Job3": result[27],
        "Job4": result[28],
        "Job5": result[29],
        "Job6": result[30],
        "rate1": result[31],
        "rate2": result[32],
        "rate3": result[33],
        "rate4": result[34],
        "rate5": result[35],
        "region1": result[36],
        "region2": result[37],
        "region3": result[38],
        "region4": result[39],
        "region5": result[40],
        "men_rate": result[41]
        }
```

##### 个性化志愿推荐功能

1. 系统推荐

![](./images/recommend_fastapi.jpg)

上图为志愿推荐功能的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class SchoolRecommend(BaseModel):
    type_: str
    score: int
    rank: int
    studentProvince: str
    risk: int
    province: str
    class_: int
```

分别为考生高考时的选科（物化生/物化政等）、分数、排名、所在省份、风险层次、学校所在省份、学校级别这些限制条件。

其处理逻辑为：**@褚效东 简单介绍一下**

```python
def subject_sort(subjects):
    order = {"物理": 1, "历史": 2, "化学": 3, "政治": 4, "生物": 5, "地理": 6, "技术": 7}
    if not all(subject in order.keys() for subject in subjects):
        raise ValueError()
    return sorted(subjects, key=lambda x: order.get(x, float('inf')))


def index_sim_search(province_name, choose_list, rank, type="高风险", school_province_name="",
                     is_double_first_class=False, is_985=False, is_211=False):
    con = mysql.connector.connect(
        host="192.168.80.190",
        port=3306,
        user="root",
        password="12345678",
        database="gaokao",
        use_pure=True,
        ssl_disabled=True
    )
    cursor = con.cursor()
    if type == "高风险":
        rank_min = int(max(rank - 20000 - rank * 0.1, 0))
        rank_max = rank
    elif type == "中风险":
        rank_min = int(max(rank - 10000 - rank * 0.1, 0))
        rank_max = int(rank + 10000 + rank * 0.1)
    else:
        rank_min = int(rank + rank * 0.1)
        rank_max = int(rank + 20000 + rank * 0.1)
    columns = ["school_name", "min_rank", "choose1", "choose2", "choose3"]
    choose_list = subject_sort(choose_list)
    rank_where = "min_rank >= {} and min_rank <= {}".format(rank_min, rank_max)
    where = []
    where.append("province_name = '{}'".format(province_name))
    if school_province_name != "" and school_province_name != "全部":
        where.append("school_province_name = '{}'".format(school_province_name))
    if is_double_first_class:
        where.append("is_dual_class = 1")
    if is_985:
        where.append("is_985 = 1")
    if is_211:
        where.append("is_211 = 1")
    if len(where) > 0:
        where = rank_where + " and " + " and ".join(where)
    else:
        where = rank_where
    q1 = "select {} from grade_sim_index where {}".format(",".join(columns), where)
    where = []
    where.append("choose1 is null or choose1=''")
    where.append("(choose1 = '{}' and (choose2 is null or choose2=''))".format(choose_list[2]))
    where.append(
        "(choose1 = '{}' and "
        "(choose2 is null or choose2='' or choose2='{}'))".format(choose_list[1], choose_list[2]))
    where.append("(choose1 = '{}' and "
                 "(choose2 is null or choose2='' or "
                 "(choose2='{}' and "
                 "(choose3 is null or choose3='' or choose3='{}')) or "
                 "(choose2='{}' and (choose3 is null or choose3=''))))".format(choose_list[0], choose_list[1],
                                                                               choose_list[2], choose_list[2]))

    q2 = "select school_name, avg(min_rank) as m from ({}) as t1 where {} GROUP BY school_name".\
        format(q1," or ".join(where))
    q = "select * from ({}) as t2 order by abs(m-{}) LIMIT 30".format(q2, rank)
    cursor.execute(q)
    results = cursor.fetchall()
    return results

@app.post("/recommend")
def recommend_school(school: SchoolRecommend):
    """
        个性化志愿推荐
    """
    subject_choice = school.type_.split(',')

    is985 = False
    is211 = False
    isDouble = False
    if school.class_ == 3:
        is985 = True
    elif school.class_ == 2:
        is211 = True
    elif school.class_ == 1:
        isDouble = True

    possible = ''
    if school.risk == 0:
        res = index_sim_search(school.studentProvince, subject_choice, school.rank, "低风险", school.province, isDouble, is985, is211)
        possible = '高'
    if school.risk == 1:
        res = index_sim_search(school.studentProvince, subject_choice, school.rank, "中风险", school.province, isDouble, is985, is211)
        possible = '中'
    if school.risk == 2:
        res = index_sim_search(school.studentProvince, subject_choice, school.rank, "高风险", school.province, isDouble, is985, is211)
        possible = '低'
    
    data = []
    for item in res:
        cnx = mysql.connector.connect(
            host="192.168.80.190",
            port=3306,
            user="root",
            password="12345678",
            database="gaokao",
            use_pure=True,
            ssl_disabled=True
        )
        cursor = cnx.cursor()
        query_sql = ("SELECT id, school_class FROM schoolBasic WHERE name = %s")
        data_sql = (item[0], )
        cursor.execute(query_sql, data_sql)
        result= cursor.fetchone()

        level = ''
        if result[1][0] == '1':
            level = '985 211 双一流'
        elif result[1][0] == '2' and len(result[1]) > 1:
            level = '211 双一流'
        elif result[1][0] == '2' and len(result[1]) == 1:
            level = '211'
        elif result[1][0] == '3':
            level = '双一流'

        school_choosen = {
            'id': result[0],
            'name': item[0],
            'level': level,
            'rank': int(item[1]),
            'possible': possible,
        }

        data.append(school_choosen)    

    return {
        'code': 200,
        'data': data,
        'page_total': 1,
    }
```

2. 填写志愿表

![](./images/addVolunteer_fastapi.jpg)

上图为向志愿表中填写数据的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class Volunteer(BaseModel):
    username: str
    name: str
    possible: str
```

分别为当前登录的用户名、待填入学校的名称和录取概率。

处理逻辑即为将这些信息传入数据库中：

```python
@app.post("/addselect")
def add_volunteer_table(volunteer: Volunteer):
    """
        向志愿表中添加数据
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    insert_query = "INSERT INTO volunteer (username, school, possible) VALUES (%s, %s, %s)"
    data = (volunteer.username, volunteer.name, volunteer.possible)
    cursor.execute(insert_query, data)
    cnx.commit()
    cursor.close()

    return {
        'code': 200,
        'message': ''
    }
```

3. 查看志愿表

![](./images/getVolunteer_fastapi.jpg)

上图为查看志愿表的 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class UserSelect(BaseModel):
    username: str
```

即为当前用户的用户名，处理逻辑即为根据当前用户名从数据库中取出其选择的大学及其录取概率。

```python
@app.post("/getselect")
def get_school_list(user: UserSelect):
    """
        获取志愿表中的数据
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    query_sql = ("SELECT school, possible FROM volunteer WHERE username = %s")
    data = (user.username, )
    cursor.execute(query_sql, data)
    results = cursor.fetchall()
    cursor.close()
    cnx.close()

    data = []
    for result in results:
        data.append({
            'name': result[0],
            'possible': result[1]
            })
        
    return {
        'code': 200,
        'data': data
    }
```

4. 删除志愿表

![](./images/deleteVolunteer_fastapi.jpg)

上图为查看志愿表的某一项 FastAPI 接口，为 POST 请求。

其请求体如下：

```python
class DelSelect(BaseModel):
    username: str
    name: str
```

即待删除志愿项的学校名称和当前用户的用户名，处理逻辑即为从数据库中删除该项：

```python
@app.post("/delselect")
def del_volunteer(delV: DelSelect):
    """
        删除志愿表中的数据
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    delete_sql = ("DELETE from volunteer WHERE username = %s and school = %s")
    data = (delV.username, delV.name)
    cursor.execute(delete_sql, data)
    cnx.commit()
    cursor.close()
    cnx.close()

    return {
        'code': 200,
        'message': '删除成功'
    }
```



### 大数据面板

##### 高考人数

![](./images/gaokaoNumber_fastapi.jpg)

上图为获取高考人数的 FastAPI 接口，为 GET 请求。

根据省份编码和年份获取到当年、当地的高考人数：

```python
@app.get("/adcode/{ad_code}/year/{year_}")
def get_score_by_province_and_year(ad_code: int, year_: int):
    """
        根据年份、省份获取高考人数
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    query_sql = ("SELECT exam_number FROM gaokao_number WHERE year = %s AND province = %s")
    data = (str(year_), adcodes.get(str(ad_code)))
    cursor.execute(query_sql, data)
    results = cursor.fetchone()
    cursor.close()
    cnx.close()

    if results != None:
        return results[0]
    else:
        return 0

```

##### 高考所选科目与可选择专业数目占比

![](./images/majorCount_fastapi.jpg)

上图为获取高考所选科目与可选择专业数目的 FastAPI 接口，为 GET 请求。

根据省份编码和年份获取到当年、当地考生高考所选科目与可选择专业数目，这里由于高考所选科目的组合数较多（C 73），因此存入 json 文件中：

```python
@app.get("/selectMajorCount/{year}/{province_id}")
def get_major_count(year: str, province_id: str):
    """
        高考所选科目与可选专业数目占比
    """
    with open('json/count_choose.json', 'r', encoding='utf-8') as f:
        data_josn = json.load(f)

    subjects = data_josn.get('data')

    res = data_josn.get(adcodes.get(province_id, ''), {})
    if res != {}:
        res = res.get(year, {})
    data = []
    if res != {}:
        for key, value in res.items():
            subject = subjects[int(key)]
            num = int(value)
            item = {
                'name': subject[0][0]+subject[1][0]+subject[2][0],
                'value': num
            }
            data.append(item)

    return {
        'code': 200,
        'data': data
    }
```

##### 知乎热词占比

![](./images/zhihuHot_fastapi.jpg)

上图为根据年份知乎热词占比的 FastAPI 接口，为 GET 请求。

根据年份获取到当年知乎热词占比，这里由于热词的内容、数目不统一，因此存入 json 文件中：

```python
@app.get("/zhihu_hot/{year}")
def get_zhihu_hot(year: int):
    """
        根据年份获取知乎热词占比
    """
    with open('json/zhihu_hot.json', 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    
    data = []
    for key, value in data_json[str(year)].items():
        data.append({
            'name': key,
            'value': int(value)
        })

    return {
        'code': 200,
        'data': data
    }
```

##### 高校类型分布

![](./images/schoolType_fastapi.jpg)

上图为根据省份获取当地高校类型占比的 FastAPI 接口，为 GET 请求。

```python
@app.get("/school_type/{abcode}")
def get_school_type_ratio(abcode: str):

    cnx = connect_sql()
    cursor = cnx.cursor()
    query_sql = ("SELECT num_985, num_211, num_double, benke, zhuanke FROM school_type WHERE province_id = %s")
    data = (abcode, )
    cursor.execute(query_sql, data)
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    return {
        "code": 200,
        "data": [
            {
                "name": "985",
                "value": result[0]
            },
            {
                "name": "211",
                "value": result[1]
            },
            {
                "name": "双一流",
                "value": result[2]
            },
            {
                "name": "本科",
                "value": result[3]
            },
            {
                "name": "专科",
                "value": result[4]
            }
        ]
    }
```

##### 一本上线率

![](./images/benkeRate_fastapi.jpg)

上图为根据年份、省份获取当年该地的一本上线率的 FastAPI 接口，为 GET 请求。

```python
@app.get("/benke_rate/{year}/{abcode}")
def get_benke_rate(year: str, abcode: str):
    """
        根据年份、省份获取当年该地的一本上线率
    """
    cnx = connect_sql()
    cursor = cnx.cursor()
    query_sql = ("SELECT benke_rate FROM benke_rate WHERE year = %s AND province_id = %s")
    data = (year, abcode)
    cursor.execute(query_sql, data)
    result = cursor.fetchone()
    cursor.close()
    cnx.close()

    return {
        'code': 200,
        'data': {
          'value': result[0]
        },
    }

```

