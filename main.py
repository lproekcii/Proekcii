# -*- coding: utf-8 -*- 

# from wx.lib.pubsub import Publisher
#sys.path.append("modules")
import sys
import wx
import time
import subThread
import toolBar
import panels
import EnhancedStatusBar as ESB
import entity

#pyinstaller --onefile --icon=ico\p1.ico --noconsole main.py

#TODO poigratsya s path chtobi ostavit moduli v modulyah
#TODO sdelat chelovecheskie oshibki esli ne nashli kakoi to fail
#TODO pohodu im nujna budet pechat i sootvetstvenno razmeri
#TODO v 2d narisovat liniy gde prohodit ploskost rascheta
#TODO polosa zagruzki nekorektno otobrajaet
#TODO* uznat ogranicheniya na pamyat i realizovat bolee nadejny algoritm
#TODO* sdelat bloki detalizovannymi

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title=u"Проекции", size=(1024, 768), pos=(150,100))
		self.SetIcon(wx.IconFromLocation(wx.IconLocation(r'ico/p1.ico')))

		# 4 razmera vidim oblst
		self.cenx = 0
		self.ceny = 0
		self.cenz = 0
		self.cens = 1
		# 3 + 3 solu oblst
		self.scenx = 0
		self.sceny = 0
		self.scenz = 0
		self.ssizex = 100
		self.ssizey = 100
		self.ssizez = 100
		self.soluType = 3			#2d/3d
		#self.soluMethod = 0       #int/mcnp/roma
		self.blocks = []
		self.sources = []
		self.blockTypes = []
		self.bestPoints = []
		self.combo = []#subThread.getCombo(len(self.parent.blocks))
		#self.bestPoints.append(entity.BestPoints(10,10,10))
		#self.bestPoints.append(entity.BestPoints(12,12,12))
		#self.bestPoints.append(entity.BestPoints(30,30,30))
		#self.bestPoints.append(entity.BestPoints(40,40,40))
		self.readTypes()
		self.curType=1
		self.fileName = ""
		self.worked = True
		self.nx = 20
		self.ny = 20
		self.nz = 20
		self.mnx = 20	#dlya writemesh
		self.mny = 20
		self.mnz = 20
		self.curBestPoint = -1
		self.kvantil = -1
		self.fon = -1
		self.vremya = -1

		# blocks.append(entity.Block(self))
		# blocks.append(entity.Block(self))
		# blocks[0].name = "ccc1"
		# blocks[1].name = "ccc2"
		# print blocks[0].name, blocks[1].name

		sizerMain = wx.BoxSizer( wx.VERTICAL )           #sozdali glavnyi sizer v kotoryi vlojili tool bar i vse ostalnoe
		self.tBar = toolBar.CreateToolBar(self)          #sozdali toolbar
		sizerContent = wx.GridSizer( 0, 2, 0, 0 )        #sozdali sizer dlya content
		sizerSetPanels = wx.BoxSizer( wx.VERTICAL )      #sozdali sizer dlya panelei na set paneli
		self.panelXZ = panels.PanelGraph(self, myid=0)   #sozdali panel
		self.panelYZ = panels.PanelGraph(self, myid=1)
		self.panelXY = panels.PanelGraph(self, myid=2)
		self.panelSet = panels.PanelSet(self)           #panel set na kotoroi budut knopki pereklucheniya na druguy panel
		self.curPanel = 0
		self.panelBlocks = panels.PanelBlocks(self)     #panel nastroiki blokov
		self.panelBlocks.Hide()
		self.panelSources = panels.PanelSources(self)   #panel nastroiki istochnikov
		self.panelSources.Hide()
		self.panelArea = panels.PanelArea(self)         #panel nastroiki oblasti
		self.panelArea.Hide()
		self.panelSolution = panels.PanelSolution(self) #panel nastroiki vychisleni
		self.panelSolution.Hide()

		sizerSetPanels.Add( self.panelSet, 1, wx.EXPAND )
		sizerSetPanels.Add( self.panelBlocks, 1, wx.EXPAND )
		sizerSetPanels.Add( self.panelSources, 1, wx.EXPAND )
		sizerSetPanels.Add( self.panelArea, 1, wx.EXPAND )
		sizerSetPanels.Add( self.panelSolution, 1, wx.EXPAND )

		sizerContent.Add( self.panelXZ, 1, wx.EXPAND |wx.BOTTOM|wx.LEFT, 1 )     #polojili paneli v contentsizer
		sizerContent.Add( self.panelYZ, 1, wx.EXPAND |wx.BOTTOM|wx.LEFT, 1 )
		sizerContent.Add( self.panelXY, 1, wx.EXPAND |wx.BOTTOM|wx.LEFT, 1 )
		sizerContent.Add( sizerSetPanels, 1, wx.EXPAND |wx.BOTTOM|wx.LEFT, 1 )

		#self.SetBackgroundColour("yellow")     #++++++++++++++++++++++++++UBRAT

		#sizerMain.Add( self.tBar, 0, wx.EXPAND|wx.BOTTOM, 4 )             #polojili toolbar v mainsizer
		sizerMain.Add( sizerContent, 1, wx.EXPAND, 5 )                    #polojili contentsizer v mainsizer
		self.SetSizer( sizerMain )
		self.Layout()

		self.statusbar = ESB.EnhancedStatusBar(self, -1)
		self.statusbar.SetSize((-1, 23))
		self.statusbar.SetFieldsCount(1)
		self.SetStatusBar(self.statusbar)
		self.gauge = wx.Gauge(self.statusbar, -1, 100, pos=(0,2))
		#self.gauge.Hide()
		bmpBuf = wx.ArtProvider_GetBitmap(wx.ART_ERROR,
										wx.ART_TOOLBAR, (16,16))

		self.btnThreadCancel = wx.StaticBitmap(self.statusbar, -1, bmpBuf, pos=(190,2))
		self.btnThreadCancel.Bind(wx.EVT_LEFT_UP, self.abortThread)
		self.gauge.Hide()
		self.btnThreadCancel.Hide()
		self.statictext = wx.StaticText(self.statusbar, -1, "", pos=(350,2))

		#self.Bind(wx.EVT_IDLE, self.IdleHandler)
		# Set up event handler for any worker thread results
		subThread.EVT_RESULT(self, self.checkThread)

		self.Bind(wx.EVT_SIZE, self.OnSize)

	# def IdleHandler(self, event):
	# 	print "suka"

	def switchPanelSet(self, num):
		#print num
		#vklychit num
		if (num == 0):
			self.panelSet.Show()
		elif (num == 1):
			self.panelBlocks.Show()
			self.panelBlocks.UpdateEdit()
		elif (num == 2):
			self.panelSources.Show()
		elif (num == 3):
			self.panelArea.Show()
			self.panelArea.UpdateEdit()
		elif (num == 4):
			self.panelSolution.Show()

		#vykluchit cur
		if (self.curPanel == 0):
			self.panelSet.Hide()
		elif (self.curPanel == 1):
			self.panelBlocks.Hide()
		elif (self.curPanel == 2):
			self.panelSources.Hide()
		elif (self.curPanel == 3):
			self.panelArea.Hide()
		elif (self.curPanel == 4):
			self.panelSolution.Hide()

		#time.sleep(5)
		#self.Layout()

		self.curPanel=num

	def startThread(self, npoints, stype, mode, op=[0,0,0]):
		self.combo = subThread.getCombo(len(self.blocks))
		self.worked = True
		solvThread = subThread.TestThread(self)
		#stype - int/mcnp/roma
		#mode -  0=zmch; 1=mesh; 2=onepoint
		solvThread.solve(npoints, stype, mode, op)
		#self.solvThread = subThread.TestThread(self)
		#print "Thread started!"
		self.gauge.Show()
		self.btnThreadCancel.Show()
		self.UIDisable()		

	def UIDisable(self):
		self.tBar.Disable()
		self.panelSet.UIDisable()
		self.panelBlocks.UIDisable()
		self.panelSources.UIDisable()
		self.panelArea.UIDisable()
		self.panelSolution.UIDisable()

	def UIEnable(self):
		self.tBar.Enable()
		self.panelSet.UIEnable()
		self.panelBlocks.UIEnable()
		self.panelSources.UIEnable()
		self.panelArea.UIEnable()
		self.panelSolution.UIEnable()
		self.Refresh()

	def checkThread(self, msg):
		t = msg.percent
		if isinstance(t, int):
			if (t==-1):
				self.gauge.Hide()
				self.gauge.SetValue(0)
				self.btnThreadCancel.Hide()
				self.UIEnable()
				self.Refresh()
				if (msg.data[0]):
					self.pointInfo(msg.data[1])
			else:
				self.gauge.SetValue(t)
				#print t, "%"
				#print "Time since thread started: ",t," seconds"
		else:
			print t, "gnuda"

	def pointInfo(self, point, i1=-1):
		def OnClose(e):
			self.Enable()
			f2.Destroy()

		self.bestPoints.append(point)
		self.curBestPoint = len(self.bestPoints)-1
		self.Refresh()

		f2 = wx.Frame(None, -1)
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		f2.SetSizer( bSizer1 )

		self.Disable()
		suka_sortirovka_blyat = [[],[]]
		st = "point: (" + str(point.c[0]) + "; " + str(point.c[1]) + "; " + str(point.c[2]) + ")\n"
		st += "crit\tchuvstv\t\tporog\n"
		for j in xrange(len(self.combo)):
			sub_st = ""
			for i in xrange(len(self.combo[j])):
				if self.combo[j][i]:
					sub_st += str(i+1) + " "
			try:
				sub_st += ":\t" + str(point.data[j])
				if (self.kvantil!=-1 and self.fon!=-1 and self.vremya!=-1):
					sub_st += "\t" + str(1000*self.kvantil*((10*self.fon/self.vremya)**0.5)/point.data[j])
				sub_st += "\n"
			except:
				sub_st += ":\t" + "nan" + "\n"
			suka_sortirovka_blyat[0].append(sub_st)
			suka_sortirovka_blyat[1].append(point.data[j]*1)

		#sortiruem
		for j in xrange(len(self.combo)-1):
			for i in xrange(len(self.combo)-1):
				if (suka_sortirovka_blyat[1][i+1]<suka_sortirovka_blyat[1][i]):
					bufv = suka_sortirovka_blyat[1][i]*1
					suka_sortirovka_blyat[1][i] = suka_sortirovka_blyat[1][i+1]*1
					suka_sortirovka_blyat[1][i+1] = bufv*1

					bufst = suka_sortirovka_blyat[0][i]*1
					suka_sortirovka_blyat[0][i] = suka_sortirovka_blyat[0][i+1]*1
					suka_sortirovka_blyat[0][i+1] = bufst*1
		#prosto ruka lico ubei sebya za takuy sortirovku

		for i in xrange(len(self.combo)):
			st += suka_sortirovka_blyat[0][i]

		#st += "\n" + "max:\t" + str(point.best)

		f2.SetSize((500,500))
		c = wx.TextCtrl( f2, -1, st,  wx.Point(0, 0), f2.GetSize(), wx.TE_MULTILINE )
		bSizer1.Add( c, 0, wx.ALL, 0 )

		f2.Show()
		f2.Bind(wx.EVT_CLOSE, OnClose)

	def abortThread(self, event):
		self.worked = False
		self.btnThreadCancel.Hide()

	def OnSize(self, event):
		#st = wx.GetMouseState()
		#print st.LeftIsDown()
		#print event.GetId()
		w, h = self.GetSize()
		wNew = int(0.5*(w-18)) 
		hNew = int(0.5*(h-96))
		if (wNew<300):
			wNew = 300
		if (hNew<200):
			hNew = 200
		xNew = int(0.5*(w-14)) 
		yNew = int(0.5*(h-18))-5
		self.panelSet.SetSize((wNew, hNew+1))
		self.panelSet.SetPosition((xNew,yNew))
		#print self.panelYZ.GetPosition()
		self.panelXZ.SetSize((wNew, hNew))
		self.panelXZ.SetPosition((1,33))
		self.panelYZ.SetSize((wNew, hNew+1))
		self.panelYZ.SetPosition((1,yNew))
		self.panelXY.SetSize((wNew, hNew))
		self.panelXY.SetPosition((xNew,33))
		self.panelBlocks.SetSize((wNew, hNew+1))
		self.panelBlocks.SetPosition((xNew,yNew))
		self.panelSources.SetSize((wNew, hNew+1))
		self.panelSources.SetPosition((xNew,yNew))
		self.panelArea.SetSize((wNew, hNew+1))
		self.panelArea.SetPosition((xNew,yNew))
		self.panelSolution.SetSize((wNew, hNew+1))
		self.panelSolution.SetPosition((xNew,yNew))
		self.tBar.SetSize((w-16,-1))
		self.Refresh()

	def saveData(self, fileName):
		#print "save", fileName
		with open(fileName, "w") as file:
			file.write("setpr:"+
						str(self.cenx)+";"+
						str(self.ceny)+";"+
						str(self.cenz)+";"+
						str(self.cens)+";"+
						str(self.scenx)+";"+
						str(self.sceny)+";"+
						str(self.scenz)+";"+
						str(self.ssizex)+";"+
						str(self.ssizey)+";"+
						str(self.ssizez)+"\n")

			for block in self.blocks:
				file.write(block.toStr()+"\n")

			for source in self.sources:
				file.write(source.toStr()+"\n")

	def loadData(self, fileName):
		self.bestPoints = []
		self.blocks = []
		with open(fileName, "r") as file:
			for line in file:
				if (line[0:5]=="setpr"):
					st = line[6:-1].split(";")
					try:
						self.cenx = int(st[0])
					except:
						self.cenx = 0

					try:
						self.ceny = int(st[1])
					except:
						self.ceny = 0

					try:
						self.cenz = int(st[2])
					except:
						self.cenz = 0

					try:
						self.cens = float(st[3])
					except:
						self.cens = 1

					try:
						self.scenx = int(st[4])
					except:
						self.scenx = 200
					
					try:
						self.sceny = int(st[5])
					except:
						self.sceny = 200
					
					try:
						self.scenz = int(st[6])
					except:
						self.scenz = 200
					
					try:
						self.ssizex = int(st[7])
						self.mnx = int(int(st[7])*0.1)
					except:
						self.ssizex = 200
					
					try:
						self.ssizey = int(st[8])
						self.mny = int(int(st[8])*0.1)
					except:
						self.ssizey = 200
					
					try:
						self.ssizez = int(st[9])
						self.mnz = int(int(st[9])*0.1)
					except:
						self.ssizez = 200

				elif (line[0:5]=="block"):
					self.blocks.append(entity.Block(self, line[6:-1]))

				elif (line[0:5]=="sourc"):
					self.sources.append(entity.Source(self, line[6:-1]))

		self.panelBlocks.curBlock = len(self.blocks)-1
		self.panelBlocks.UpdateEdit()
		self.panelSources.curSource = len(self.sources)-1
		self.panelSources.UpdateEdit()
		self.panelArea.UpdateEdit()
		self.Refresh()

	def readTypes(self):
		cur = -1
		with open("types","r") as file:
			for line in file:
				if (line[0]=="[" and line[-2]=="]"):
					self.blockTypes.append(entity.BlockType(self))
					cur += 1
				elif (cur>-1):
					if (line[0:4]=="name"):
						self.blockTypes[-1].name=line[5:-1]
					elif (line[0:2]=="l1"):
						self.blockTypes[-1].l1=int(line[3:-1])
					elif (line[0:2]=="l2"):
						self.blockTypes[-1].l2=int(line[3:-1])
					elif (line[0:2]=="l3"):
						self.blockTypes[-1].l3=int(line[3:-1])
					elif (line[0:5]=="sdvig"):
						self.blockTypes[-1].sdvig=int(line[6:-1])
					elif (line[0:2]=="r1"):
						self.blockTypes[-1].r1=float(line[3:-1])
					elif (line[0:2]=="r2"):
						self.blockTypes[-1].r2=float(line[3:-1])
					elif (line[0:4]=="otst"):
						self.blockTypes[-1].otst=float(line[5:-1])
	
	def refresh(self):
		self.curBestPoint = -1
		self.bestPoints = []
		self.Refresh()

class MainAppClass(wx.App):
	def __init__(self, redirect=False, filename=None):
		wx.App.__init__(self, redirect, filename)

	def OnInit(self):
		# create frame here
		frame = MainFrame()
		frame.Show()
		return True

def main():
	app = MainAppClass()
	app.MainLoop()

if __name__ == "__main__":
	main()


