import wx
import time
from threading import Thread
import entity
import copy
from math import pi, sin, cos, atan, atan2
import numpy as np

EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
	"""Define Result Event."""
	win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data."""
	def __init__(self, data, percent):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data
		self.percent = percent

class TestThread(Thread):
	"""Test Worker Thread Class."""

	#----------------------------------------------------------------------
	def __init__(self, parent):
		"""Init Worker Thread Class."""
		Thread.__init__(self)
		self.parent = parent

	#----------------------------------------------------------------------
	def solve(self, npoints, stype, mode, op):
		self.worked = True
		self.npoints = npoints
		self.stype = stype                          #a eto int/mcnp/roma
		self.mode = mode                            #eto zmch/mesh/onepoint
		self.op = op                                #koord one point
		self.cen = [self.parent.scenx, self.parent.sceny, self.parent.scenz]
		self.size = [self.parent.ssizex, self.parent.ssizey, self.parent.ssizez]
		self.blocks = []
		for block in self.parent.blocks:
			self.blocks.append(copy.copy(block))
		self.soluType = self.parent.soluType          #soryan chto tak huevo no eto tipa 2d/3d
		self.blockTypes = []
		for btype in self.parent.blockTypes:
			self.blockTypes.append(copy.copy(btype))

		self.combo = getCombo(len(self.parent.blocks))

		#----------------------------------pizdecki kostyl-------
		#blyaaaaaa neujeli nahui vot tut budet readmeshfromfile
		nBlocks = len(self.blocks)
		self.mesh = [np.zeros((21,39,11)),np.zeros((31,38,9))]  #mcnp, roma

		for i in xrange(2):
			if (i==0):
				meshName='data/mcnp'
				sx=-2000
				sy=-3800
				sz=0
				kx=200
				ky=200
				kz=200
			elif (i==1):
				meshName='data/roman'
				sx=-1400
				sy=-1850
				sz=100
				kx=100
				ky=100
				kz=100

			with open(meshName,'r') as f:
				for line in f:
					st = map(lambda x: float(x),line[:-1].split())
					self.mesh[i][int((st[0]-sx)/kx)][int((st[1]-sy)/ky)][int((st[2]-sz)/kz)]=st[3]*1
		#------------------------------end pizdecki kostyl-------
		#--------------------------------zhx,zhy,zhz dlya 2d mesh------------
		chuvstv=3

		self.zhx=(chuvstv-1)/2
		self.zhy=(chuvstv-1)/2
		self.zhz=(chuvstv-1)/2

		if (self.soluType<3):
			if (self.soluType==0): #0 - XZ
				vec = [0,1,0]
			elif (self.soluType==1): #1 - YZ
				vec = [1,0,0]
			elif (self.soluType==2): #2 - XY
				vec = [0,0,1]

			#povorachivaem vec po i1
			alphax = -self.blocks[0].ugol[0]*pi/180
			alphay = -self.blocks[0].ugol[1]*pi/180
			alphaz = -self.blocks[0].ugol[2]*pi/180

			#povorot alphaz
			x1 = vec[0]*cos(alphaz) - vec[1]*sin(alphaz)
			y1 = vec[0]*sin(alphaz) + vec[1]*cos(alphaz)
			z1 = vec[2]*1
			vec[0], vec[1] = x1*1, y1*1
			#povorot alphay
			x1 = vec[0]*cos(alphay) + vec[2]*sin(alphay)
			y1 = vec[1]*1
			z1 = -vec[0]*sin(alphay) + vec[2]*cos(alphay)
			vec[0], vec[2] = x1*1, z1*1
			#povorot alphax
			x1 = vec[0]*1
			y1 = vec[1]*cos(alphax) - vec[2]*sin(alphax)
			z1 = vec[1]*sin(alphax) + vec[2]*cos(alphax)
			vec[1], vec[2] = y1*1, z1*1
			#v sootv s etim menyaem zh kakoeto
			if (abs(vec[0])>0.2):
				self.zhx = 0
			if (abs(vec[1])>0.2):
				self.zhy = 0
			if (abs(vec[2])>0.2):
				self.zhz = 0
		#-------------------------------- end zhx,zhy,zhz--------------------

		self.start() # start the thread
 
	#----------------------------------------------------------------------
	def run(self):
		"""Run Worker Thread."""
		if (self.mode==0):
			self.zmch()
			wx.PostEvent(self.parent, ResultEvent([0, "Thread finished!"], -1))	# -1 tipa zakonchili, obyazatelno otpravlyat
		elif (self.mode==1):
			self.meshWrite()
			wx.PostEvent(self.parent, ResultEvent([0, "Thread finished!"], -1))
		elif (self.mode==2):
			#t = time.time()
			bufp = self.GetQ(self.op[0],self.op[1],self.op[2])
			#print "proshlo ",time.time()-t
			wx.PostEvent(self.parent, ResultEvent([1, bufp], -1))	# -1 tipa zakonchili, obyazatelno otpravlyat

	#----------------------------------------------------------------------

	def meshWrite(self):
		def nomerTochki(x, y, z, nx, ny):
			return x+y*(nx+1)+z*(nx+1)*(ny+1)

		#nametim tochki po kotorim budem delat setki
		nx = self.parent.mnx
		ny = self.parent.mny
		nz = self.parent.mnz
		size = self.size*1
		if (self.soluType==0): #0 - XZ
			ny = 1
			size[1] = 1
		elif (self.soluType==1): #1 - YZ
			nx = 1
			size[0] = 1
		elif (self.soluType==2): #2 - XY
			nz = 1
			size[2] = 1

		with open('output/mesh.vtk','w') as file:
			file.write('# vtk DataFile Version 1.0\n')
			file.write('Unstructured Grid Example\n')
			file.write('ASCII\n')
			file.write('\n')
			file.write('DATASET UNSTRUCTURED_GRID\n')

			forPerc = 9 + 3*len(self.parent.combo)
			
			nPoints = (nx+1)*(ny+1)*(nz+1)
			file.write('POINTS '+str(nPoints)+' float\n')

			#pishem points
			for k in xrange(nz+1):
				#wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(0.0 + 1.0*k/nz)/forPerc )))
				for j in xrange(ny+1):
					for i in xrange(nx+1):
						x = self.cen[0] + size[0] * ((i+0.0)/nx - 0.5)
						y = self.cen[1] + size[1] * ((j+0.0)/ny - 0.5)
						z = self.cen[2] + size[2] * ((k+0.0)/nz - 0.5)
						file.write(str(x)+' '+str(y)+' '+str(z)+'\n')

			file.write('\n')
			#--------------------------------------------------nCells operac
			#wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(k+1.0*j/ny)/nz )))

			#pishem cells  
			nCells = nx*ny*nz
			file.write('CELLS '+str(nCells)+' '+str(9*(nCells))+'\n')
			for k in xrange(nz):
				#wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(1.0 + 1.0*k/nz)/forPerc )))
				for j in xrange(ny):
					for i in xrange(nx):
						t1 = nomerTochki(i,j,k,nx,ny)
						t2 = nomerTochki(i+1,j,k,nx,ny)
						t3 = nomerTochki(i+1,j+1,k,nx,ny)
						t4 = nomerTochki(i,j+1,k,nx,ny)
						t5 = nomerTochki(i,j,k+1,nx,ny)
						t6 = nomerTochki(i+1,j,k+1,nx,ny)
						t7 = nomerTochki(i+1,j+1,k+1,nx,ny)
						t8 = nomerTochki(i,j+1,k+1,nx,ny)
						file.write( '8 '+str(t1)+' '+str(t2)+' '+str(t3)+' '+str(t4)+' '+str(t5)+' '+str(t6)+' '+str(t7)+' '+str(t8)+'\n')
			
			file.write('\n')
			#--------------------------------------------------nCells operac

			#pishem celltype
			file.write('CELL_TYPES '+str(nCells)+'\n')
			for k in xrange(nz):
				#wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(2.0 + 1.0*k/nz)/forPerc )))
				for j in xrange(ny):
					for i in xrange(nx):
						file.write('12\n')
			
			file.write('\n')
			#--------------------------------------------------nCells operac
			#schitaem vse dannye (pizda)
			file.write('CELL_DATA '+str(nCells)+'\n')

			ebatKakoiKostylMesh = []
			#for r in xrange(3):
			for r in xrange(3):
				self.stype = r
				for k in xrange(nz):
					# wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(3+r + 1.0*k/nz)/forPerc )))
					for j in xrange(ny):
						wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(j + k*ny + r*nz*ny)/(3*ny*nz) )))
						for i in xrange(nx):
							x = self.cen[0] + size[0] * ((i+0.0)/nx - 0.5)
							y = self.cen[1] + size[1] * ((j+0.0)/ny - 0.5)
							z = self.cen[2] + size[2] * ((k+0.0)/nz - 0.5)
							ebatKakoiKostylMesh.append(self.GetQ(x,y,z))
			#--------------------------------------------------nCells*3 operac  //eto neverno
			#pishem vse dannye (pizda)
			#for r in xrange(3):                                            #bejim po vsem modam
			for r in xrange(3):
				for v in xrange(len(self.parent.combo)):                          #bejim po vsem combam (aga imenno stolko u nas setok budet)
					#wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(6+r + 1.0*v/len(self.parent.combo))/forPerc )))
					st = ''
					for i in xrange(len(self.parent.combo[v])):
						if self.parent.combo[v][i]:
							st += str(i+1) + '_'

					if (r==0):
						file.write('SCALARS int_'+st+' float\n')
					elif (r==1):
						file.write('SCALARS mcnp_'+st+' float\n')
					else:
						file.write('SCALARS roma_'+st+' float\n')

					file.write('LOOKUP_TABLE default\n')
					for k in xrange(nz):
						for j in xrange(ny):
							for i in xrange(nx):
								uind = r*nCells + k*ny*nx + j*nx + i
								file.write(str(ebatKakoiKostylMesh[uind].data[v])+'\n')

					file.write('\n')
			#--------------------------------------------------nCells*3*len(self.combo) operac


			#eto zapis maximumov
			#for r in xrange(3):
			for r in xrange(3):
				if (r==0):
					file.write('SCALARS int_max float\n')
				elif (r==1):
					file.write('SCALARS mcnp_max float\n')
				else:
					file.write('SCALARS roma_max float\n')

				file.write('LOOKUP_TABLE default\n')

				for k in xrange(nz):
					#wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(forPerc-4+r + 1.0*k/nz)/forPerc )))
					for j in xrange(ny):
						for i in xrange(nx):
							uind = r*nCells + k*ny*nx + j*nx + i
							file.write(str(ebatKakoiKostylMesh[uind].best)+'\n')

				file.write('\n')
			#--------------------------------------------------nCells*3 operac

		with open('output/blocks.vtk','w') as file:
			file.write('# vtk DataFile Version 1.0\n')
			file.write('Unstructured Grid Example\n')
			file.write('ASCII\n')
			file.write('\n')
			file.write('DATASET UNSTRUCTURED_GRID\n')

			#-----------------------------------------------------------points
			nPoints = len(self.blocks)*8
			file.write('POINTS '+str(nPoints)+' float\n')

			for block in self.blocks:
				for p in block.points:
					file.write(str(p.c[0])+' '+str(p.c[1])+' '+str(p.c[2])+'\n')

			file.write('\n')

			#-----------------------------------------------------------cells
			nCells = len(self.blocks)
			file.write('CELLS '+str(nCells)+' '+str(9*nCells)+'\n')

			for i in xrange(nCells):
				file.write( '8 '+str(i*8+0)+' '+str(i*8+1)+' '+str(i*8+3)+' '+str(i*8+2)+
							' '+str(i*8+4)+' '+str(i*8+5)+' '+str(i*8+7)+' '+str(i*8+6)+'\n')
			file.write('\n')

			#-----------------------------------------------------------cell type
			file.write('CELL_TYPES '+str(nCells)+'\n')
			for i in xrange(nCells):
				file.write('12\n')
			file.write('\n')

			#-----------------------------------------------------------cell data
			file.write('CELL_DATA '+str(nCells)+'\n')
			file.write('SCALARS int_'+'something'+' float\n')
			file.write('LOOKUP_TABLE default\n')
			for i in xrange(nCells):
				file.write(str(0)+'\n')

	def zmch(self):
		nx = self.parent.nx
		ny = self.parent.ny
		nz = self.parent.nz

		size = self.size*1
		if (self.soluType==0): #0 - XZ
			ny = 1
			size[1] = 0
		elif (self.soluType==1): #1 - YZ
			nx = 1
			size[0] = 0
		elif (self.soluType==2): #2 - XY
			nz = 1
			size[2] = 0

		self.bestPoints = []

		for k in xrange(nz):
			for j in xrange(ny):
				wx.PostEvent(self.parent, ResultEvent("percent", int( 100.0*(k+1.0*j/ny)/nz )))  #otpravlyaem procent gotovnosti
				for i in xrange(nx):
					if not self.parent.worked: #znachit stopaem
						return
					x = self.cen[0] + size[0] * ((i+0.0)/nx - 0.5)
					y = self.cen[1] + size[1] * ((j+0.0)/ny - 0.5)
					z = self.cen[2] + size[2] * ((k+0.0)/nz - 0.5)
					#teper v sootvetstvii s metodom poluchim bestpoints

					bufp = self.GetQ(x,y,z)

					if (bufp.worst>0):
						self.bestPoints.append(copy.copy(bufp))
						if (len(self.bestPoints)>self.npoints):
							self.bestPoints.pop(self.bestPoints.index(max(self.bestPoints, key=lambda x: x.best)))

		for p in self.bestPoints:
			self.parent.bestPoints.append(copy.copy(p))
		self.bestPoints = []

	def GetQ(self, x0, y0, z0):
		bp = entity.BestPoints(x0,y0,z0)

		nBlocks = len(self.blocks)
		if (nBlocks==0): return bp
		for i in xrange(nBlocks):
			#--------------------------------------- eto pizdec nepravilno
			alphax = -self.blocks[i].ugol[0]*pi/180
			alphay = -self.blocks[i].ugol[1]*pi/180
			alphaz = -self.blocks[i].ugol[2]*pi/180

			#sdvigaem
			x = x0 - self.blocks[i].coord[0]
			y = y0 - self.blocks[i].coord[1]
			z = z0 - self.blocks[i].coord[2]

			#povorot alphaz
			x1 = x*cos(alphaz) - y*sin(alphaz)
			y1 = x*sin(alphaz) + y*cos(alphaz)
			z1 = z*1
			x, y = x1*1, y1*1
			#povorot alphay
			x1 = x*cos(alphay) + z*sin(alphay)
			y1 = y*1
			z1 = -x*sin(alphay) + z*cos(alphay)
			x, z = x1*1, z1*1
			#povorot alphax
			x1 = x*1
			y1 = y*cos(alphax) - z*sin(alphax)
			z1 = y*sin(alphax) + z*cos(alphax)
			y, z = y1*1, z1*1
			
			#---------------------------------------

			if (self.stype==0):
				bp.data.append(self.GetQint(x, y, z, i))
			else:
				bp.data.append(self.GetQmesh(x, y, z, i))

		#a potom dlya summ blokov
		for i in xrange(nBlocks,len(self.combo)):
			#v sootvetstvii s self.combo[i]
			nn = 0
			ss = 0
			for j in xrange(len(self.combo[i])):
				if (self.combo[i][j] and bp.data[j]>0):
					ss += bp.data[j]
					nn += 1
			if (nn>0):
				bp.data.append(1.0*ss/(nn**0.5))
			else:
				bp.data.append(-1)

		bp.best = max(bp.data)
		bp.worst = min(bp.data)
		return bp

	def GetQint(self, x, y, z, i1):
		if (z<0):
			return -1
		teles = self.otlikIntegBuf(0,0,500,i1)
		return self.blocks[i1].chuvstv*self.otlikIntegBuf(x,y,z,i1)/teles

	def otlikIntegBuf(self, x, y, z, i1):
		otst = self.blockTypes[self.blocks[i1].btype].otst
		r2 = self.blockTypes[self.blocks[i1].btype].r2
		r1 = self.blockTypes[self.blocks[i1].btype].r1

		b = ((z+otst)**2 + (0.5*r1-x)**2)**0.5
		I1 = self.integral(z+otst,b,(0.5*r2-y))-self.integral(z+otst,b,(-0.5*r2-y))
		b = ((z+otst)**2 + (0.5*r1+x)**2)**0.5
		I2 = self.integral(z+otst,b,(0.5*r2-y))-self.integral(z+otst,b,(-0.5*r2-y))
		return (z+otst)*((0.5*r1-x)*I1+(0.5*r1+x)*I2)

	def integral(self, a, b, y):
		if (a*(y*y+b*b)==0 or a*(b*b-a*a)==0): return -1
		return atan((y*(b*b-a*a)**0.5)/(a*(y*y+b*b)**0.5))/(a*(b*b-a*a)**0.5)

	def GetQmesh(self, x, y, z, i1):
		#x, y, z koordinaty v sisteme s blokom
		#self.stype 1=mcnp, 2=roma
		t = self.stype-1


		#nujno naiti dve blijaishie tochki v setke
		p0 = [x,y,z]
		#-----------------------------------------------------------------------------
		#parameters
		if (t==0):
			#mcnp
			nx=21
			ny=39
			nz=11
			#sdvig
			sx=-2000
			sy=-3800
			sz=0

			kx=200
			ky=200
			kz=200
		elif (t==1):
			#roma
			nx=31
			ny=38
			nz=9

			sx=-1400
			sy=-1850
			sz=100

			kx=100
			ky=100
			kz=100

		ii = int(round(1.0*(x-sx)/kx))
		jj = int(round(1.0*(y-sy)/ky))
		kk = int(round(1.0*(z-sz)/kz))

		#-------------------------------delete this--------------------
		# jj=19
		# v=0
		# for i1 in xrange(nx):
		# 	for k1 in xrange(nz):
		# 		tmp=1.0
		# 		for i2 in xrange(nx):
		# 			for k2 in xrange(nz):
		# 				if (i1!=i2 or k1!=k2):
		# 					p_i = [i1*kx+sx,jj*ky+sy,k1*kz+sz]
		# 					p_j = [i2*kx+sx,jj*ky+sy,k2*kz+sz]
		# 					sc1 = ((x-p_j[0])*(p_i[0]-p_j[0]) + 
		# 						(y-p_j[1])*(p_i[1]-p_j[1]) + 
		# 						(z-p_j[2])*(p_i[2]-p_j[2]))
		# 					sc2 = ((p_i[0]-p_j[0])*(p_i[0]-p_j[0]) + 
		# 						(p_i[1]-p_j[1])*(p_i[1]-p_j[1]) + 
		# 						(p_i[2]-p_j[2])*(p_i[2]-p_j[2]))
		# 					tmp=tmp*sc1/sc2
		# 		v += self.mesh[t][i1][jj][k1]*tmp
		# return v
		#-------------------------------end delete---------------------

		v=0
		for i1 in xrange(self.zhx*2+1):
			for j1 in xrange(self.zhy*2+1):
				for k1 in xrange(self.zhz*2+1):
					if (ii-self.zhx+i1>=0 and ii-self.zhx+i1<nx
						and jj-self.zhy+j1>=0 and jj-self.zhy+j1<ny
						and kk-self.zhz+k1>=0 and kk-self.zhz+k1<nz):
						tmp=1.0
						for i2 in xrange(self.zhx*2+1):
							for j2 in xrange(self.zhy*2+1):
								for k2 in xrange(self.zhz*2+1):
									if (ii-self.zhx+i2>=0 and ii-self.zhx+i2<nx
										and jj-self.zhy+j2>=0 and jj-self.zhy+j2<ny
										and kk-self.zhz+k2>=0 and kk-self.zhz+k2<nz):
										if (i1!=i2 or j1!=j2 or k1!=k2):
											p_i = [(ii-self.zhx+i1)*kx+sx,(jj-self.zhy+j1)*ky+sy,(kk-self.zhz+k1)*kz+sz]
											p_j = [(ii-self.zhx+i2)*kx+sx,(jj-self.zhy+j2)*ky+sy,(kk-self.zhz+k2)*kz+sz]
											sc1 = ((x-p_j[0])*(p_i[0]-p_j[0]) + 
												(y-p_j[1])*(p_i[1]-p_j[1]) + 
												(z-p_j[2])*(p_i[2]-p_j[2]))
											sc2 = ((p_i[0]-p_j[0])*(p_i[0]-p_j[0]) + 
												(p_i[1]-p_j[1])*(p_i[1]-p_j[1]) + 
												(p_i[2]-p_j[2])*(p_i[2]-p_j[2]))
											tmp=tmp*sc1/sc2
						v += self.mesh[t][ii-self.zhx+i1][jj-self.zhy+j1][kk-self.zhz+k1]*tmp
		return v



def comboRequr(nabor, n, i1):
	if (n==0):
		return [nabor]
	result = []
	for i in xrange(i1,len(nabor)-n+1):
		nabor[i] = True
		for item in comboRequr(copy.copy(nabor),n-1,i+1):
			result.append(item)
		nabor[i] = False
	return result

def getCombo(n):
	a = []
	for i in xrange(1,n+1):
		for item in comboRequr([False]*n, i, 0):
			a.append(item)
	return a
