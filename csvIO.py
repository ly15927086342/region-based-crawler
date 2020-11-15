#coding = 'utf-8-sig'

import csv
import os

'''
function lists:
1. 追加行
2. 删除行
3. 读取文件
4. 重写文件
5. 追加多行
6. 删除多行
'''

class  CsvIO(object):
	"""docstring for  FileIO"""
	def __init__(self):
		super(CsvIO, self).__init__()

	def getField(self,filename):
		fields = None
		try:
			with open(filename, 'r', newline='',encoding='utf-8-sig') as csvfile:
				reader = csv.DictReader(csvfile)
				fields = reader.fieldnames
				csvfile.close()
		except:
			pass
		return fields

	def hasField(self,filename):
		hasHead = False if self.getField(filename) == None else True
		return hasHead

	def appendRow(self,filename,fields,data):
		try:
			hasHead = self.hasField(filename)
			with open(filename, 'a', newline='',encoding='utf-8-sig') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames=fields)
				if(not hasHead):
					writer.writeheader()
				writer.writerow(data)
				csvfile.close()
			return True
		except:
			return False

	def appendRows(self,filename,fields,data):
		try:
			hasHead = self.hasField(filename)
			with open(filename, 'a', newline='',encoding='utf-8-sig') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames=fields)
				if(not hasHead):
					writer.writeheader()
				writer.writerows(data)
				csvfile.close()
			return True
		except:
			return False

	def readRows(self,filename):
		res = []
		try:
			with open(filename, newline='',encoding='utf-8-sig') as csvfile:
				reader = csv.DictReader(csvfile)
				for row in reader:
					res.append(row)
				csvfile.close()
			return res
		except:
			return False

	def writeRows(self,filename,fields,data):
		try:
			with open(filename, 'w', newline='',encoding='utf-8-sig') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames=fields)
				writer.writeheader()
				writer.writerows(data)
				csvfile.close()
			return True
		except:
			return False

	def deleteLastRow(self,filename,fields):
		rows = self.readRows(filename)
		if(rows == False):
			return False
		rows.pop()
		return self.writeRows(filename,fields,rows)

	def deleteLastRows(self,filename,row,fields):
		rows = self.readRows(filename)
		if(rows == False):
			return False
		del rows[-row:]
		return self.writeRows(filename,fields,rows)