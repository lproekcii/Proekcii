# -*- coding: utf-8 -*- 

import wx
import entity
import time
import copy


#-----------------------------------------
# x        x
# |_z      |_y
#
#
# y
# |_z
#
# myid:   0 - XZ;  1 - YZ;  2 - XY;
#-----------------------------------------

class PanelGraph(wx.Panel):
	def __init__(self, parent, myid):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.parent = parent
		self.myid = myid
		if (self.myid==0):
			self.x = 2
			self.y = 0
			self.z = 1
			self.direct = True  #znachit chto budem minimum iskat 
									#(v kachestve blijnego k nabludeniu)
		elif (self.myid==1):
			self.x = 2
			self.y = 1
			self.z = 0
			self.direct = False   #znachit chto budem max iskat
		elif (self.myid==2):
			self.x = 1
			self.y = 0
			self.z = 2
			self.direct = False   #znachit chto budem max iskat
		#sizer = wx.BoxSizer( wx.VERTICAL )
		#self.SetSizer( sizer )
		#self.Layout()
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOTION, self.OnMouse)
		self.Bind(wx.EVT_LEFT_UP, self.OnClick)

		#sizer.Fit( self )

	def OnClick(self, e):
		if (len(self.parent.bestPoints)==0): return
		x1,y1 = e.GetPosition()
		x, y, z = self.pxtocr(x1,y1)

		ic = -1
		bufr = 500
		#bejim po bestpoints i nahodim blijaishuy k x,y,z
		if (self.myid==0):
			bestP = copy.copy(self.parent.bestPoints[0])
			bufr = (bestP.c[0]-x)**2 + (bestP.c[2]-z)**2
			for i in xrange(len(self.parent.bestPoints)):
				p = copy.copy(self.parent.bestPoints[i])
				if (bufr > (p.c[0]-x)**2 + (p.c[2]-z)**2):
					bufr = (p.c[0]-x)**2 + (p.c[2]-z)**2
					bestP = copy.copy(p)
					ic = i*1
		elif (self.myid==1):
			bestP = copy.copy(self.parent.bestPoints[0])
			bufr = (bestP.c[1]-y)**2 + (bestP.c[2]-z)**2
			for i in xrange(len(self.parent.bestPoints)):
				p = copy.copy(self.parent.bestPoints[i])
				if (bufr > (p.c[1]-y)**2 + (p.c[2]-z)**2):
					bufr = (p.c[1]-y)**2 + (p.c[2]-z)**2
					bestP = copy.copy(p)
					ic = i*1
		elif (self.myid==2):
			bestP = copy.copy(self.parent.bestPoints[0])
			bufr = (bestP.c[1]-y)**2 + (bestP.c[0]-x)**2
			for i in xrange(len(self.parent.bestPoints)):
				p = copy.copy(self.parent.bestPoints[i])
				if (bufr > (p.c[1]-y)**2 + (p.c[0]-x)**2):
					bufr = (p.c[1]-y)**2 + (p.c[0]-x)**2
					bestP = copy.copy(p)
					ic = i*1

		#teper proverim dostatocho li blizko iskomaya tochka
		if bufr>2.7*(self.parent.cens**1.7):
			return

		self.parent.pointInfo(bestP, ic)

	def OnMouse(self, e):
		x1,y1 = e.GetPosition()
		x, y, z = self.pxtocr(x1,y1)
		x, y, z = int(x), int(y), int(z)
		self.parent.statictext.SetLabel("("+str(x)+", "+str(y)+", "+str(z)+")")

	def OnPaint(self, e):
		#http://zetcode.com/wxpython/gdi/
		dc = wx.PaintDC(self)
		dc.SetPen(wx.Pen('white'))
		w, h = self.GetSize()
		dc.DrawRectangle(0, 0, w, h)
		self.DrawHint(dc, w, h)
		self.DrawBlocks(dc)
		self.DrawSources(dc)
		self.DrawSolu(dc)
		self.DrawBestPoints(dc)
		self.DrawCurBestPoint(dc)

		#self.DrawAxis(dc, w, h)
		#self.DrawGrid(dc)
		#print self.GetSize()

	def DrawCurBestPoint(self, dc):
		if (self.parent.curBestPoint==-1): return
		x, y = self.crtopx(self.parent.bestPoints[self.parent.curBestPoint].c)
		r = 6
		dc.DrawLine(x-r, y, x+r, y)
		dc.DrawLine(x, y-r, x, y+r)

	def DrawBestPoints(self, dc):
		if ((self.parent.soluType<3 and self.myid==self.parent.soluType) or (self.parent.soluType==3)):
			dc.SetPen(wx.Pen('#000000'))
			for p in self.parent.bestPoints:
				x,y = self.crtopx(p.c)
				dc.DrawCircle(x,y,2)

	def DrawSolu(self, dc):
		#vo snachala cheknem ne 2d li u nas
		if ((self.parent.soluType<3 and self.myid==self.parent.soluType) or (self.parent.soluType==3)):
			#nada postavit punktir i narisovat 4 linii
			dc.SetPen(wx.Pen('#0AB1FF',1,wx.DOT))
			#dc.DrawLine(50, 50, 50, 50)
			cx, cy, cz = self.parent.scenx, self.parent.sceny, self.parent.scenz
			sx, sy, sz = int(0.5*self.parent.ssizex), int(0.5*self.parent.ssizey), int(0.5*self.parent.ssizez)
			pp = [
				[cx-sx, cy-sy, cz-sz],
				[cx-sx, cy-sy, cz+sz],
				[cx-sx, cy+sy, cz-sz],
				[cx-sx, cy+sy, cz+sz],
				[cx+sx, cy-sy, cz-sz],
				[cx+sx, cy-sy, cz+sz],
				[cx+sx, cy+sy, cz-sz],
				[cx+sx, cy+sy, cz+sz]
			]

			lines = [
				[pp[0],pp[1]],
				[pp[2],pp[3]],
				[pp[4],pp[5]],
				[pp[6],pp[7]],

				[pp[0],pp[2]],
				[pp[1],pp[3]],
				[pp[4],pp[6]],
				[pp[5],pp[7]],

				[pp[0],pp[4]],
				[pp[1],pp[5]],
				[pp[2],pp[6]],
				[pp[3],pp[7]]
			]


			for i in xrange(12):
				x1,y1 = self.crtopx(lines[i][0])
				x2,y2 = self.crtopx(lines[i][1])
				dc.DrawLine(x1, y1, x2, y2)

	def DrawHint(self, dc, w, h):
		l1 = ""
		l2 = ""
		if (self.myid==0):
			l1 = "X"
			l2 = "Z"
		elif (self.myid==1):
			l1 = "Y"
			l2 = "Z"
		elif (self.myid==2):
			l1 = "X"
			l2 = "Y"
		dc.SetPen(wx.Pen('#0AB1FF'))
		gc = wx.GraphicsContext.Create(dc)
		font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
		gc.SetFont(font, '#0AB1FF')
		dc.DrawLine(5, h-5, 25, h-5)     #gorizont
		dc.DrawLine(5, h-25, 5, h-5)         #vertikal
		dc.DrawText(l1, 5, h-35)      #mojno gc postavit
		dc.DrawText(l2, 25, h-15)     #mojno gc postavit

	def DrawBlocks(self, dc):
		#dc.SetPen(wx.Pen('#0AB1FF'))
		for block in self.parent.blocks:
			#print block.name
			nmax = 0
			nmin = 0
			zmax = block.points[0].c[self.z]*1
			zmin = block.points[0].c[self.z]*1
			for i in xrange(8):
				if (block.points[i].c[self.z] > zmax):
					nmax = i
					zmax = block.points[i].c[self.z]*1
				if (block.points[i].c[self.z] < zmin):
					nmin = i
					zmin = block.points[i].c[self.z]*1

			if (self.direct):
				nmin, nmax = nmax, nmin

			n = [0,0,0]
			# poluchim sosedei etoi vershiny tipa dlya punktira
			n = self.getSosed(nmin)
			for i in xrange(3):
				self.drawLine(dc, block.points[nmin].c,block.points[n[i]].c,1)
			#risuem eti 3 punktira: nmin-n[0]  nmin-n[1]  nmin-n[2]

			#dlya kajdogo n1n2n3 poluchaem ego sosedei napr: n11n12n13
			for i in xrange(3):
				nSub = self.getSosed(n[i])
				for j in xrange(3):
					if (nSub[j] != nmin):
						self.drawLine(dc, block.points[n[i]].c,block.points[nSub[j]].c,0)
						#risuem n[i]-nSub[j]

			#teper berem protivopolojnuyn vershinu, sosedei i risuem tri normalnye linii
			n = self.getSosed(nmax)
			for i in xrange(3):
				self.drawLine(dc, block.points[nmax].c,block.points[n[i]].c,0)
			#risuem eti 3 linii: nmax-n[0]  nmax-n[1]  nmax-n[2]

			#risuem krujochek centr bloka
			x,y = self.crtopx(block.coord)
			dc.DrawCircle(x,y,3)
			#risuem imya
			dc.DrawText(block.name, x+5, y+5)

	def DrawSources(self, dc):
		#dc.SetPen(wx.Pen('#0AB1FF'))
		for source in self.parent.sources:
			#risuem krujochek centr bloka
			x,y = self.crtopx(source.coord)
			dc.DrawCircle(x,y,3)    #pomenyat na chtonibud
			#risuem imya
			dc.DrawText(source.name, x+5, y+5)

	def crtopx(self, p):
		#p[0,1,2]
		#return x,y
		cens = self.parent.cens
		if (cens==0):
			return 0,0
		w, h = self.GetSize()
		if (self.myid==0):
			cenx = self.parent.cenz
			ceny = self.parent.cenx
		elif (self.myid==1):
			cenx = self.parent.cenz
			ceny = self.parent.ceny
		elif (self.myid==2):
			cenx = self.parent.ceny
			ceny = self.parent.cenx
		#print self.myid, cenx, ceny
		return 1.0*(p[self.x] - cenx)/cens + 0.5*w, 1.0*(ceny - p[self.y])/cens + 0.5*h

	def pxtocr(self, x1,y1):
		xm, ym = self.GetSize()
		if (self.myid==0):
			x, y, z = self.parent.cenx - self.parent.cens*(y1 - 0.5*ym), 0, self.parent.cenz + self.parent.cens*(x1 - 0.5*xm)
		elif (self.myid==1):
			x, y, z = 0, self.parent.ceny - self.parent.cens*(y1 - 0.5*ym), self.parent.cenz + self.parent.cens*(x1 - 0.5*xm)
		elif (self.myid==2):
			x, y, z = self.parent.cenx - self.parent.cens*(y1 - 0.5*ym), self.parent.ceny + self.parent.cens*(x1 - 0.5*xm), 0
		return [x,y,z]

	def drawLine(self, dc, p1, p2, ltype):
		#0 prosto
		if (ltype == 0):
			dc.SetPen(wx.Pen('#000000',1,wx.SOLID))
		#1 punktir
		elif (ltype == 1):
			dc.SetPen(wx.Pen('#000000',1,wx.DOT))

		x1, y1 = self.crtopx(p1)
		x2, y2 = self.crtopx(p2)

		dc.DrawLine(x1, y1, x2, y2)

	def getSosed(self, n):
		if (n==0):
			return [1,2,4]
		elif (n==1):
			return [0,3,5]
		elif (n==2):
			return [0,3,6]
		elif (n==3):
			return [1,2,7]
		elif (n==4):
			return [0,5,6]
		elif (n==5):
			return [1,4,7]
		elif (n==6):
			return [2,4,7]
		elif (n==7):
			return [3,5,6]

	def DrawAxis(self, dc, w, h):
		dc.SetPen(wx.Pen('#0AB1FF'))
		font =  dc.GetFont()
		font.SetSymbolicSize(1)
		#font.SetPointSize(32)
		dc.SetFont(font)
		dc.DrawLine(1, h-15, w-1, h-15)     #gorizont
		dc.DrawLine(15, 1, 15, h-15)         #vertikal

		for i in range( 15, h-15, 20):      #vertikalnye
			dc.DrawText(str(i), -30, i+5)
			dc.DrawLine(2, i, -5, i)

		for i in range( 1, w, int(w*0.2)):    #gorintal
			dc.DrawLine(i, h-14, i, h-11)			#riski
			dc.DrawText(str(i), i-4, h-14)	 #cifry

	def DrawGrid(self, dc):
		dc.SetPen(wx.Pen('#d5d5d5'))

		for i in range(20, 220, 20):
			dc.DrawLine(2, i, 300, i)

		for i in range(100, 300, 100):
			dc.DrawLine(i, 2, i, 200)

