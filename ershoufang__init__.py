#coding = 'utf-8'

from ershoufangSpider import *
import demjson
import requests
import random
from user_agent_list import USER_AGENT
from lxml import etree
from bs4 import BeautifulSoup
import re

# 线程数
THREAD_MAX = 3

# 时间间隔（秒）
TIMESPAN = 18

# 文件夹相对路径
DICT_PATH = './result_ershoufang'

# 主程序入口
if __name__ == '__main__':
	region = ['xinzhouqu','hannan','hongshan','wuchang','jiangan','hanyang','jiangxia','jianghan','dongxihu','qiaokou','huangpo','whtkfq','whqingshanqu','caidian']
	field = ['url','title','price','area','style','toward','new','floor','decoration','expires','build_date','community','baidulat','baidulon','lat','lon','key_desc','owner_mind','serve_desc']
	
	# 爬取指定区域的页面
	app = ershoufangSpider(regions = region,
		fields = field,
		thread_num = THREAD_MAX,
		dict_path = DICT_PATH,
		timespan = TIMESPAN)
	app.run()
	
	# 对爬取失败的文件重爬，和app.run()不能顺序执行，因为两个函数都是异步函数
	# app.reSpideFailLinks()