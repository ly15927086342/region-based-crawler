#coding = 'utf-8'
import requests
import time
import random
import threading
from queue import Queue
import csv
import logging
import os
import re
from user_agent_list import USER_AGENT

'''
采用模板方法模式，构建抽象爬虫框架类
'''
class AbstractSpiderFrame(object):

	def __init__(self, regions = [], fields = [], thread_num = 3, dict_path = './',timespan = 10):
		self.id = 0
		# regions构成entry
		self.regions = regions
		# entry获取pages
		self.entry = []
		# pages获取links
		self.pages = []
		self.links = []
		# 存爬取失败的url
		self.failList = []
		self.susList = []
		# fields表示要存入数据库的所有字段
		self.fields = fields
		self.thread_num = thread_num
		self.dict_path = dict_path
		self.timespan = timespan
		self.Task = Queue()
		self.finish = False
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
			if(res == False):
				self.failList.append({
					'type':'pages',
					'region':self.regions[self.id],
					'url':url
					})
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
		# 多线程运算
		for i in range(0,self.thread_num):
			t = threading.Thread(target=self.getLinkList)
			t.start()
			time.sleep(self.timespan/self.thread_num)

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
				print('sus:'+url)
				field = dict()
				for i in range(0,len(self.fields)):
					field[self.fields[i]] = res[i]
				self.susList.append(field)
			self.links.pop()

	# 爬取完毕的回调
	def spideLinks(self,callback):
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
			time.sleep(self.timespan/self.thread_num)
		while(not len(self.links) == 0):
			pass
		print('---spideLinks end---')
		self.logger.info('spideLinks finish')
		self.onFinish(callback)

	def run(self):
		if(self.id==len(self.regions)):
			return
		print('---开始爬取'+self.regions[self.id]+'---')
		self.logger.info('开始爬取'+self.regions[self.id])
		self.getEntry()
		self.getPages()
		self.getLinks()
		self.spideLinks(self.run)

	def saveRes(self):
		try:
			if(len(self.susList)>0):
				hasHead = False
				# 行数为0或报错表示无头部，需要写头
				try:
					with open(self.dict_path+self.regions[self.id]+'_result.csv', 'r', newline='',encoding='utf-8') as csvfile:
						reader = csv.reader(csvfile)
						length = 0
						for row in reader:
							length = length + 1
						if(length>0):
							hasHead = True
						csvfile.close()
				except:
					pass
				with open(self.dict_path+self.regions[self.id]+'_result.csv', 'a', newline='',encoding='utf-8') as csvfile:
					writer_sus = csv.DictWriter(csvfile, fieldnames=self.fields)
					if(not hasHead):
						writer_sus.writeheader()
					writer_sus.writerows(self.susList)
					csvfile.close()
				self.susList.clear()
			if(len(self.failList)>0):
				with open(self.dict_path+self.regions[self.id]+'_fail.csv', 'w', newline='',encoding='utf-8') as failfile:
					writer_fail = csv.DictWriter(failfile, fieldnames=['type','region','url'])
					writer_fail.writeheader()
					writer_fail.writerows(self.failList)
					failfile.close()
				self.failList.clear()
			# failList为空，则删除fail文件
			else:
				if(os.path.exists(self.dict_path+self.regions[self.id]+'_fail.csv')):
					os.remove(self.dict_path+self.regions[self.id]+'_fail.csv')
		except:
			self.logger.error(self.regions[self.id]+'文件存储失败')

	# 出发回调函数执行
	def onFinish(self,callback):
		self.saveRes()
		self.entry.clear()
		self.pages.clear()
		self.links.clear()
		print('---'+self.regions[self.id]+'爬取完毕---')
		print('---成功总数：'+str(len(self.susList))+'---')
		print('---失败总数：'+str(len(self.failList))+'---')
		print('-----------------分割线------------------')
		self.logger.info(self.regions[self.id]+'爬取完毕')
		self.id = self.id + 1
		callback()

	# 爬取文件夹内失败的链接，爬取成功会删除fail文件
	def reSpideFailLinks(self):
		self.regions.clear()
		print('---检查文件夹内的失败文件---')
		self.logger.info('检查文件夹内的失败文件')
		files = os.listdir(self.dict_path)
		self.DataStore = dict()
		for file in files:
			if(not re.search('_fail.csv',file)==None):
				with open(self.dict_path + file, newline='',encoding='utf-8') as csvfile:
					reader = csv.DictReader(csvfile)
					for row in reader:
						if(self.DataStore.get(row['region'])==None):
							self.DataStore[row['region']] = {
							'pages':[],
							'links':[]
							}
							if(row['type']=='pages'):
								self.DataStore[row['region']]['pages'] = [row['url']]
							elif(row['type']=='links'):
								self.DataStore[row['region']]['links'] = [row['url']]
						else:
							if(row['type']=='pages'):
								self.DataStore[row['region']]['pages'].append(row['url'])
							elif(row['type']=='links'):
								self.DataStore[row['region']]['links'].append(row['url'])
					csvfile.close()
		for key in self.DataStore:
			self.regions.append(key)
		self.logger.info('共有'+str(len(self.regions))+'个区数据待爬')
		self.reRun()

	def reRun(self):
		if(self.id==len(self.regions)):
			return
		print('---开始爬取'+self.regions[self.id]+'---')
		self.logger.info('开始爬取'+self.regions[self.id])
		self.preSetParms()
		self.getLinks()
		self.spideLinks(self.reRun)

	def preSetParms(self):
		self.pages = self.DataStore[self.regions[self.id]]['pages']
		self.links = self.DataStore[self.regions[self.id]]['links']

	def getHtml(self,url):
		# 控制爬取速度，防止被封
		time.sleep(self.timespan)
		r = requests.get(url,headers={
			'User-Agent':USER_AGENT[int(random.random()*len(USER_AGENT))]
			})
		# print(r.apparent_encoding)
		# r.encoding = r.apparent_encoding
		if r.status_code == 200:
			return r.text
		else:
			return None