class PanelSet(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.parent = parent
		#sizer = wx.BoxSizer( wx.VERTICAL )
		#self.SetSizer( sizer )
		#self.Layout()

		#self.tBar = toolBar.CreateToolBar(self, wx.Point(240,240),   wx.Size( 100,100 ) )


		self.btnBlocks   = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap(u'ico/blocks.png'), wx.Point(10,10),   wx.Size( 100,100 ) )
		self.btnSources  = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap(u'ico/sources.png'), wx.Point(120,10),  wx.Size( 100,100 )  )
		self.btnArea     = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap(u'ico/area.png'),       wx.Point(10,120),  wx.Size( 100,100 )  )
		self.btnSolution = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap(u'ico/solu.png'),    wx.Point(120,120),  wx.Size( 100,100 )  )

		#self.btnBlocks   = wx.Button( self, wx.ID_ANY, u"bloki", wx.Point(10,10),   wx.Size( 100,100 ) )
		#self.btnSources  = wx.Button( self, wx.ID_ANY, u"istochniki", pos=(120,10), size=( 100,100 )  )
		#self.btnArea     = wx.Button( self, wx.ID_ANY, u"zona",       pos=(10,120), size=( 100,100 )  )
		#self.btnSolution = wx.Button( self, wx.ID_ANY, u"raschet",    pos=(120,120), size=( 100,100 )  )

		#self.SetBackgroundColour("white")

		self.btnBlocks.Bind(wx.EVT_BUTTON, lambda event: self.OnButton(event, 1))
		self.btnSources.Bind(wx.EVT_BUTTON, lambda event: self.OnButton(event, 2))
		self.btnArea.Bind(wx.EVT_BUTTON, lambda event: self.OnButton(event, 3))
		self.btnSolution.Bind(wx.EVT_BUTTON, lambda event: self.OnButton(event, 4))
		#sizer.Fit( self )

	def OnButton(self, event, num):
		#print num
		self.parent.switchPanelSet(num)

	def UIEnable(self):
		self.btnBlocks.Enable()
		self.btnSources.Enable()
		self.btnArea.Enable()
		self.btnSolution.Enable()

	def UIDisable(self):
		self.btnBlocks.Disable()
		self.btnSources.Disable()
		self.btnArea.Disable()
		self.btnSolution.Disable()

