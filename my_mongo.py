from config import my_config
from pymongo import MongoClient

# 链接MongoDB
mongo_url = ('mongodb://' +
             my_config["mongo_user"] + ':' +
             my_config["mongo_password"] + '@' +
             my_config["mongo_host"])
client = MongoClient(
    host=mongo_url,
    maxPoolSize=50,  # 最大连接池数量
    connectTimeoutMS=6000000,  # 连接超时时间
    socketTimeoutMS=6000000,  # 套接字超时时间
)


def init_database():
    """
    初始化数据库
    请注意，MongoDB并不一定需要提前创建数据库，此处的操作是为了方便理解和演示
    此外，该函数也可用于检测MongoDB是否正确安装和配置
    """
    # 选择数据库，数据库名为gaokao
    db = client.gaokao
    return db


init_database()


def get_id_dict(collection_name):
    """
    获取数据库中的id字典
    :param collection_name: 数据库中的集合名
    :return: id字典
    """
    id_dict = None
    try:
        id_1 = client.gaokao[collection_name].find({}, {"id": 1, "name": 1})
        id_dict = {i["id"]: i["name"] for i in id_1}
        id_dict = dict(sorted(id_dict.items(), key=lambda x: x[0]))
    except Exception as e:
        print(e)
    return id_dict


school_id = get_id_dict("school_id")
province_id = get_id_dict("province_id")


# if __name__ == "__main__":
#     input("此操作将删除数据库中所有数据，是否继续？")
#     client.drop_database("gaokao")
#     init_database()
