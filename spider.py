#coding = 'utf-8'

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

	def getEntry(self):
		raise Exception("子类未重写getEntry方法")

	def getPages(self):
		raise Exception("子类未重写getPages方法")

	def getLinks(self):
		raise Exception("子类未重写getLinks方法")

	def spideLinks(self):
		raise Exception("子类未重写spideLinks方法")

	def run(self):
		print('---开始爬取'+self.regions[0]+'---')
		self.getEntry()
		self.getPages()
		self.getLinks()
		self.spideLinks()