class PanelBlocks(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.parent = parent
		self.curBlock = -1
		ccc = (240,240,240)
		#sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.btnBack = wx.Button( self, wx.ID_ANY, u"Назад",                      pos=(10,10),   size=( 70, 25 ) )		
		self.chsBlock = wx.Choice( self, wx.ID_ANY,                        wx.Point(230, 55), wx.Size(100, 30), [], 0 )     # spisok tekushih blokov
		#self.chsBlock.SetBackgroundColour(ccc)
		self.chsBlock.Bind(wx.EVT_CHOICE, self.OnBlocks)
		lblName = wx.StaticText( self, wx.ID_ANY, u"имя",                 pos=(10, 38) )
		self.txtName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,        wx.Point(10, 55), wx.Size(100, 25), 0 )   #imya bloka
		self.txtName.SetBackgroundColour(ccc)
		self.txtName.Bind(wx.EVT_TEXT, self.OnText)
		lblChustv = wx.StaticText( self, wx.ID_ANY, u"чувствительность",           pos=(120, 38) )
		self.txtChustv = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(120, 55), wx.Size(100, 25), 0 )   #chustv
		self.txtChustv.SetBackgroundColour(ccc)
		self.txtChustv.Bind(wx.EVT_TEXT, self.OnText)
		lblSizeX = wx.StaticText( self, wx.ID_ANY, u"размер x",               pos=(10, 78) )
		self.txtSizeX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,       wx.Point(10, 95), wx.Size(100, 25), 0 )   # sizex
		self.txtSizeX.SetBackgroundColour(ccc)
		self.txtSizeX.Bind(wx.EVT_TEXT, self.OnText)
		lblSizeY = wx.StaticText( self, wx.ID_ANY, u"размер y",              pos=(120, 78) )
		self.txtSizeY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,      wx.Point(120, 95), wx.Size(100, 25), 0 )   # sizey
		self.txtSizeY.SetBackgroundColour(ccc)
		self.txtSizeY.Bind(wx.EVT_TEXT, self.OnText)
		lblSizeZ = wx.StaticText( self, wx.ID_ANY, u"размер z",              pos=(230, 78) )
		self.txtSizeZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,      wx.Point(230, 95), wx.Size(100, 25), 0 )   # sizez
		self.txtSizeZ.SetBackgroundColour(ccc)
		self.txtSizeZ.Bind(wx.EVT_TEXT, self.OnText)
		lblCoordX = wx.StaticText( self, wx.ID_ANY, u"положение x",              pos=(10, 118) )
		self.txtCoordX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(10, 135), wx.Size(100, 25), 0 )   # koordx
		self.txtCoordX.SetBackgroundColour(ccc)
		self.txtCoordX.Bind(wx.EVT_TEXT, self.OnText)
		lblCoordY = wx.StaticText( self, wx.ID_ANY, u"положение y",             pos=(120, 118) )
		self.txtCoordY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,    wx.Point(120, 135), wx.Size(100, 25), 0 )   # koordy
		self.txtCoordY.SetBackgroundColour(ccc)
		self.txtCoordY.Bind(wx.EVT_TEXT, self.OnText)
		lblCoordZ = wx.StaticText( self, wx.ID_ANY, u"положение z",             pos=(230, 118) )
		self.txtCoordZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,    wx.Point(230, 135), wx.Size(100, 25), 0 )   # koordz
		self.txtCoordZ.SetBackgroundColour(ccc)
		self.txtCoordZ.Bind(wx.EVT_TEXT, self.OnText)
		lblUgolX = wx.StaticText( self, wx.ID_ANY, u"угол вокр. x",              pos=(10, 158) )
		self.txtUgolX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,      wx.Point(10, 175), wx.Size(100, 25), 0 )   # ugolx
		self.txtUgolX.SetBackgroundColour(ccc)
		self.txtUgolX.Bind(wx.EVT_TEXT, self.OnText)
		lblUgolY = wx.StaticText( self, wx.ID_ANY, u"угол вокр. y",             pos=(120, 158) )
		self.txtUgolY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(120, 175), wx.Size(100, 25), 0 )   # ugoly
		self.txtUgolY.SetBackgroundColour(ccc)
		self.txtUgolY.Bind(wx.EVT_TEXT, self.OnText)
		lblUgolZ = wx.StaticText( self, wx.ID_ANY, u"угол вокр. z",             pos=(230, 158) )
		self.txtUgolZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(230, 175), wx.Size(100, 25), 0 )   # ugolz
		self.txtUgolZ.SetBackgroundColour(ccc)
		self.txtUgolZ.Bind(wx.EVT_TEXT, self.OnText)


		self.btnAddBlock = wx.Button( self, wx.ID_ANY, u"Добавить блок",            pos=(10,210),   size=( 100, 25 ) )                #add block
		self.btnAddBlock.Bind(wx.EVT_BUTTON, self.AddBlock)
		blockTypeList = []
		for bltp in self.parent.blockTypes:
			blockTypeList.append(bltp.name[:]) 
		self.chsBlockType = wx.Choice( self, wx.ID_ANY,                    wx.Point(11, 235), wx.Size(98, 30), blockTypeList, 0 )     #tip bloka
		self.chsBlockType.SetSelection(1)
		self.chsBlockType.Bind(wx.EVT_CHOICE, self.OnBlockTypes)
		self.btnDeleteBlock = wx.Button( self, wx.ID_ANY, u"Удалить блок",     pos=(120,210),   size=( 100, 25 ) )                #delete block
		self.btnDeleteBlock.Bind(wx.EVT_BUTTON, self.OnDelete)
		self.btnApplyChanges = wx.Button( self, wx.ID_ANY, u"Применить",           pos=(230,240),   size=( 100, 25 ) )                #apply change
		self.btnApplyChanges.Bind(wx.EVT_BUTTON, self.OnApply)
		self.btnCancelChanges = wx.Button( self, wx.ID_ANY, u"Сбросить",         pos=(230,210),   size=( 100, 25 ) )                #cancel change
		self.btnCancelChanges.Bind(wx.EVT_BUTTON, self.OnCancel)
		#sizer.Add( m_button, 0, wx.ALL, 5 )

		self.btnBack.Bind(wx.EVT_BUTTON, self.OnButton)
		#sizer.Fit( self )

	def OnButton(self, event):
		self.parent.switchPanelSet(0)

	def OnCancel(self, event):
		self.UpdateEdit()

	def OnApply(self, e):
		t = self.curBlock
		if (t == -1):
			self.UpdateEdit()
			return
		
		buf = self.txtName.GetValue()
		self.parent.blocks[t].name = buf

		buf = self.txtChustv.GetValue()
		try:
			self.parent.blocks[t].chuvstv = int(buf)
		except:
			pass

		buf = self.txtSizeX.GetValue()
		try:
			self.parent.blocks[t].size[0] = int(buf)
		except:
			pass

		buf = self.txtSizeY.GetValue()
		try:
			self.parent.blocks[t].size[1] = int(buf)
		except:
			pass

		buf = self.txtSizeZ.GetValue()
		try:
			self.parent.blocks[t].size[2] = int(buf)
		except:
			pass

		buf = self.txtCoordX.GetValue()
		try:
			self.parent.blocks[t].coord[0] = int(buf)
		except:
			pass

		buf = self.txtCoordY.GetValue()
		try:
			self.parent.blocks[t].coord[1] = int(buf)
		except:
			pass

		buf = self.txtCoordZ.GetValue()
		try:
			self.parent.blocks[t].coord[2] = int(buf)
		except:
			pass

		buf = self.txtUgolX.GetValue()
		try:
			self.parent.blocks[t].ugol[0] = int(buf)
		except:
			pass

		buf = self.txtUgolY.GetValue()
		try:
			self.parent.blocks[t].ugol[1] = int(buf)
		except:
			pass

		buf = self.txtUgolZ.GetValue()
		try:
			self.parent.blocks[t].ugol[2] = int(buf)
		except:
			pass

		self.parent.blocks[t].setPoints()
		self.UpdateEdit()
		self.parent.Refresh()

	def OnDelete(self, event):
		if (self.curBlock == -1):
			return

		self.parent.blocks.pop(self.curBlock)
		self.curBlock = len(self.parent.blocks)-1
		self.UpdateEdit()
		self.parent.Refresh()

	def AddBlock(self, event):
		t = self.parent.curType
		#dobavili i ustanovili cur na nego
		self.parent.blocks.append(entity.Block(self.parent, "", t))
		self.curBlock = len(self.parent.blocks)-1
		self.UpdateEdit()
		self.parent.Refresh()
		
	def UpdateEdit(self):
		t = self.curBlock

		#obrabotka choise
		newList = []
		i = 1
		for block in self.parent.blocks:
			newList.append(str(i)+". "+block.name[:])
			i += 1
		
		self.chsBlock.SetItems(newList)
		self.chsBlock.SetSelection(t)

		#esli cur block -1 to ochistit
		if (t==-1):
			self.txtName.SetValue("")
			self.txtChustv.SetValue("")
			self.txtSizeX.SetValue("")
			self.txtSizeY.SetValue("")
			self.txtSizeZ.SetValue("")
			self.txtCoordX.SetValue("")
			self.txtCoordY.SetValue("")
			self.txtCoordZ.SetValue("")
			self.txtUgolX.SetValue("")
			self.txtUgolY.SetValue("")
			self.txtUgolZ.SetValue("")
		else:
			#inache zapolnit ego znacheniyami
			self.txtName.SetValue(self.parent.blocks[t].name)
			self.txtChustv.SetValue(str(self.parent.blocks[t].chuvstv))
			self.txtSizeX.SetValue(str(self.parent.blocks[t].size[0]))
			self.txtSizeY.SetValue(str(self.parent.blocks[t].size[1]))
			self.txtSizeZ.SetValue(str(self.parent.blocks[t].size[2]))
			self.txtCoordX.SetValue(str(self.parent.blocks[t].coord[0]))
			self.txtCoordY.SetValue(str(self.parent.blocks[t].coord[1]))
			self.txtCoordZ.SetValue(str(self.parent.blocks[t].coord[2]))
			self.txtUgolX.SetValue(str(self.parent.blocks[t].ugol[0]))
			self.txtUgolY.SetValue(str(self.parent.blocks[t].ugol[1]))
			self.txtUgolZ.SetValue(str(self.parent.blocks[t].ugol[2]))
		
		#podkrasit
		ccc=(240,240,240)
		self.txtName.SetBackgroundColour(ccc)
		self.txtChustv.SetBackgroundColour(ccc)
		self.txtSizeX.SetBackgroundColour(ccc)
		self.txtSizeY.SetBackgroundColour(ccc)
		self.txtSizeZ.SetBackgroundColour(ccc)
		self.txtCoordX.SetBackgroundColour(ccc)
		self.txtCoordY.SetBackgroundColour(ccc)
		self.txtCoordZ.SetBackgroundColour(ccc)
		self.txtUgolX.SetBackgroundColour(ccc)
		self.txtUgolY.SetBackgroundColour(ccc)
		self.txtUgolZ.SetBackgroundColour(ccc)
		self.Refresh()

	def OnBlocks(self, event):
		t = self.chsBlock.GetSelection()
		self.chsBlock.SetSelection(t)
		self.curBlock = t
		self.UpdateEdit()

	def OnText(self, event):
		obj = event.GetEventObject()
		obj.SetBackgroundColour("white")
		self.Refresh()

	def OnBlockTypes(self, event):
		t = self.chsBlockType.GetSelection()
		self.chsBlockType.SetSelection(t)
		self.parent.curType = t

	def UIEnable(self):
		self.btnBack.Enable()
		self.chsBlock.Enable()
		self.txtName.Enable()
		self.txtChustv.Enable()
		self.txtSizeX.Enable()
		self.txtSizeY.Enable()
		self.txtSizeZ.Enable()
		self.txtCoordX.Enable()
		self.txtCoordY.Enable()
		self.txtCoordZ.Enable()
		self.txtUgolX.Enable()
		self.txtUgolY.Enable()
		self.txtUgolZ.Enable()
		self.btnAddBlock.Enable()
		self.chsBlockType.Enable()
		self.btnDeleteBlock.Enable()
		self.btnApplyChanges.Enable()
		self.btnCancelChanges.Enable()

	def UIDisable(self):
		self.btnBack.Disable()
		self.chsBlock.Disable()
		self.txtName.Disable()
		self.txtChustv.Disable()
		self.txtSizeX.Disable()
		self.txtSizeY.Disable()
		self.txtSizeZ.Disable()
		self.txtCoordX.Disable()
		self.txtCoordY.Disable()
		self.txtCoordZ.Disable()
		self.txtUgolX.Disable()
		self.txtUgolY.Disable()
		self.txtUgolZ.Disable()
		self.btnAddBlock.Disable()
		self.chsBlockType.Disable()
		self.btnDeleteBlock.Disable()
		self.btnApplyChanges.Disable()
		self.btnCancelChanges.Disable()

