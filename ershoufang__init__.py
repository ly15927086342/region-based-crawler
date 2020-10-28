#coding = 'utf-8'

from ershoufangSpider import *

# 线程数
THREAD_MAX = 3

# 时间间隔（秒）
TIMESPAN = 15

# 文件夹相对路径
DICT_PATH = './result_ershoufang'

# 主程序入口
if __name__ == '__main__':
	region = ['xinzhouqu','hannan','hongshan','wuchang','jiangan','hanyang','jiangxia','jianghan','dongxihu','qiaokou','huangpo','whtkfq','whqingshanqu','caidian']
	field = ['title','price','unit','type','area','direction','floor','decoration','community','subway','address','bdlat','bdlng','description']
	
	# 爬取指定区域的页面
	app = ershoufangSpider(regions = region,
		fields = field,
		thread_num = THREAD_MAX,
		dict_path = DICT_PATH,
		timespan = TIMESPAN)
	app.run()
	
	# 对爬取失败的文件重爬，和app.run()不能顺序执行，因为两个函数都是异步函数
	appR = chuzuSpider(regions = [],
		fields = field,
		thread_num = THREAD_MAX,
		dict_path = DICT_PATH,
		timespan = TIMESPAN)
	appR.reSpideFailLinks()