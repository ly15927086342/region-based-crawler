#coding = 'utf-8'
import requests
import time
import random
import threading
from queue import Queue
import logging
import os
import re
from csvIO import CsvIO
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
		self.entry = ''
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
		self.thread_pool = []
		self.MAX_ALERT_NUM = 10
		# 用于failList连续增加MAX_ALERT_NUM个则认为是被检测出异常，需要直接退出程序
		self.alert = 0

	def getEntryFunc(self,region):
		raise Exception("子类未重写getEntryFunc方法")

	def getPagesFunc(self,url):
		raise Exception("子类未重写getPagesFunc方法")

	def getLinkListFunc(self,url):
		raise Exception("子类未重写getLinkListFunc方法")

	def processLinksFunc(self,url):
		raise Exception("子类未重写processLinksFunc方法")

	def urlIsVaild(self,url):
		raise Exception("子类未重写urlIdValid方法")

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
				self.alert = self.alert + 1
				if(self.alert >= self.MAX_ALERT_NUM):
					self.logger.warn('反爬机制可能生效，请手动解决问题')
					print('反爬机制可能生效，请手动解决问题')
			else:
				self.alert = 0
				self.links.extend(res)

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
			self.thread_pool.append(t)
			time.sleep(self.timespan/self.thread_num)
		# 阻塞线程
		for thread in self.thread_pool:
			thread.join()
		self.thread_pool.clear()
		print('---getLinks end---')
		self.logger.info('getLinks finish')
		print('链接总数：'+str(len(self.links)))
		# 把所有链接先写入fail文件
		cur_list = self.failList + []
		for link in self.links:
			cur_list.append({
				'type':'links',
				'region':self.regions[self.id],
				'url':link
				})
		if(len(cur_list)>0):
			CsvIO().writeRows(self.dict_path+self.regions[self.id]+'_fail.csv',['type','region','url'],cur_list)

	def processLinks(self):
		while(not self.Task.empty()):
			url = self.Task.get()
			# 链接无效则直接跳过
			if(not self.urlIsVaild(url)):
				continue
			res = self.processLinksFunc(url)
			if(len(res)==0):
				self.failList.append({
					'type':'links',
					'region':self.regions[self.id],
					'url':url
					})
				print('['+str(len(self.failList)+len(self.susList))+']'+'fail:'+url)
				self.logger.warn('fail:' + url + ';type:links')
				self.alert = self.alert + 1
				if(self.alert >= self.MAX_ALERT_NUM):
					self.logger.warn('反爬机制可能生效，请手动解决问题')
					print('反爬机制可能生效，请手动解决问题')
			else:
				self.alert = 0
				field = dict()
				for i in range(0,len(self.fields)):
					field[self.fields[i]] = res[i]
				self.susList.append(field)
				print('['+str(len(self.failList)+len(self.susList))+']'+'sus:'+url)

	# 爬取完毕的回调
	def spideLinks(self,callback):
		print('---spideLinks start---')
		self.Task.queue.clear()
		# links推入任务队列
		for url in self.links:
			self.Task.put(url)
		# 多线程运算
		for i in range(0,self.thread_num):
			t = threading.Thread(target=self.processLinks)
			t.start()
			self.thread_pool.append(t)
			time.sleep(self.timespan/self.thread_num)
		for thread in self.thread_pool:
			thread.join()
		self.thread_pool.clear()
		print('---spideLinks end---')
		self.logger.info('spideLinks finish')
		self.onFinish(callback)

	def run(self):
		# 按区爬取所有待爬链接，存入fail文件
		for id in range(0,len(self.regions)):
			self.id = id
			print('---开始爬取'+self.regions[self.id]+'---')
			self.logger.info('开始爬取'+self.regions[self.id])
			# 已存在fail文件或已存在result文件则跳过
			if(os.path.exists(self.dict_path+self.regions[self.id]+'_fail.csv') or os.path.exists(self.dict_path+self.regions[self.id]+'_result.csv')):
				continue
			self.getEntry()
			self.getPages()
			self.getLinks()
			self.susList.clear()
			self.failList.clear()
			self.pages.clear()
			self.links.clear()
		self.reSpideFailLinks()

	def saveRes(self):
		res = True
		if(len(self.susList)>0):
			res = res and CsvIO().appendRows(self.dict_path+self.regions[self.id]+'_result.csv',self.fields,self.susList)
		if(len(self.failList)>0):
			res = res and CsvIO().writeRows(self.dict_path+self.regions[self.id]+'_fail.csv',['type','region','url'],self.failList)
		# failList为空，则删除fail文件
		else:
			if(os.path.exists(self.dict_path+self.regions[self.id]+'_fail.csv')):
				os.remove(self.dict_path+self.regions[self.id]+'_fail.csv')
		if(res == False):
			self.logger.error(self.regions[self.id]+'文件存储失败')

	# 出发回调函数执行
	def onFinish(self,callback):
		self.saveRes()
		print('-----------------分割线------------------')
		print('---成功总数：'+str(len(self.susList))+'---')
		print('---失败总数：'+str(len(self.failList))+'---')
		self.susList.clear()
		self.failList.clear()
		self.pages.clear()
		self.links.clear()
		print('---'+self.regions[self.id]+'爬取完毕---')
		self.logger.info(self.regions[self.id]+'爬取完毕')
		print('-----------------分割线------------------')
		self.id = self.id + 1
		callback()

	# 爬取文件夹内失败的链接，爬取成功会删除fail文件
	def reSpideFailLinks(self):
		self.id = 0
		self.regions.clear()
		print('---检查文件夹内的失败文件---')
		self.logger.info('检查文件夹内的失败文件')
		files = os.listdir(self.dict_path)
		self.DataStore = dict()
		for file in files:
			if(not re.search('_fail.csv',file)==None):
				reader = CsvIO().readRows(self.dict_path + file)
				if(reader == False):
					self.logger.info('文件读取失败')
					exit()
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
		time.sleep(self.timespan+random.random()*self.timespan/5)
		r = requests.get(url,timeout=10,headers={
			'User-Agent':random.choice(USER_AGENT)
			})
		# print(r.apparent_encoding)
		# r.encoding = r.apparent_encoding
		if r.status_code == 200:
			return r.text.replace(u'\xa0', u' ')
		else:
			return None