class PanelSources(wx.Panel):
	#time.sleep(5)
	def __init__(self, parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.parent = parent
		self.curSource = -1
		ccc = (240,240,240)
		#sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.btnBack = wx.Button( self, wx.ID_ANY, u"Назад",                      pos=(10,10),   size=( 70, 25 ) )
		self.chsSource = wx.Choice( self, wx.ID_ANY,                        wx.Point(230, 55), wx.Size(100, 30), [], 0 )     # spisok tekushih blokov
		self.chsSource.Bind(wx.EVT_CHOICE, self.OnSources)
		lblName = wx.StaticText( self, wx.ID_ANY, u"имя",                 pos=(10, 38) )
		self.txtName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,        wx.Point(10, 55), wx.Size(100, 25), 0 )   #imya istochnika
		self.txtName.SetBackgroundColour(ccc)
		self.txtName.Bind(wx.EVT_TEXT, self.OnText)
		lblAkt = wx.StaticText( self, wx.ID_ANY, u"активность",               pos=(120, 38) )
		self.txtAkt = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,        wx.Point(120, 55), wx.Size(100, 25), 0 )   #aktivn
		self.txtAkt.SetBackgroundColour(ccc)
		self.txtAkt.Bind(wx.EVT_TEXT, self.OnText)
		lblCoordX = wx.StaticText( self, wx.ID_ANY, u"положение x",               pos=(10, 78) )
		self.txtCoordX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,      wx.Point(10, 95), wx.Size(100, 25), 0 )   # koordx
		self.txtCoordX.SetBackgroundColour(ccc)
		self.txtCoordX.Bind(wx.EVT_TEXT, self.OnText)
		lblCoordY = wx.StaticText( self, wx.ID_ANY, u"положение y",              pos=(120, 78) )
		self.txtCoordY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(120, 95), wx.Size(100, 25), 0 )   # koordy
		self.txtCoordY.SetBackgroundColour(ccc)
		self.txtCoordY.Bind(wx.EVT_TEXT, self.OnText)
		lblCoordZ = wx.StaticText( self, wx.ID_ANY, u"положение z",              pos=(230, 78) )
		self.txtCoordZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(230, 95), wx.Size(100, 25), 0 )   # koordz
		self.txtCoordZ.SetBackgroundColour(ccc)
		self.txtCoordZ.Bind(wx.EVT_TEXT, self.OnText)

		self.btnAdd = wx.Button( self, wx.ID_ANY, u"Добавить источ",                 pos=(10,130),   size=( 100, 25 ) )                #add block
		self.btnAdd.Bind(wx.EVT_BUTTON, self.AddSource)
		self.btnDelete = wx.Button( self, wx.ID_ANY, u"Удалить источ",          pos=(120,130),   size=( 100, 25 ) )                #delete block
		self.btnDelete.Bind(wx.EVT_BUTTON, self.OnDelete)
		self.btnApply = wx.Button( self, wx.ID_ANY, u"Применить",                  pos=(230,160),   size=( 100, 25 ) )                #apply change
		self.btnApply.Bind(wx.EVT_BUTTON, self.OnApply)
		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Сбросить",         pos=(230,130),   size=( 100, 25 ) )                #cancel change
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		#sizer.Add( m_button, 0, wx.ALL, 5 )

		self.btnBack.Bind(wx.EVT_BUTTON, self.OnButton)
		#sizer.Fit( self )

	def OnButton(self, event):
		self.parent.switchPanelSet(0)
		pass

	def OnCancel(self, event):
		self.UpdateEdit()

	def UpdateEdit(self):
		t = self.curSource

		#obrabotka choise
		newList = []
		i = 1
		for source in self.parent.sources:
			newList.append(str(i)+". "+source.name[:])
			i += 1
		
		self.chsSource.SetItems(newList)
		self.chsSource.SetSelection(t)

		#esli cur block -1 to ochistit
		if (t==-1):
			self.txtName.SetValue("")
			self.txtAkt.SetValue("")
			self.txtCoordX.SetValue("")
			self.txtCoordY.SetValue("")
			self.txtCoordZ.SetValue("")
		else:
			#inache zapolnit ego znacheniyami
			self.txtName.SetValue(self.parent.sources[t].name)
			self.txtAkt.SetValue(str(self.parent.sources[t].akt))
			self.txtCoordX.SetValue(str(self.parent.sources[t].coord[0]))
			self.txtCoordY.SetValue(str(self.parent.sources[t].coord[1]))
			self.txtCoordZ.SetValue(str(self.parent.sources[t].coord[2]))
		
		#podkrasit
		ccc=(240,240,240)
		self.txtName.SetBackgroundColour(ccc)
		self.txtAkt.SetBackgroundColour(ccc)
		self.txtCoordX.SetBackgroundColour(ccc)
		self.txtCoordY.SetBackgroundColour(ccc)
		self.txtCoordZ.SetBackgroundColour(ccc)
		self.Refresh()

	def OnApply(self, e):
		t = self.curSource
		if (t == -1):
			self.UpdateEdit()
			return
		
		buf = self.txtName.GetValue()
		self.parent.sources[t].name = buf

		buf = self.txtAkt.GetValue()
		try:
			self.parent.sources[t].akt = int(buf)
		except:
			pass

		buf = self.txtCoordX.GetValue()
		try:
			self.parent.sources[t].coord[0] = int(buf)
		except:
			pass

		buf = self.txtCoordY.GetValue()
		try:
			self.parent.sources[t].coord[1] = int(buf)
		except:
			pass

		buf = self.txtCoordZ.GetValue()
		try:
			self.parent.sources[t].coord[2] = int(buf)
		except:
			pass

		self.UpdateEdit()
		self.parent.Refresh()

	def OnDelete(self, event):
		if (self.curSource == -1):
			return

		self.parent.sources.pop(self.curSource)
		self.curSource = len(self.parent.sources)-1
		self.UpdateEdit()
		self.parent.Refresh()

	def AddSource(self, event):
		self.parent.sources.append(entity.Source(self.parent, ""))
		self.curSource = len(self.parent.sources)-1
		self.UpdateEdit()
		self.parent.Refresh()

	def OnSources(self, event):
		t = self.chsSource.GetSelection()
		self.chsSource.SetSelection(t)
		self.curSource = t
		self.UpdateEdit()

	def OnText(self, event):
		obj = event.GetEventObject()
		obj.SetBackgroundColour("white")
		self.Refresh()

	def UIEnable(self):
		self.btnBack.Enable()
		self.chsSource.Enable()
		self.txtName.Enable()
		self.txtAkt.Enable()
		self.txtCoordX.Enable()
		self.txtCoordY.Enable()
		self.txtCoordZ.Enable()
		self.btnAdd.Enable()
		self.btnDelete.Enable()
		self.btnApply.Enable()
		self.btnCancel.Enable()

	def UIDisable(self):
		self.btnBack.Disable()
		self.chsSource.Disable()
		self.txtName.Disable()
		self.txtAkt.Disable()
		self.txtCoordX.Disable()
		self.txtCoordY.Disable()
		self.txtCoordZ.Disable()
		self.btnAdd.Disable()
		self.btnDelete.Disable()
		self.btnApply.Disable()
		self.btnCancel.Disable()

