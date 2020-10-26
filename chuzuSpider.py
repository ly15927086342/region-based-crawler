#coding = 'utf-8'

import requests
import json
from lxml import etree
from bs4 import BeautifulSoup
import time
import random
import math
import threading
import sqlite3
import re
from queue import Queue
from spider import AbstractSpiderFrame

'''
模板方法模式，
继承AbstractSpiderFrame的子类，重写部分方法
'''
class chuzuSpider(AbstractSpiderFrame):
	def __init__(self, regions = [], fields = [], thread_num = 3):
		super(chuzuSpider, self).__init__(regions,fields,thread_num)
		self.headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
		}
		self.Task = Queue()
		self.finish = False

	def getHtml(self,url):
		time.sleep(1+random.random())
		r = requests.get(url,headers=self.headers)
		# print(r.apparent_encoding)
		# r.encoding = r.apparent_encoding
		if r.status_code == 200:
			return r.text

	def getEntry(self):
		print('---getEntry start---')
		for region in self.regions:
			self.entry.append('http://wh.ganji.com/'+region+'/zufang/')
		print('---getEntry end---')

	def getPages(self):
		print('---getPages start---')
		for url in self.entry:
			res = self.getHtml(url)
			soup = BeautifulSoup(res,'lxml')
			page = soup.find_all(class_='pageBox')[1]
			a = page.find_all('a')
			maxP = int(a[len(a)-2].find('span').string)
			for i in range(1,maxP+1):
				self.pages.append(url+'pn'+str(i)+'/')
		print('---getPages end---')

	def getLinkList(self):
		while(not self.Task.empty()):
			url = self.Task.get()
			res = self.getHtml(url)
			soup = BeautifulSoup(res,'lxml')
			try:
				domItem = soup.find_all(class_='ershoufang-list')
				for dom in domItem:
					link = dom.find(class_='title').find('a').get('href')
					# //开头转http://
					if(re.match(r'http:',link)==None):
						link = 'http:'+link
					# ?后面的参数都舍弃
					link = link.split('?')[0]
					self.links.append(link)
				self.pages.pop()
			except:
				print('err: '+url)

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

	def spideLinks(self):
		while(not len(self.pages) == 0):
			pass
		print('链接总数：'+str(len(self.links)))

		print('---spideLinks start---')

		print('---spideLinks end---')
		self.onFinish()

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
