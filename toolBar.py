import wx
import os

class CreateToolBar(wx.ToolBar):
	def __init__(self, parent, p=wx.DefaultPosition, s=wx.DefaultSize):       #, id1=wx.ID_ANY, point1=wx.DefaultPosition, size1=wx.DefaultSize
		wx.ToolBar.__init__( self, parent, wx.ID_ANY, p, s)      #, id1, wx.Point(point1.Get()[0]), size=size1
		self.parent = parent
		self.AddTool( 101, wx.Bitmap("ico/open.png") )
		self.AddTool( 102, wx.Bitmap("ico/save.png") )
		self.AddTool( 103, wx.Bitmap("ico/saveas.png") )
		#self.AddSeparator()
		#self.AddTool( 106, wx.Bitmap("ico/play.png") )
		#self.AddSeparator()
		#self.AddTool( 104, wx.Bitmap("ico/stop.png") )
		self.AddTool( 105, wx.Bitmap("ico/refresh.png") ) 
		self.Realize()
		self.Bind(wx.EVT_TOOL, self.onToolBar )

	def onToolBar(self, event):
		id = event.GetId()

		if (id == 106):
			self.parent.startThread(event)
		elif (id == 104):
			print self.parent.abortThread(event)
		elif (id == 101):
			wildcard = "All files (*.*)|*.*"
			openDialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN)
			if openDialog.ShowModal() == wx.ID_OK:
				self.parent.fileName = openDialog.GetPath()
				self.parent.loadData(self.parent.fileName)
			openDialog.Destroy()
		elif (id == 102):
			if (self.parent.fileName==""):
				self.forSaveRequest()
			else:
				self.parent.saveData(self.parent.fileName)
		elif (id == 103):
			self.forSaveRequest()
		elif (id == 105):
			self.parent.refresh()
			

	def forSaveRequest(self):
		wildcard = "All files (*.*)|*.*"
		saveDialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, wx.SAVE)
		if saveDialog.ShowModal() == wx.ID_OK:
			self.parent.fileName = saveDialog.GetPath()
			self.parent.saveData(self.parent.fileName)
		saveDialog.Destroy()


		# if (id == wx.ID_EXIT ):
		# 	self.onClose(event)
		
		
		
		# elif (id == 104):
		# 	if ((self.curi != -1) and (self.curj != -1)):					
		# 		self.data.append([])
		# 		self.data[-1].append(self.curi)
		# 		self.data[-1].append(self.curj)
		# 		self.data[-1].append("Element")
		# 		self.data[-1].append("Pasport")
		# 		self.data[-1].append(0)
		# 		self.data[-1].append(0)
		# 		self.data[-1].append("1.1.2000")
		# 		self.data[-1].append(0)
		# 		self.data[-1].append(0)
		# 		self.elements[self.curi][self.curj][0] = "#800080"
		# 		self.Refresh()
		# 		self.retable()
		# elif (id == 105):
		# 	if (self.curLrow != -1):
		# 		i1 = -1
		# 		for i in range(len(self.data)):
		# 			if (self.leftTableList[self.curLrow][0:8]==self.data[i][0:8]):
		# 				i1 = 1*i
		# 		self.curLrow = -1
		# 		self.curLcol = -1
		# 		i2 = 1*self.data[i1][0]
		# 		j2 = 1*self.data[i1][1]
		# 		self.data.remove(self.data[i1])
		# 		#print "udalit",self.data[i1]
		# 		flag = False
		# 		for i in range(len(self.data)):
		# 			if (self.data[i][0] == i2) and (self.data[i][1] == j2):
		# 				flag = True
		# 		if (not flag):
		# 			self.elements[i2][j2][0] = 1*table.table[i2][j2][0]
		# 			self.Refresh()
		# 		self.retable()
		# elif (id == 106):
		# 	MessageBox(self,"report")