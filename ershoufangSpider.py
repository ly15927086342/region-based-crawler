#coding = 'utf-8'

import json
from lxml import etree
from bs4 import BeautifulSoup
import math
import sqlite3
import re
from spider import AbstractSpiderFrame

'''
模板方法模式，
继承AbstractSpiderFrame的子类，重写部分方法
'''
class ershoufangSpider(AbstractSpiderFrame):
	def __init__(self, regions = [], fields = [], thread_num = 3,dict_path = './',timespan = 10):
		super(ershoufangSpider, self).__init__(regions,fields,thread_num,dict_path,timespan)

	# @parms{region}: self.regions[i]
	# @return{childLink}：根据区域生成待爬取的主页链接
	def getEntryFunc(self,region):
		return 'https://wh.58.com/'+region+'/ershoufang/'

	# @parms{url}: self.entry[i]
	# @return{childLink}：self.entry[i]页获取的所有列表页的链接list
	def getPagesFunc(self,url):
		pg = []
		try:
			res = self.getHtml(url)
			soup = BeautifulSoup(res,'lxml')
			page = soup.find_all(class_='pager')[0]
			a = page.find_all('a')
			maxP = int(a[len(a)-2].find('span').string)
			for i in range(1,maxP+1):
				pg.append(url+'pn'+str(i)+'/')
		except:
			pass
		return pg

	# @parms{url}: self.pages[i]
	# @return{childLink/False}： self.pages[i]页所有待爬页面的链接list，如果页面异常，返回False
	def getLinkListFunc(self,url):
		try:
			res = self.getHtml(url)
			soup = BeautifulSoup(res,'lxml')
			childLink = []
			domItem = soup.find(class_='house-list-wrap').find_all(class_='list-info')
			for dom in domItem:
				link = dom.find(class_='title').find('a').get('href')
				# //开头转http://
				if(re.match(r'https:',link)==None):
					link = 'https:'+link
				# ?后面的参数都舍弃
				link = link.split('?')[0]
				childLink.append(link)
			return childLink
		except:
			return False

	# @parms{url}: self.links[i]
	# @return{record}: 和self.fields顺序必须保持一致，返回一个list，该list会写入csv
	# 详情页的爬取处理函数
	def processLinksFunc(self,url):
		record = []
		try:
			res = self.getHtml(url)
			soup = BeautifulSoup(res,'lxml')
			title = soup.find(class_='house-title').find('h1').string.strip()
			situation = soup.find(id='generalSituation')
			situation_left = situation.find(class_='general-item-left').find_all('li')
			situation_right = situation.find(class_='general-item-right').find_all('li')
			style = situation_left[1].find_all('span')[1].string
			toward = situation_left[3].find_all('span')[1].string
			new = situation_left[4].find_all('span')[1].string
			floor = situation_right[0].find_all('span')[1].string
			decoration = situation_right[1].find_all('span')[1].string
			expires = situation_right[2].find_all('span')[1].string
			build_date = situation_right[3].find_all('span')[1].string

			desc = soup.find(id='generalDesc').find(class_='general-pic-desc')
			key_desc = desc[0].find(class_='pic-desc-word').get_text('|').strip().replace(' ','')
			owner_mind = desc[1].find(class_='pic-desc-word').get_text('|').strip().replace(' ','')
			serve_desc = desc[2].find(class_='pic-desc-word').get_text('|').strip().replace(' ','')

			loc = re.search(r'____json4fe={(.*?)};',res.replace(' ','').replace('\n','')).group(0)
			locObj = demjson.decode(loc)
			baidulat = locObj['xiaoqu']['baidulat']
			baidulon = locObj['xiaoqu']['baidulon']
			lat = locObj['xiaoqu']['lat']
			lon = locObj['xiaoqu']['lon']
			community = locObj['xiaoqu']['name']
			price = locObj['price']
			area = locObj['area']

			record = [url,title,price,area,style,toward,new,floor,decoration,expires,build_date,community,baidulat,baidulon,lat,lon,key_desc,owner_mind,serve_desc]
			print(record)
		except:
			pass
		return record
