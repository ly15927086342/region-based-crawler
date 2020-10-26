#coding = 'utf-8'

from chuzuSpider import *
from queue import Queue
import re
import time
import random
import requests

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
	test = ['hannan']
	field = ['title','price','unit','type','area','direction','floor','decoration','community','subway','address','description']
	next(test,0,field)