class PanelArea(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.parent = parent
		#sizer = wx.BoxSizer( wx.VERTICAL )
		self.btnBack = wx.Button( self, wx.ID_ANY, u"Назад",                       pos=(10,10),   size=( 70, 25 ) )
		self.btnBack.Bind(wx.EVT_BUTTON, self.OnButton)
		lblAreaSize = wx.StaticText( self, wx.ID_ANY, u"Видимая область",         pos=(120, 25) )
		lblACoordX = wx.StaticText( self, wx.ID_ANY, u"центр x",               pos=(10, 48) )
		self.txtACoordX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,      wx.Point(10, 65), wx.Size(100, 25), 0 )   # koordx
		self.txtACoordX.Bind(wx.EVT_TEXT, self.OnText)
		lblACoordY = wx.StaticText( self, wx.ID_ANY, u"центр y",              pos=(120, 48) )
		self.txtACoordY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(120, 65), wx.Size(100, 25), 0 )   # koordy
		self.txtACoordY.Bind(wx.EVT_TEXT, self.OnText)
		lblACoordZ = wx.StaticText( self, wx.ID_ANY, u"центр z",              pos=(230, 48) )
		self.txtACoordZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(230, 65), wx.Size(100, 25), 0 )   # koordz
		self.txtACoordZ.Bind(wx.EVT_TEXT, self.OnText)
		lblASize = wx.StaticText( self, wx.ID_ANY, u"масштаб",                 pos=(10, 88) )
		self.txtASize = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,       wx.Point(10, 105), wx.Size(100, 25), 0 )   # koordz
		self.txtASize.Bind(wx.EVT_TEXT, self.OnText)
		self.btnAuto = wx.Button( self, wx.ID_ANY, u"Авто",                    pos=(230, 105),   size=( 100, 25 ) )                #auto
		self.btnAuto.Bind(wx.EVT_BUTTON, self.OnAuto)
		
		lblSeeSize = wx.StaticText( self, wx.ID_ANY, u"Расчетная область",        pos=(120, 130) )
		rdBoxList = [ u"XZ", u"YZ", u"XY", u"3D" ]
		self.rdBox = wx.RadioBox( self, wx.ID_ANY, u"Тип расчета",            wx.Point(10, 235), wx.DefaultSize, rdBoxList, 4 )
		self.rdBox.SetSelection(3)
		self.rdBox.Bind(wx.EVT_RADIOBOX, self.OnRdBox)
		lblSCoordX = wx.StaticText( self, wx.ID_ANY, u"центр x",              pos=(10, 148) )
		self.txtSCoordX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(10, 165), wx.Size(100, 25), 0 )   # koordx
		self.txtSCoordX.Bind(wx.EVT_TEXT, self.OnText)
		lblSCoordY = wx.StaticText( self, wx.ID_ANY, u"центр y",             pos=(120, 148) )
		self.txtSCoordY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,    wx.Point(120, 165), wx.Size(100, 25), 0 )   # koordy
		self.txtSCoordY.Bind(wx.EVT_TEXT, self.OnText)
		lblSCoordZ = wx.StaticText( self, wx.ID_ANY, u"центр z",             pos=(230, 148) )
		self.txtSCoordZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,    wx.Point(230, 165), wx.Size(100, 25), 0 )   # koordz
		self.txtSCoordZ.Bind(wx.EVT_TEXT, self.OnText)
		lblSizeX = wx.StaticText( self, wx.ID_ANY, u"размер x",               pos=(10, 188) )
		self.txtSizeX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,       wx.Point(10, 205), wx.Size(100, 25), 0 )   # koordx
		self.txtSizeX.Bind(wx.EVT_TEXT, self.OnText)
		lblSizeY = wx.StaticText( self, wx.ID_ANY, u"размер y",              pos=(120, 188) )
		self.txtSizeY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,      wx.Point(120, 205), wx.Size(100, 25), 0 )   # koordy
		self.txtSizeY.Bind(wx.EVT_TEXT, self.OnText)
		lblSizeZ = wx.StaticText( self, wx.ID_ANY, u"размер z",              pos=(230, 188) )
		self.txtSizeZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,      wx.Point(230, 205), wx.Size(100, 25), 0 )   # koordz
		self.txtSizeZ.Bind(wx.EVT_TEXT, self.OnText)
		self.btnApply = wx.Button( self, wx.ID_ANY, u"Применить",                   pos=(230,270),   size=( 100, 25 ) )                #add block
		self.btnApply.Bind(wx.EVT_BUTTON, self.OnApply)
		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Сбросить",                 pos=(230,240),   size=( 100, 25 ) )                #add block
		self.btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		self.UpdateEdit()

	def OnApply(self, e):
		ccc = (240,240,240)
		try:
			buf = int(self.txtACoordX.GetValue())
			self.parent.cenx=buf
		except:
			pass
		
		try:
			buf = int(self.txtACoordY.GetValue())
			self.parent.ceny=buf
		except:
			pass

		try:
			buf = int(self.txtACoordZ.GetValue())
			self.parent.cenz=buf
		except:
			pass

		try:
			buf = float(self.txtASize.GetValue())
			self.parent.cens=buf
		except:
			pass

		try:
			buf = int(self.txtSCoordX.GetValue())
			self.parent.scenx=buf
		except:
			pass

		try:
			buf = int(self.txtSCoordY.GetValue())
			self.parent.sceny=buf
		except:
			pass

		try:
			buf = int(self.txtSCoordZ.GetValue())
			self.parent.scenz=buf
		except:
			pass

		try:
			buf = int(self.txtSizeX.GetValue())
			self.parent.ssizex=buf
			self.mnx=int(0.1*buf)
		except:
			pass

		try:
			buf = int(self.txtSizeY.GetValue())
			self.parent.ssizey=buf
			self.mny=int(0.1*buf)
		except:
			pass

		try:
			buf = int(self.txtSizeZ.GetValue())
			self.parent.ssizez=buf
			self.mnz=int(0.1*buf)
		except:
			pass

		for block in self.parent.blocks:
			block.setPoints()
		self.UpdateEdit()
		self.parent.Refresh()

	def OnCancel(self, e):
		self.UpdateEdit()

	def OnText(self, event):
		obj = event.GetEventObject()
		obj.SetBackgroundColour("white")
		self.Refresh()

	def OnRdBox(self, event):
		self.parent.soluType = self.rdBox.GetSelection()
		self.parent.Refresh()

	def OnAuto(self, event):
		if (len(self.parent.blocks)==0):
			return
		#ishem samuy dalekuy tochku
		x = self.parent.blocks[0].points[0].c[0]-self.parent.cenx
		y = self.parent.blocks[0].points[0].c[1]-self.parent.ceny
		z = self.parent.blocks[0].points[0].c[2]-self.parent.cenz
		r = x*x+y*y+z*z
		x,y,z = self.parent.cenx, self.parent.ceny, self.parent.cenz
		bmax = r*1
		for block in self.parent.blocks:
			for p in block.points:
				r = (p.c[0]-x)*(p.c[0]-x)+(p.c[1]-y)*(p.c[1]-y)+(p.c[2]-z)*(p.c[2]-z)
				if (r>bmax):
					bmax = r

		bmax = int(1.1*(bmax**0.5))
		#print bmax
		w,h = self.GetSize()
		w = min(w,h)
		w = int(0.5*w)
		#menyaem cens chtobi ee zahvatyvalo
		self.parent.cens = (bmax+1.0)/w
		self.UpdateEdit()
		self.parent.Refresh()

	def OnButton(self, event):
		self.parent.switchPanelSet(0)

	def UpdateEdit(self):
		ccc = (240,240,240)
		self.txtACoordX.SetValue(str(self.parent.cenx))
		self.txtACoordX.SetBackgroundColour(ccc)
		self.txtACoordY.SetValue(str(self.parent.ceny))
		self.txtACoordY.SetBackgroundColour(ccc)
		self.txtACoordZ.SetValue(str(self.parent.cenz))
		self.txtACoordZ.SetBackgroundColour(ccc)
		self.txtASize.SetValue(str(self.parent.cens))
		self.txtASize.SetBackgroundColour(ccc)
		self.txtSCoordX.SetValue(str(self.parent.scenx))
		self.txtSCoordX.SetBackgroundColour(ccc)
		self.txtSCoordY.SetValue(str(self.parent.sceny))
		self.txtSCoordY.SetBackgroundColour(ccc)
		self.txtSCoordZ.SetValue(str(self.parent.scenz))
		self.txtSCoordZ.SetBackgroundColour(ccc)
		self.txtSizeX.SetValue(str(self.parent.ssizex))
		self.txtSizeX.SetBackgroundColour(ccc)
		self.txtSizeY.SetValue(str(self.parent.ssizey))
		self.txtSizeY.SetBackgroundColour(ccc)
		self.txtSizeZ.SetValue(str(self.parent.ssizez))
		self.txtSizeZ.SetBackgroundColour(ccc)
		self.Refresh()

	def UIEnable(self):
		self.btnBack.Enable()
		self.txtACoordX.Enable()
		self.txtACoordY.Enable()
		self.txtACoordZ.Enable()
		self.txtASize.Enable()
		self.btnAuto.Enable()
		self.rdBox.Enable()
		self.txtSCoordX.Enable()
		self.txtSCoordY.Enable()
		self.txtSCoordZ.Enable()
		self.txtSizeX.Enable()
		self.txtSizeY.Enable()
		self.txtSizeZ.Enable()
		self.btnApply.Enable()
		self.btnCancel.Enable()

	def UIDisable(self):
		self.btnBack.Disable()
		self.txtACoordX.Disable()
		self.txtACoordY.Disable()
		self.txtACoordZ.Disable()
		self.txtASize.Disable()
		self.btnAuto.Disable()
		self.rdBox.Disable()
		self.txtSCoordX.Disable()
		self.txtSCoordY.Disable()
		self.txtSCoordZ.Disable()
		self.txtSizeX.Disable()
		self.txtSizeY.Disable()
		self.txtSizeZ.Disable()
		self.btnApply.Disable()
		self.btnCancel.Disable()

