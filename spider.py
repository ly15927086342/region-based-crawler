#coding = 'utf-8'
import requests
import time
import random
import threading
from queue import Queue
import csv
import logging
import os

'''
采用模板方法模式，构建抽象爬虫框架类
'''
class AbstractSpiderFrame(object):
	def __init__(self, regions = [], fields = [], thread_num = 3, dict_path = './'):
		self.id = 0
		# regions构成entry
		self.regions = regions
		# entry获取pages
		self.entry = []
		# pages获取links
		self.pages = []
		self.links = []
		# fields表示要存入数据库的所有字段
		self.fields = fields
		self.thread_num = thread_num
		self.dict_path = dict_path
		self.headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
		}
		self.Task = Queue()
		self.finish = False
		# 存爬取失败的url
		self.failList = []
		self.susList = []
		self.checkParms()

	def getEntryFunc(self):
		raise Exception("子类未重写getEntryFunc方法")

	def getPagesFunc(self,url):
		raise Exception("子类未重写getPagesFunc方法")

	def getLinkListFunc(self):
		raise Exception("子类未重写getLinkListFunc方法")

	def processLinksFunc(self):
		raise Exception("子类未重写processLinksFunc方法")

	# 检查线程数和文件夹路径参数
	def checkParms(self):
		if(self.thread_num > 5):
			raise Exception("线程数不能超过5")
		if(not self.dict_path[-1:]=='/'):
			self.dict_path = self.dict_path + '/'
		if(not os.path.exists(self.dict_path)):
			try:
				os.makedirs(self.dict_path)
			except:
				raise Exception("文件夹路径格式错误或非文件夹")
		# 日志配置
		handler = logging.FileHandler(self.dict_path+'log.txt',mode='a',encoding='utf-8')
		logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s',handlers=[handler])
		self.logger = logging.getLogger(__name__)

	def getEntry(self):
		print('---getEntry start---')
		self.entry = self.getEntryFunc(self.regions[self.id])
		print('---getEntry end---')
		self.logger.info('getEntry finish')

	def getPages(self):
		print('---getPages start---')
		self.pages.clear()
		res = self.getPagesFunc(self.entry)
		self.pages.extend(res)
		print('---getPages end---')
		self.logger.info('getPages finish')

	def getLinkList(self):
		while(not self.Task.empty()):
			url = self.Task.get()
			# 用户重写该解析方法
			res = self.getLinkListFunc(url)
			if(len(res)==0):
				self.logger.warn('fail:' + url + ';type:pages')
			else:
				self.links.extend(res)
			self.pages.pop()

	def getLinks(self):
		print('---getLinks start---')
		self.Task.queue.clear()
		# pages推入任务队列
		for url in self.pages:
			self.Task.put(url)
		self.links.clear()
		# 多线程运算
		for i in range(0,self.thread_num):
			t = threading.Thread(target=self.getLinkList)
			t.start()

	def processLinks(self):
		while(not self.Task.empty()):
			url = self.Task.get()
			res = self.processLinksFunc(url)
			if(len(res)==0):
				self.failList.append({
					'type':'links',
					'region':self.regions[self.id],
					'url':url
					})
				print('fail:'+url)
				self.logger.warn('fail:' + url + ';type:links')
			else:
				field = dict()
				for i in range(0,len(self.fields)):
					field[self.fields[i]] = res[i]
				self.susList.append(field)
			self.links.pop()

	def spideLinks(self):
		while(not len(self.pages) == 0):
			pass
		print('---getLinks end---')
		self.logger.info('getLinks finish')
		print('链接总数：'+str(len(self.links)))
		print('---spideLinks start---')
		self.Task.queue.clear()
		# links推入任务队列
		for url in self.links:
			self.Task.put(url)
		# 多线程运算
		for i in range(0,self.thread_num):
			t = threading.Thread(target=self.processLinks)
			t.start()
		while(not len(self.links) == 0):
			pass
		print('---spideLinks end---')
		self.logger.info('spideLinks finish')
		self.onFinish()

	def run(self):
		if(self.id==len(self.regions)):
			return
		print('---开始爬取'+self.regions[self.id]+'---')
		self.logger.info('开始爬取'+self.regions[self.id])
		self.getEntry()
		self.getPages()
		self.getLinks()
		self.spideLinks()

	def saveRes(self):
		try:
			with open(self.dict_path+self.regions[self.id]+'_result.csv', 'a', newline='',encoding='utf-8') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames=self.fields)
				writer.writeheader()
				writer.writerows(self.susList)
				csvfile.close()
			with open(self.dict_path+self.regions[self.id]+'_fail.csv', 'w', newline='',encoding='utf-8') as failfile:
				writer = csv.DictWriter(failfile, fieldnames=['type','region','url'])
				writer.writeheader()
				writer.writerows(self.failList)
				failfile.close()
		except:
			self.logger.error(self.regions[self.id]+'文件存储失败')

	# 出发回调函数执行
	def onFinish(self):
		self.saveRes()
		print('---'+self.regions[self.id]+'爬取完毕---')
		print('---成功总数：'+str(len(self.susList))+'---')
		print('---失败总数：'+str(len(self.failList))+'---')
		print('-----------------分割线------------------')
		self.logger.info(self.regions[self.id]+'爬取完毕')
		self.id = self.id + 1
		self.run()

	def getHtml(self,url):
		# 控制爬取速度，防止被封
		time.sleep(5+random.random()*5)
		r = requests.get(url,headers=self.headers)
		# print(r.apparent_encoding)
		# r.encoding = r.apparent_encoding
		if r.status_code == 200:
			return r.text