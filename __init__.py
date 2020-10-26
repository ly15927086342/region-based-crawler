#coding = 'utf-8'

from chuzuSpider import *
from queue import Queue
import re

def next(arr,id,field):
	print(id,len(arr))
	if(id == len(arr)):
		return
	app = chuzuSpider([arr[id]],field,3)
	app.callback(next,arr,id+1,field)
	app.run()

# 主程序入口
if __name__ == '__main__':
	# region = ['hongshan','wuchang','jiangan','hanyang','jiangxia','jianghan','dongxihu','qiaokou','huangpo','whtkfq','whqingshanqu','caidian','xinzhouqu','hannan']
	test = ['hannan','xinzhouqu']
	field = ['title','price','unit','type','direction','decoration','community','subway','address','region','description']
	# 每个区实例化一个爬虫，
	next(test,0,field)