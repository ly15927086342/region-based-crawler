#coding = 'utf-8'
import requests
import time
import random
import threading
from queue import Queue

'''
采用模板方法模式，构建抽象爬虫框架类
'''
class AbstractSpiderFrame(object):
	def __init__(self, regions = [], fields = [], thread_num = 3):
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
		self.headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
		}
		self.Task = Queue()
		self.finish = False

	def getEntryFunc(self):
		raise Exception("子类未重写getEntryFunc方法")

	def getPagesFunc(self,url):
		raise Exception("子类未重写getPagesFunc方法")

	def getLinkListFunc(self):
		raise Exception("子类未重写getLinkListFunc方法")

	def processLinksFunc(self):
		raise Exception("子类未重写processLinksFunc方法")

	def getEntry(self):
		print('---getEntry start---')
		for region in self.regions:
			res = self.getEntryFunc(region)
			self.entry.append(res)
		print('---getEntry end---')

	def getPages(self):
		print('---getPages start---')
		for url in self.entry:
			res = self.getPagesFunc(url)
			self.pages.extend(res)
		print('---getPages end---')

	def getLinkList(self):
		while(not self.Task.empty()):
			url = self.Task.get()
			# 用户重写该解析方法
			res = self.getLinkListFunc(url)
			self.links.extend(res)
			self.pages.pop()

	def getLinks(self):
		print('---getLinks start---')
		self.Task.queue.clear()
		# pages推入任务队列
		for url in self.pages:
			self.Task.put(url)
		# 多线程运算
		for i in range(0,self.thread_num):
			t = threading.Thread(target=self.getLinkList)
			t.start()
		print('---getLinks end---')

	def processLinks(self):
		while(not self.Task.empty()):
			url = self.Task.get()
			self.processLinksFunc(url)

	def spideLinks(self):
		while(not len(self.pages) == 0):
			pass
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
		print('---spideLinks end---')
		self.onFinish()

	def run(self):
		print('---开始爬取'+self.regions[0]+'---')
		self.getEntry()
		self.getPages()
		self.getLinks()
		self.spideLinks()

	def getHtml(self,url):
		time.sleep(1+random.random())
		r = requests.get(url,headers=self.headers)
		# print(r.apparent_encoding)
		# r.encoding = r.apparent_encoding
		if r.status_code == 200:
			return r.text

	# 出发回调函数执行
	def onFinish(self):
		print('---'+self.regions[0]+'爬取完毕---')
		self.next(self.callbackParms['arr'],self.callbackParms['id'],self.callbackParms['field'])

	# 回调函数配置
	def callback(self,cb,arr,id,field):
		self.next = cb
		self.callbackParms = {
		'arr':arr,
		'id':id,
		'field':field
		}