#coding = 'utf-8'

from chuzuSpider import *
import csv

# 线程数
THREAD_MAX = 3

# 文件夹相对路径
DICT_PATH = './result'

# 主程序入口
if __name__ == '__main__':
	region = ['xinzhouqu','hannan','hongshan','wuchang','jiangan','hanyang','jiangxia','jianghan','dongxihu','qiaokou','huangpo','whtkfq','whqingshanqu','caidian']
	field = ['title','price','unit','type','area','direction','floor','decoration','community','subway','address','bdlat','bdlng','description']
	app = chuzuSpider(region,field,THREAD_MAX,DICT_PATH)
	app.run()