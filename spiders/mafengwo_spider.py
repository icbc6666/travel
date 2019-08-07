import requests
from lxml import etree
import re
from db.mongodb import mongo

"""
1 准备url列表
2 遍历url列表,发送请求,获取响应
3 解析数据
4 保存数据
"""


class MaFengWoSpider(object):

    def __init__(self, city):
        self.city = city
        self.url_pattern = "http://www.mafengwo.cn/search/q.php?q="+city+"&p={}&t=pois&kt=1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }

    def get_url_list(self):
        # 获取url列表
        # 获取前20个页面的url
        url_list = []
        for i in range(1,21):
            url = self.url_pattern.format(i)
            url_list.append(url)
        return url_list

    def get_page_url(self, url):
        # 获取响应
        response = requests.get(url, headers=self.headers)
        # 返回响应的字符串数据
        return response.content.decode()

    def get_data(self, page):
        """解析页面数据"""
        # 把页面转换为element对象,在element上就可以使用xpath来提取数据

        element = etree.HTML(page)
        # 获取包含景点信息的标签的列表
        lis = element.xpath('//*[@id="_j_search_result_left"]/div/div/ul/li')
        # 定义列表存储数据
        data_list= []
        for li in lis:
            name = ''.join(li.xpath('./div/div[2]/h3//a/text()'))
            # print(name)
            item = {}
            if name.find('景点') == -1:
                # 跳出本次循环,后面的代码,继续下一次循环
                continue
            # 去掉标题中的景点
            item['name'] = name.replace('景点 - ', '')
            # print(item)
            # 获取景点的地址
            item['address'] = li.xpath('./div/div[2]/ul/li[1]/a//text()')[0]
            # print(item)
            comments_num = li.xpath('./div/div[2]/ul/li[2]/a//text()')[0]
            item['comments_num'] = int(re.findall('蜂评\((\d+)\)', comments_num)[0])
            travel_notes_num = li.xpath('./div/div[2]/ul/li[3]/a//text()')[0]
            item['travel_notes_num'] = int(re.findall('游记\((\d+)\)', travel_notes_num)[0])
            item['city'] = self.city
            # print(item)
            # 将数据添加带列表
            data_list.append(item)
            # print(data_list)
        return data_list

    def save_data(self, page_data):
        """保存数据"""
        for data in page_data:
            # 把景点名称,指定MongoDB的主键
            # print(data)
            data['_id'] = data['name']
            # 把数据保存到MongoDB中
            mongo.save(data)

    def run(self):
        """程序入口,逻辑核心"""
        # 准备url列表
        url_list = self.get_url_list()
        # 遍历列表发送请求,获取响应
        for url in url_list:
            page = self.get_page_url(url)
            # print(page)
            page_data = self.get_data(page)
            # 保存数据
            self.save_data(page_data)


if __name__ == "__main__":
    ms = MaFengWoSpider("广州")
    ms.run()