from pymongo import MongoClient
import pymongo

'''
定义一个类,专门用于操作MongoDB数据库
'''


class Mongo(object):

    def __init__(self):
        """初始化操作"""
        # 链接MongoDB的服务器
        self.client = MongoClient('mongodb://127.0.0.1:27017')
        # 获取要操作的集合
        self.collection = self.client['travel']['scenic']

    def save(self, data):
        # print(data)
        self.collection.save(data)

    def find_scenic_count(self, city):
        """获取城市景点的数量"""
        return self.collection.count({'city': city})

    def find_scenics(self, city_name, count=20):
        cursor = self.collection.find({'address': {'$regex': city_name}}, limit=count).\
            sort([('comments_num', pymongo.DESCENDING)])

        scenics = []
        for scenic in cursor:
            scenics.append(scenic)
        # print(scenics)
        return scenics


# 创建一个用于操作MongoDB数据库的单例对象.
mongo = Mongo()