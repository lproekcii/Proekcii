from math import pi, sin, cos
import copy

class Block():
	def __init__(self, parent, params="", btype=1):
		self.parent = parent
		if (params==""):
			self.name = ""
			self.btype = btype
			self.sdvig = self.parent.blockTypes[self.btype].sdvig
			self.chuvstv = 0
			self.size = [
							self.parent.blockTypes[self.btype].l1,
							self.parent.blockTypes[self.btype].l2,
							self.parent.blockTypes[self.btype].l3
						]
			self.coord = [0,0,0]
			self.ugol = [0,0,0]

		else:
			st = params.split(";")
			self.name = st[0]
			try:
				self.sdvig = int(st[1])
			except:
				self.sdvig = 0

			try:
				self.btype = int(st[2])
			except:
				self.btype = 1

			try:
				self.chuvstv = int(st[3])
			except:
				self.chuvstv = 0

			self.size = [0,0,0]
			try:
				self.size[0] = int(st[4])
			except:
				self.size[0] = 0

			try:
				self.size[1] = int(st[5])
			except:
				self.size[1] = 0

			try:
				self.size[2] = int(st[6])
			except:
				self.size[2] = 0

			self.coord = [0,0,0]
			try:
				self.coord[0] = int(st[7])
			except:
				self.coord[0] = 0

			try:
				self.coord[1] = int(st[8])
			except:
				self.coord[1] = 0

			try:
				self.coord[2] = int(st[9])
			except:
				self.coord[2] = 0

			self.ugol = [0,0,0]
			try:
				self.ugol[0] = int(st[10])
			except:
				self.ugol[0] = 0

			try:
				self.ugol[1] = int(st[11])
			except:
				self.ugol[1] = 0

			try:
				self.ugol[2] = int(st[12])
			except:
				self.ugol[2] = 0

		self.points = [Point(0,0,0) for i in xrange(8)]
		self.setPoints()

	def toStr(self):
		st = "block:"
		st += (self.name + ";" +
				str(self.sdvig) + ";" +
				str(self.btype) + ";" +
				str(self.chuvstv) + ";"+
				str(self.size[0]) + ";"+
				str(self.size[1]) + ";"+
				str(self.size[2]) + ";"+
				str(self.coord[0]) + ";"+
				str(self.coord[1]) + ";"+
				str(self.coord[2]) + ";"+
				str(self.ugol[0]) + ";"+
				str(self.ugol[1]) + ";"+
				str(self.ugol[2]) + ";")
		return st

	def setPoints(self):
		self.points[0].c[0] = self.sdvig - self.size[0]
		self.points[0].c[1] = -0.5*self.size[1]
		self.points[0].c[2] = -self.size[2]

		self.points[1].c[0] = self.sdvig
		self.points[1].c[1] = -0.5*self.size[1]
		self.points[1].c[2] = -self.size[2]

		self.points[2].c[0] = self.sdvig - self.size[0]
		self.points[2].c[1] = 0.5*self.size[1]
		self.points[2].c[2] = -self.size[2]

		self.points[3].c[0] = self.sdvig
		self.points[3].c[1] = 0.5*self.size[1]
		self.points[3].c[2] = -self.size[2]

		self.points[4].c[0] = self.sdvig - self.size[0]
		self.points[4].c[1] = -0.5*self.size[1]
		self.points[4].c[2] = 0

		self.points[5].c[0] = self.sdvig
		self.points[5].c[1] = -0.5*self.size[1]
		self.points[5].c[2] = 0

		self.points[6].c[0] = self.sdvig - self.size[0]
		self.points[6].c[1] = 0.5*self.size[1]
		self.points[6].c[2] = 0

		self.points[7].c[0] = self.sdvig
		self.points[7].c[1] = 0.5*self.size[1]
		self.points[7].c[2] = 0

		alphax = self.ugol[0]*pi/180
		alphay = self.ugol[1]*pi/180
		alphaz = self.ugol[2]*pi/180

		if (alphax*alphax + alphay*alphay + alphaz*alphaz > 0):
			#delaem povoroty
			buf = Point()

			#povorot alphax
			for i in xrange(8):
				buf.c[0] = self.points[i].c[0]*1
				buf.c[1] = self.points[i].c[1]*cos(alphax) - self.points[i].c[2]*sin(alphax)
				buf.c[2] = self.points[i].c[1]*sin(alphax) + self.points[i].c[2]*cos(alphax)
				self.points[i] = copy.deepcopy(buf)

			#povorot alphay
			for i in xrange(8):
				buf.c[0] = self.points[i].c[0]*cos(alphay) + self.points[i].c[2]*sin(alphay)
				buf.c[1] = self.points[i].c[1]*1
				buf.c[2] = -self.points[i].c[0]*sin(alphay) + self.points[i].c[2]*cos(alphay)
				self.points[i] = copy.deepcopy(buf)

			#povorot alphaz
			for i in xrange(8):
				buf.c[0] = self.points[i].c[0]*cos(alphaz) - self.points[i].c[1]*sin(alphaz)
				buf.c[1] = self.points[i].c[0]*sin(alphaz) + self.points[i].c[1]*cos(alphaz)
				buf.c[2] = self.points[i].c[2]*1
				self.points[i] = copy.deepcopy(buf)

		#a terb sdvinem vse
		for i in xrange(8):
			for j in xrange(3):
				self.points[i].c[j] += self.coord[j]

class Source():
	def __init__(self, parent, params=""):
		self.parent = parent
		if (params==""):
			self.name = ""
			self.akt = 0
			self.coord = [0,0,0]

		else:
			st = params.split(";")
			self.name = st[0]

			try:
				self.akt = int(st[3])
			except:
				self.akt = 0

			self.coord = [0,0,0]
			try:
				self.coord[0] = int(st[7])
			except:
				self.coord[0] = 0

			try:
				self.coord[1] = int(st[8])
			except:
				self.coord[1] = 0

			try:
				self.coord[2] = int(st[9])
			except:
				self.coord[2] = 0

	def toStr(self):
		st = "sourc:"
		st += (
				self.name + ";" +
				str(self.akt) + ";"+
				str(self.coord[0]) + ";"+
				str(self.coord[1]) + ";"+
				str(self.coord[2]) + ";"
				)
		return st

class BlockType():
	def __init__(self, parent):
		self.name="zero"
		self.l1=0
		self.l2=0
		self.l3=0
		self.sdvig=0
		self.r1=0
		self.r2=0
		self.otst=0

class Point():
	def __init__(self, x=0,y=0,z=0):
		self.c = [x,y,z]

class BestPoints():
	def __init__(self, x=0,y=0,z=0):
		self.c = [x,y,z]
		self.data = []
		self.best = -1  #max
		self.worst = -1