class PanelSolution(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		self.parent = parent
		#sizer = wx.BoxSizer( wx.VERTICAL )
		
		self.btnBack = wx.Button( self, wx.ID_ANY, u"Назад",                       pos=(10,10),   size=( 70, 25 ) )
		self.btnBack.Bind(wx.EVT_BUTTON, self.OnButton)
		lblAreaSize = wx.StaticText( self, wx.ID_ANY, u"Зона минимальной чувств",             pos=(110, 22) )
		rdBoxList = [ u"Интегральный", u"MCNP", u"Roman" ]
		self.rdBox = wx.RadioBox( self, wx.ID_ANY, u"метод",            wx.Point(20, 45), wx.DefaultSize, rdBoxList, 1 )
		#self.rdBox.Bind(wx.EVT_RADIOBOX, self.OnRdBox)
		lblKol = wx.StaticText( self, wx.ID_ANY, u"кол-во точек",                  pos=(230, 38) )
		self.txtKol = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,         wx.Point(230, 55), wx.Size(100, 25), 0 )   # koordz
		self.btnSolution = wx.Button( self, wx.ID_ANY, u"Расчет",              pos=(230, 85),   size=( 100, 25 ) )    #auto
		self.btnSolution.Bind(wx.EVT_BUTTON, self.OnSolve)
		self.btnOption = wx.Button( self, wx.ID_ANY, u"+",              pos=(330, 85),   size=( 14, 25 ) )    #auto
		self.btnOption.Bind(wx.EVT_BUTTON, self.OnOptions)
		lblOnePoint = wx.StaticText( self, wx.ID_ANY, u"Расчет одной точки",        pos=(118, 140) )
		lblSCoordX = wx.StaticText( self, wx.ID_ANY, u"коорд x",            pos=(10, 158) )
		self.txtSCoordX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,     wx.Point(10, 175), wx.Size(100, 25), 0 )   # koordx
		lblSCoordY = wx.StaticText( self, wx.ID_ANY, u"коорд y",           pos=(120, 158) )
		self.txtSCoordY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,    wx.Point(120, 175), wx.Size(100, 25), 0 )   # koordy
		lblSCoordZ = wx.StaticText( self, wx.ID_ANY, u"коорд z",           pos=(230, 158) )
		self.txtSCoordZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString,    wx.Point(230, 175), wx.Size(100, 25), 0 )   # koordz
		self.btnOnePoint = wx.Button( self, wx.ID_ANY, u"Расчет",          pos=(230, 205),   size=( 100, 25 ) )    #auto
		self.btnOnePoint.Bind(wx.EVT_BUTTON, self.OnOnePoint)
		self.btnOption2 = wx.Button( self, wx.ID_ANY, u"+",              pos=(330, 205),   size=( 14, 25 ) )    #auto
		self.btnOption2.Bind(wx.EVT_BUTTON, self.OnOptions2)
		lblMeshWrite = wx.StaticText( self, wx.ID_ANY, u"Запись сетки",      pos=(150, 235) )
		self.btnMeshWrite = wx.Button( self, wx.ID_ANY, u"Записать",          pos=(230, 255),   size=( 100, 25 ) )    #auto
		self.btnMeshWrite.Bind(wx.EVT_BUTTON, self.OnMeshWrite)
		self.btnOption3 = wx.Button( self, wx.ID_ANY, u"+",              pos=(330, 255),   size=( 14, 25 ) )    #auto
		self.btnOption3.Bind(wx.EVT_BUTTON, self.OnOptions3)
		
		#sizer.Fit( self )

	def OnMeshWrite(self, e):
		if (len(self.parent.blocks)==0): return
		self.parent.startThread(0, 0, 1)

	def OnOnePoint(self, e):
		flag = False
		try:
			cx = int(self.txtSCoordX.GetValue())
			self.txtSCoordX.SetBackgroundColour('#ffffff')
		except:
			flag = True
			self.txtSCoordX.SetBackgroundColour('#ff0000')

		try:
			cy = int(self.txtSCoordY.GetValue())
			self.txtSCoordY.SetBackgroundColour('#ffffff')
		except:
			flag = True
			self.txtSCoordY.SetBackgroundColour('#ff0000')

		try:
			cz = int(self.txtSCoordZ.GetValue())
			self.txtSCoordZ.SetBackgroundColour('#ffffff')
		except:
			flag = True
			self.txtSCoordZ.SetBackgroundColour('#ff0000')

		self.parent.Refresh()	
		if flag: return

		stype = self.rdBox.GetSelection()
		self.parent.startThread(0, stype, 2, [cx, cy, cz])

	# self.kvantil = -1
	# self.fon = -1
	# self.vremya = -1
	def OnOptions2(self, e):
		def OnClose(e):
			self.parent.Enable()
			frame.Destroy()

		def OnOk(e):
			try:
				self.parent.kvantil = float(txtk.GetValue())
			except:
				self.parent.kvantil = -1

			try:
				self.parent.fon = float(txtf.GetValue())
			except:
				self.parent.fon = -1

			try:
				self.parent.vremya = float(txtt.GetValue())
			except:
				self.parent.vremya = -1

			self.parent.Enable()
			frame.Destroy()

		frame = wx.Frame(None, -1)
		bSizer = wx.BoxSizer( wx.VERTICAL )
		frame.SetSizer( bSizer )

		lblk = wx.StaticText( frame, -1, u"Квантиль",  pos=(0, 0) )
		txtk = wx.TextCtrl( frame, -1, str(self.parent.kvantil),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblk, 0, wx.ALL, 0 )
		bSizer.Add( txtk, 0, wx.ALL, 0 )
		lblf = wx.StaticText( frame, -1, u"Фон, мкР/час",  pos=(0, 0) )
		txtf = wx.TextCtrl( frame, -1, str(self.parent.fon),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblf, 0, wx.ALL, 0 )
		bSizer.Add( txtf, 0, wx.ALL, 0 )
		lblt = wx.StaticText( frame, -1, u"Время, с",  pos=(0, 0) )
		txtt = wx.TextCtrl( frame, -1, str(self.parent.vremya),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblt, 0, wx.ALL, 0 )
		bSizer.Add( txtt, 0, wx.ALL, 0 )

		lblkostyl = wx.StaticText( frame, -1, u"",  pos=(0, 0) )
		bSizer.Add( lblkostyl, 0, wx.ALL, 0 )
		btnOk = wx.Button( frame, -1, u"Применить",  wx.Point(0, 0), wx.Size(100, 25) )
		btnOk.Bind(wx.EVT_BUTTON, OnOk)
		bSizer.Add( btnOk, 0, wx.ALL, 0 )

		self.parent.Disable()
		frame.Show()
		frame.Bind(wx.EVT_CLOSE, OnClose)

	def OnOptions3(self, e):
		def OnClose(e):
			self.parent.Enable()
			frame.Destroy()

		def OnOk(e):
			try:
				self.parent.mnx = int(txtnx.GetValue())
			except:
				self.parent.mnx = 20

			try:
				self.parent.mny = int(txtny.GetValue())
			except:
				self.parent.mny = 20

			try:
				self.parent.mnz = int(txtnz.GetValue())
			except:
				self.parent.mnz = 20

			self.parent.Enable()
			frame.Destroy()

		frame = wx.Frame(None, -1)
		bSizer = wx.BoxSizer( wx.VERTICAL )
		frame.SetSizer( bSizer )

		lblnx = wx.StaticText( frame, -1, u"nx",  pos=(0, 0) )
		txtnx = wx.TextCtrl( frame, -1, str(self.parent.mnx),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblnx, 0, wx.ALL, 0 )
		bSizer.Add( txtnx, 0, wx.ALL, 0 )
		lblny = wx.StaticText( frame, -1, u"ny",  pos=(0, 0) )
		txtny = wx.TextCtrl( frame, -1, str(self.parent.mny),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblny, 0, wx.ALL, 0 )
		bSizer.Add( txtny, 0, wx.ALL, 0 )
		lblnz = wx.StaticText( frame, -1, u"nz",  pos=(0, 0) )
		txtnz = wx.TextCtrl( frame, -1, str(self.parent.mnz),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblnz, 0, wx.ALL, 0 )
		bSizer.Add( txtnz, 0, wx.ALL, 0 )
		lblkostyl = wx.StaticText( frame, -1, u"",  pos=(0, 0) )
		bSizer.Add( lblkostyl, 0, wx.ALL, 0 )
		btnOk = wx.Button( frame, -1, u"Apply",  wx.Point(0, 0), wx.Size(100, 25) )
		btnOk.Bind(wx.EVT_BUTTON, OnOk)
		bSizer.Add( btnOk, 0, wx.ALL, 0 )

		self.parent.Disable()
		frame.Show()
		frame.Bind(wx.EVT_CLOSE, OnClose)

	def OnOptions(self, e):
		def OnClose(e):
			self.parent.Enable()
			frame.Destroy()

		def OnOk(e):
			try:
				self.parent.nx = int(txtnx.GetValue())
			except:
				self.parent.nx = 20

			try:
				self.parent.ny = int(txtny.GetValue())
			except:
				self.parent.ny = 20

			try:
				self.parent.nz = int(txtnz.GetValue())
			except:
				self.parent.nz = 20

			self.parent.Enable()
			frame.Destroy()

		frame = wx.Frame(None, -1)
		bSizer = wx.BoxSizer( wx.VERTICAL )
		frame.SetSizer( bSizer )

		lblnx = wx.StaticText( frame, -1, u"nx",  pos=(0, 0) )
		txtnx = wx.TextCtrl( frame, -1, str(self.parent.nx),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblnx, 0, wx.ALL, 0 )
		bSizer.Add( txtnx, 0, wx.ALL, 0 )
		lblny = wx.StaticText( frame, -1, u"ny",  pos=(0, 0) )
		txtny = wx.TextCtrl( frame, -1, str(self.parent.ny),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblny, 0, wx.ALL, 0 )
		bSizer.Add( txtny, 0, wx.ALL, 0 )
		lblnz = wx.StaticText( frame, -1, u"nz",  pos=(0, 0) )
		txtnz = wx.TextCtrl( frame, -1, str(self.parent.nz),  wx.Point(0, 0), wx.Size(100, 20) )
		bSizer.Add( lblnz, 0, wx.ALL, 0 )
		bSizer.Add( txtnz, 0, wx.ALL, 0 )
		lblkostyl = wx.StaticText( frame, -1, u"",  pos=(0, 0) )
		bSizer.Add( lblkostyl, 0, wx.ALL, 0 )
		btnOk = wx.Button( frame, -1, u"Apply",  wx.Point(0, 0), wx.Size(100, 25) )
		btnOk.Bind(wx.EVT_BUTTON, OnOk)
		bSizer.Add( btnOk, 0, wx.ALL, 0 )

		self.parent.Disable()
		frame.Show()
		frame.Bind(wx.EVT_CLOSE, OnClose)

	def OnSolve(self, e):
		try:
			npoints = int(self.txtKol.GetValue())
		except:
			return
		stype = self.rdBox.GetSelection()
		#print npoints, stype

		if (len(self.parent.blocks)==0 or npoints==0):
			return

		self.parent.startThread(npoints, stype, 0)

	def OnButton(self, event):
		self.parent.switchPanelSet(0)

	def UIEnable(self):
		self.btnBack.Enable()
		self.rdBox.Enable()
		self.txtKol.Enable()
		self.btnSolution.Enable()
		self.btnOnePoint.Enable()
		self.txtSCoordX.Enable()
		self.txtSCoordY.Enable()
		self.txtSCoordZ.Enable()
		self.btnMeshWrite.Enable()
		self.btnOption.Enable()
		self.btnOption2.Enable()
		self.btnOption3.Enable()

	def UIDisable(self):
		self.btnBack.Disable()
		self.rdBox.Disable()
		self.txtKol.Disable()
		self.btnSolution.Disable()
		self.btnOnePoint.Disable()
		self.txtSCoordX.Disable()
		self.txtSCoordY.Disable()
		self.txtSCoordZ.Disable()
		self.btnMeshWrite.Disable()
		self.btnOption.Disable()
		self.btnOption2.Disable()
		self.btnOption3.Disable()

