import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_lib'))
try:
    from PyQt5 import QtCore, QtWidgets, uic, QtGui
    import pyqtgraph as pg
    import numpy as np
    from matplotlib import cm

except ModuleNotFoundError as error:
    if error.name in ('PyQt5', 'pyqtgraph', 'numpy','matplotlib'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')
    else:
        print('\n'+error.msg+'\nPlease use PIP to install\n')
    raise

def roundup(x):
    """Return x (int,float) rounded up to nearest 100.0"""
    return np.ceil(x/100)*100

def tth2Q(tth,lambd):    
    Q = 4*np.pi*np.sin(np.radians(tth/2))/lambd
    return(Q)

def d2tth(d,lambd):
    tth = np.degrees(np.arcsin(lambd/(2*d)))*2
    return tth

def tth2d(tth,lambd):
    d = lambd/(np.sin(np.radians(tth)/2) * 2)
    return d

def convertColormapMPtoPG(cmap):
    """Convert matplotlib.cm.cmap [0.0-1.0] to pyqtgraph.ColorMap [0-255]"""
    pos = np.linspace(0,1,5)
    colors = [tuple(color*255) for color in cmap(pos)]
    return pg.ColorMap(pos=pos,color=colors)

def findFiles(path,extension='.dat'):
    files = [path+'/'+f for f in os.listdir(path) if f.endswith(extension)]        
    files.sort()
    return files

def AUcolors(exclude=()):
    """Return AU standard colors (light).
    Available colors: 'blue', 'purple', 'cyan', 'turquoise', 'green', 'yellow', 'orange', 'red', 'magenta', and 'gray'.
    
    Keyword arguments:
    exclude -- tuple of strings (default empty)
    """
    AU_colors = {'blue'     :(  0, 61,115),
                 'purple'   :(101, 90,159),
                 'cyan'     :( 55,160,203),
                 'turquoise':(  0,171,164),
                 'green'    :(139,173, 63),
                 'yellow'   :(250,187,  0),
                 'orange'   :(238,127,  0),
                 'red'      :(226,  0, 26),
                 'magenta'  :(226,  0,122),
                 'gray'     :(135,135,135)}
    for ex in exclude:
        AU_colors.pop(ex)
    return AU_colors

def darkPalette():
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText,QtGui.QColor(0, 0, 0))
    #QPalette.setColorGroup(cr, windowText, button, light, dark, mid, text, bright_text, base, window)
    palette.setColorGroup(QtGui.QPalette.Disabled, QtGui.QColor(53, 53, 53),
                                                   QtGui.QColor(0, 0, 0),
                                                   QtGui.QColor(25, 25, 25),
                                                   QtGui.QColor(25, 25, 25),
                                                   QtGui.QColor(25, 25, 25),
                                                   QtGui.QColor(53, 53, 53),
                                                   QtGui.QColor(255, 0, 0),
                                                   QtGui.QColor(25, 25, 25),
                                                   QtGui.QColor(53, 53, 53))
    return palette

class MultiImageWidget(pg.GraphicsLayoutWidget):
    
    sigHLineDragged = QtCore.Signal(object)
    
    def __init__(self,n_images=1,labels=()):
        pg.GraphicsLayoutWidget.__init__(self)
        self._setLabels(labels)
        self.setBackground((25,25,25))
        #Create imageItems
        self.images = [pg.ImageItem(border='w') for i in range(n_images)]     
        #Create histograms
        self.hist = pg.HistogramLUTItem()
        self.hist.gradient.setColorMap(convertColormapMPtoPG(cm.get_cmap('cividis')))
        self.hist_2 = pg.HistogramLUTItem()
        self.hist_2.gradient.setColorMap(convertColormapMPtoPG(cm.get_cmap('bwr')))
        # Create a ViewBox for each image -1
        self.views = [self.addViewBox(invertY=True,name=labels[i]) for i in range(n_images-1)]
        #Add first histogram
        self.addItem(self.hist)
        #Add last viewbox
        self.views.append(self.addViewBox(invertY=True,name=labels[-2]))
        #Add last histogram 
        self.addItem(self.hist_2)
        #Add horizontal lines
        self.hlines = [pg.InfiniteLine(pos=1,angle=0, movable=True, pen='g') for i in range(n_images)]
        #Create axes
        self.axes = [pg.AxisItem('bottom', maxTickLength=5,linkView=v) for v in self.views]
        for i,v in enumerate(self.views):
            v.setAspectLocked(False)
            v.addItem(self.images[i])
            v.linkView(v.XAxis,self.views[0])
            v.linkView(v.YAxis,self.views[0])           
            v.setLimits(xMin=-5, 
                        minXRange=10, 
                        yMin=-5,
                        minYRange=10)

            data = np.zeros((100,100))
            self.images[i].setImage(data)
            ## Set initial view bounds
            #view[i].setRange(QtCore.QRectF(0, 0, 600, 600))
            
            #Add movable horizontal line for data slicing
            v.addItem(self.hlines[i])
            self.hlines[i].sigDragged.connect(self._update_hline)
            #self.views[0].setMouseEnabled(y=False) # makes user interaction a little easier
            #hline.setValue(300)
            #hline.setZValue(1000) # bring iso line above contrast controls
            #hline.sigPositionChanged.connect(lambda: print(hline.value()))        
            
        self.nextRow()
        for i,v in enumerate(self.views):
            #Add axis
            self.addItem(self.axes[i])
            if i == 1:
                self.nextCol()
            
            
        #Register initial horizontal line values
        self._v_old = [round(v.value(),2) for v in self.hlines]
        #Register initial divergent colormap level
        self._l_old = [-1,1]
        #Histogram
        self.hist.setImageItem(self.images[0])
        self.hist.sigLevelsChanged.connect(self._setSharedLevels)
        self.hist.sigLookupTableChanged.connect(self._setSharedLookupTable)
        
        self.hist_2.setImageItem(self.images[-1])
        self.hist_2.sigLevelsChanged.connect(self._setDivergentLevels)
        #self.hist_2.sigLevelChangeFinished.connect(self._setDivergentRange)
        
    def _update_hline(self):
        v_new = [v.value() for v in self.hlines if not round(v.value(),2) in self._v_old]
        for hl in self.hlines:
            try:
                hl.setValue(v_new[0])
            except IndexError:
                pass
        self._v_old = [round(v.value(),2) for v in self.hlines]
        self.sigHLineDragged.emit(self)
        
    def _setSharedLevels(self):
        levels = self.images[0].getLevels()
        for im in self.images[1:2]:
            im.setLevels(levels)

    def _setSharedLookupTable(self):
        lut = self.images[0].lut
        for im in self.images[1:2]:
            im.setLookupTable(lut)
    
    def _setDivergentLevels(self):
        new = [l for l in self.hist_2.getLevels() if not l in self._l_old]
        if len(new)>0:
            level = abs(new[0])
            self.hist_2.setLevels(min=-level ,max=level)
        self._l_old = self.hist_2.getLevels()
    
    def _setDivergentRange(self):
        _,level = self.hist_2.getLevels()
        self.hist_2.setHistogramRange(-roundup(level),roundup(level))
    
    def setData(self,index, im):
        xMax, yMax = im.shape
        self.images[index].setImage(im)
        self.views[index].autoRange()
        self.views[index].setLimits(xMin=-5, xMax=xMax+5,
                                    minXRange=10, 
                                    yMin=-2, yMax=yMax+2,
                                    minYRange=10)
        for hl in self.hlines:
                hl.setValue(yMax-0.5)
                hl.setBounds((-1,yMax+1))
    
    def setTicks(self, index, ticks):
        """
        [
            [ (majorTickValue1, majorTickString1), (majorTickValue2, majorTickString2), ... ],
            [ (minorTickValue1, minorTickString1), (minorTickValue2, minorTickString2), ... ],
            ...
        ]
        """
        self.axes[index].setTicks(ticks)
          
    def _setLabels(self,labels=[]):
        for label in labels:
            self.addLabel(label,color='w')
        if len(labels)>0:
            self.nextRow()

    def getHorizontalLineVal(self):
        return self.hlines[0].value()
        
class PlotPatternWidget(pg.PlotWidget):
    
    def __init__(self):
        pg.PlotWidget.__init__(self)
        
        #Set Background color to gray
        self.setBackground((25,25,25))
        self.setLabel('left','Intensity (a.u.)')
        self.setLabel('bottom','2θ (°)')
        self.addLegend()
        self.setLimits(xMin=0, xMax=180)
        #Add plots
        self.pobs = self.plot(x=[0],y=[0], name='Observed', pen=None, symbol='o', symbolPen='r', symbolSize=2)
        self.pcal = self.plot(x=[0],y=[0], name='Calculated')
        self.pres = self.plot(x=[0],y=[0], name='Residual', pen=pg.mkPen(color='b', width=0.5))
        
        self.psub = {}
    
        self.colors = AUcolors(exclude=('blue','red','gray'))
        
    def addSubplot(self,key=None):
        try:
            color = self.colors.popitem()[1]
        except KeyError:
            color = AUcolors(exclude=('blue','red','gray'))
        pen = pg.mkPen(color=color, style=QtCore.Qt.DashLine)
        self.psub[key]=self.plot(x=[0],y=[0], name=key, pen=pen)

    def removeSubplots(self):
        for item in self.psub.values():
            self.removeItem(item)
        self.colors = AUcolors(exclude=('blue','red','gray'))
        
    def setSubplotData(self,key,x,y):    
        self.psub[key].setData(x,y)
        
    def setObsData(self,x,y):
         self.pobs.setData(x,y)
    
    def setCalData(self,x,y):
        #Remove NAN values 
        x = x[~np.isnan(y)]
        y = y[~np.isnan(y)]
        self.pcal.setData(x,y)    
        
    def setResData(self,x,y):
         self.pres.setData(x,y)
         
class PlotParametersWidget(pg.PlotWidget):
    
    sigVLineDragged = QtCore.Signal(object)
    
    def __init__(self):
        pg.PlotWidget.__init__(self)
        
        #Set Background color to gray
        self.setBackground((25,25,25))
        self.setLabel('left','Temperature (K)')
        self.setLabel('bottom','Frame (#)')
        self.legend = self.addLegend()
        self.setLimits(xMin=0, xMax=10000,
                       yMin=0, yMax=2500)
        #self.enableAutoRange(enable=True)
        #Add vertical line
        self.vline = pg.InfiniteLine(pos=1,angle=90, movable=True, pen='g')
        self.addItem(self.vline)
        self.vline.sigDragged.connect(self._update_vline)

        #Create first plotItem
        self.p1 = self.plotItem
        self.p1.setLabels(left='Temperature (K)')
        #Hide second x-axis until data is added with setRwpData()
        self.p1.showAxis('right', show=False)
        rp_label = '<html><head/><body><p>R<span style=" vertical-align:sub;">p</span></p></body></html>'
        rwp_label = '<html><head/><body><p>R<span style=" vertical-align:sub;">wp</span></p></body></html>'
        #self.p1.getAxis('right').setLabel(rwp_label)        
        self.p1.getAxis('right').setLabel('R-value')   
        
        #Create a new ViewBox, link the right axis to its coordinate system
        self.v2 = pg.ViewBox()
        self.p1.scene().addItem(self.v2)
        self.p1.getAxis('right').linkToView(self.v2)
        self.v2.setXLink(self.p1)
        self.v2.setLimits(yMin=0, yMax=1000)
        
        #Add temperature plot to PlotItem
        self.ptemp = self.p1.plot(x=[-1],y=[-1], name='Temperature', pen=pg.mkPen(color=(238, 127, 0)), symbol='+', symbolPen=(238, 127, 0))
        #Create Rwp plot and add to second viewbox
        self.prp = pg.PlotDataItem(x=[-1],y=[-1], name=rp_label, pen=pg.mkPen(color=(  0, 61,115)), symbol='+', symbolPen=(  0, 61,115))
        
        #Create Rwp plot and add to second viewbox
        self.prwp = pg.PlotDataItem(x=[-1],y=[-1], name=rwp_label, pen=pg.mkPen(color=(139,173, 63)), symbol='+', symbolPen=(139,173, 63))
        self.v2.addItem(self.prp)
        self.v2.addItem(self.prwp)
        
        self._updateViews()
        self.p1.vb.sigResized.connect(self._updateViews)        
        
    ## Handle view resizing 
    def _updateViews(self):
        ## view has resized; update auxiliary views to match
        self.v2.setGeometry(self.p1.vb.sceneBoundingRect())
        self.v2.linkedViewChanged(self.p1.vb, self.v2.XAxis)
        
    def clearPlot(self):
        self.ptemp.setData([-1],[-1])
        self.prwp.setData([-1],[-1])
        self.prp.setData([-1],[-1])
        self.legend.clear()
        
    def setTempData(self,x,y):
        self.legend.addItem(self.ptemp, self.ptemp.name())
        self.ptemp.setData(x,y)
        yMax = roundup(y.max())
        if yMax < 1:
            yMax = 1.0
        self.setLimits(xMin=-2, xMax=len(x)+2,
               yMin=0, yMax=yMax)
        self.vline.setBounds((-1,len(x)+1))
        self.autoRange()
    
    def setRwpData(self,x,y):
        self.legend.addItem(self.prwp, self.prwp.name())
        self.p1.showAxis('right',show=True)
        self.prwp.setData(x,y)
        
    def setRpData(self,x,y):
        self.legend.addItem(self.prp, self.prp.name())
        self.p1.showAxis('right',show=True)
        self.prp.setData(x,y)
        self.v2.autoRange()
        
    def updateVline(self,pos):
        self.vline.setValue(pos)
        
    def _update_vline(self):
        self.sigVLineDragged.emit(self)

class mainWindow(QtWidgets.QMainWindow, uic.loadUiType(os.path.join(os.path.dirname(__file__), '_lib/_main.ui'))[0]):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setupUi(self)
        
        self.actionUpdate.triggered.connect(self.updateFiles)
        self.action_OpenCSV.triggered.connect(self.openCSV)
        self.action_OpenDAT.triggered.connect(self.openDAT)
        self.action_OpenPRF.triggered.connect(self.openPRF)
        self.action_OpenXYE.triggered.connect(self.openXYE)
        self.action_OpenXYY.triggered.connect(self.openXYY)
        self.actionAbout.triggered.connect(self.aboutBox)
        
        ###Canvas###
        self.miw = MultiImageWidget(n_images=3,labels=('Observed','Calculated','Scale','Residual','Scale'))
        self.ppw = PlotPatternWidget()
        self.parw = PlotParametersWidget()
        self.verticalLayout_surf.insertWidget(0, self.miw)
        self.verticalLayout_pat.insertWidget(0, self.ppw)
        self.verticalLayout_par.insertWidget(0, self.parw)
        
        self.miw.sigHLineDragged.connect(self.updatePatternPlot)
        self.parw.sigVLineDragged.connect(self.updateHLine)
        for image in self.miw.images:
            image.hoverEvent = self.imageHoverEvent
        self.ppw.pobs.getViewBox().hoverEvent = self.patternHoverEvent
        self.parw.ptemp.getViewBox().hoverEvent = self.parameterHoverEvent
        
        self.im = np.zeros((3,100,100))
        self.tth = np.arange(0,100,1)
        self.files = ['']
        self.temp = []
        self.rp = []
        self.rwp = []
        self.lambd = None
        self.sub_plots={}
    
    def imageHoverEvent(self,event):
        if event.isExit():
            self.statusbar.clearMessage()
            return
        datapoints  = self.im.shape[1]
        frames = self.im.shape[2]
        pos = event.pos()
        #vpos = self.imw_im.view.mapToView(pos)
        i, j = pos.x(), pos.y()
        i = int(np.clip(i, 0, datapoints - 1))
        j = int(np.clip(j, 0, frames - 1))
        tth = self.tth[i]
        obs, calc, res = [val[i, j] for val in self.im]
        if isinstance(self.lambd,float):
            Q = tth2Q(tth,self.lambd)
            d = tth2d(tth,self.lambd)
            self.statusbar.showMessage('Frame: {:4d}  |  2θ: {:6.2f} °  |  Q: {:6.3f} Å⁻¹ |  d: {:6.3f} Å  |  Observed: {:8.1f}  |  Calculated: {:8.1f}  |  Residual: {:8.1f}  |'.format(frames-j,tth,Q,d,obs,calc,res))
        else:
            self.statusbar.showMessage('Frame: {:4d}  |  2θ: {:6.2f} °  |  Observed: {:8.1f}  |  Calculated: {:8.1f}  |  Residual: {:8.1f}  |'.format(frames-j,tth,obs,calc,res))
    
    def patternHoverEvent(self,event):
        if event.isExit():
            self.statusbar.clearMessage()
            return
        pos = event.pos()
        vpos = self.ppw.pobs.getViewBox().mapToView(pos)
        tth, I = vpos.x(), vpos.y()
        if isinstance(self.lambd,float):
            Q = tth2Q(tth,self.lambd)
            d = tth2d(tth,self.lambd)
            self.statusbar.showMessage('2θ: {:6.2f} °  |  Q: {:6.3f} Å⁻¹ |  d: {:6.3f} Å  |  Intensity: {:8.1f}  |'.format(tth,Q,d,I))
        else:    
            self.statusbar.showMessage('2θ: {:6.2f}  |  Intensity: {:8.1f}  |'.format(tth,I))

    def parameterHoverEvent(self,event):
        if event.isExit():
            self.statusbar.clearMessage()
            return
        pos = event.pos()
        vpos = self.parw.ptemp.getViewBox().mapToView(pos)
        f, T = vpos.x(), vpos.y()
        if len(self.rwp)>0 and len(self.rp)>0:
            i = np.clip(f, 0, self.rwp.shape[0]-1)
            rwp = self.rwp[int(i)]
            rp = self.rp[int(i)]
            self.statusbar.showMessage('Frame: {:4.0f}  |  Temperature: {:6.1f} K  |  Rwp: {:6.2f}  |  Rp: {:6.2f}  |'.format(f,T,rwp,rp))
        elif len(self.rwp)>0:
            i = np.clip(f, 0, self.rwp.shape[0]-1)
            rwp = self.rwp[int(i)]
            self.statusbar.showMessage('Frame: {:4.0f}  |  Temperature: {:6.1f} K  |  Rwp: {:6.2f}  |'.format(f,T,rwp))
        elif len(self.rp)>0:
            i = np.clip(f, 0, self.rp.shape[0]-1)
            rp = self.rp[int(i)]
            self.statusbar.showMessage('Frame: {:4.0f}  |  Temperature: {:6.1f} K  |  Rp: {:6.2f}  |'.format(f,T,rp))
        
        else:
            self.statusbar.showMessage('Frame: {:4.0f}  |  Temperature: {:6.1f} K  |'.format(f,T))

    def updateFiles(self):
        files = self.files
        if files[0].endswith('.prf'):
            self.openPRF(files)
        elif files[0].endswith('.xyy'):
            self.openXYY(files)
        elif files[0].endswith('.dat'):
            self.openDAT(files)
        elif files[0].endswith('.xye'):
            self.openXYE(files)
        return
    
    def aboutBox(self):
        text = ['<html><head/>',
                    '<body>',
                        '<p align="center">',
                            '<span style=" font-size:10pt; font-weight:600;">',
                                'Refinement Evaluator<br/>',
                            '</span>',
                            'by<br/>',
                            'Frederik H Gjørup<br/>',
                            'Department of Chemistry<br/>',
                            'Aarhus University<br/>',
                            'August 2020',
                        '</p>',
                    '</body>',
                '</html>']
        QtWidgets.QMessageBox.about(self,'About',''.join(text))
        
    def updatePatternPlot(self):
        h_val = self.miw.getHorizontalLineVal()
        pos = int(np.clip(round(h_val),0,self.im.shape[2]-1))
        temp = ''
        if not self.files[0] == '':
            if len(self.temp)>0:
                temp = ' - Temperature: {:.0f} K'.format(self.temp[-(pos+1)])
            title = '{}{}'.format(self.files[-(pos+1)].split('/')[-1][:-4],temp)
            self.ppw.setTitle(title)
        self.ppw.setObsData(self.tth,self.im[0,:,pos])
        self.ppw.setCalData(self.tth,self.im[1,:,pos])
        self.ppw.setResData(self.tth,self.im[2,:,pos])
        for key in self.sub_plots:
            self.ppw.setSubplotData(key,self.tth,self.sub_plots[key][-(pos+1),:])
        
        self.parw.updateVline(len(self.temp)-h_val+0.5)
    
    def updateParameterPlot(self):
        frames = np.arange(1,self.im.shape[2]+1,1,dtype=float)
        self.parw.clearPlot()
        if len(self.temp)>0:
            if not np.all(self.temp==0.0):
                self.parw.setTempData(frames,self.temp)
            else:
                self.parw.setTempData(frames,np.full(frames.shape[0],-1.0,dtype=float))
        if len(self.rp)>0:
            self.parw.setRpData(frames,self.rp)
        if len(self.rwp)>0:
            self.parw.setRwpData(frames,self.rwp)
    
    def setMultiImages(self,tth,im):
        #Generate ticks for images
        ticks = self.generateTicks(tth)        
        for i in range(3):
            self.miw.setData(i,im[i])
            self.miw.setTicks(i,ticks)
            
    def generateTicks(self,tth):
        """Generate ticks assuming equidistant steps.
        return:
                [[ (majorTickValue1, majorTickString1), (majorTickValue2, majorTickString2), ... ],
            [ (minorTickValue1, minorTickString1), (minorTickValue2, minorTickString2), ... ]]
        """
        if tth[-1]-self.tth[0] < 15:
            scale = 1
        elif tth[-1]-tth[0] < 30:
            scale = 2
        elif tth[-1]-tth[0] < 60:
            scale = 5
        else:
            scale = 10
        mn = np.ceil(tth[0]/scale)*scale
        mx = np.floor(tth[-1]/scale)*scale
        first = np.argmin(np.abs(tth-mn))
        last = np.argmin(np.abs(tth-mx))
        step = scale/np.mean(np.diff(tth))
        val = np.arange(first-step,last+step,step)
        minor = np.linspace(val[0],val[-1]+step,(len(val))*10+1)
        s = np.arange(mn-scale,mx+scale*2,scale)
        ticks = [[(v,'{:.0f}'.format(s[i])) for i, v in enumerate(val)],[(m,'') for m in minor]]
        return ticks
    
    
    def updateHLine(self):
        val = len(self.temp)-self.parw.vline.value()
        self.miw.hlines[0].setValue(val+0.5)
        self.miw._update_hline()
        
    def removeSubplots(self):
        self.sub_plots={}
        self.ppw.removeSubplots()
####################################################################################################
##                                   Read data methods                                            ##
####################################################################################################
    def openCSV(self):
        path = ''
        if not path:
            path = QtCore.QDir.currentPath() 
        path, _ =  QtWidgets.QFileDialog.getOpenFileName(self, 'Open .csv file', path , '*.csv')
        path = path.replace('_meta.csv','.csv')
        if path.endswith('.csv'):
            tth, im_obs = self.readMatrix(path)
            im = np.full((3,im_obs.shape[0],im_obs.shape[1]),0, dtype=float)
            im[0,:,:] = im_obs
            self.im = im
            self.tth = tth
            self.setMultiImages(tth,self.im)
            self.removeSubplots()
            self.updatePatternPlot()
        else:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open .csv file!\nFile: '+path)    

    def readMatrix(self,fname):
        with open(fname,'r') as f:
           content = f.read()
        c = content.strip().split('\n')
        rows = len(c)
        tth = np.array(c[0].strip().split(','), dtype=float)
        im = np.array(','.join(c[1:]).strip().split(','), dtype = float).reshape(rows-1,len(tth))
        im = np.rot90(im,k=-1)
        return tth, im
    
    def openPRF(self,files=None):
        if not isinstance(files,list):
            path = ''
            if not path:
                path = QtCore.QDir.currentPath() 
            files, _ =  QtWidgets.QFileDialog.getOpenFileNames(self, 'Select .prf files', path , '*.prf')
        else:
            path = os.path.dirname(files[0])
        if len(files)<1:
            return
        if files[0].endswith('.prf'):
            progress = self.progressWindow("Reading files", "Abort", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
            im =[[],[],[]]
            temp=[]
            rp = []
            for i, file in enumerate(files):
                progress.setValue(i)
                tth, yobs, ycal, res, bckg, T, excl_reg, lambd = self.readPRF(file)
                res = np.array([float(yobs[i])-float(ycal[i]) for i in range(len(yobs))])
                res[excl_reg]=0
                ycal[excl_reg]=np.nan
                im[0].append(yobs)
                im[1].append(ycal)
                im[2].append(res)
                temp.append(T)
                rp.append(np.sum(abs(res[excl_reg==False]))/np.sum(yobs[excl_reg==False])*100)
                if progress.wasCanceled():
                    break
            im = np.array(im)
            im = np.rot90(im,k=-1,axes=(1,2))
            
            self.im = im 
            self.tth = tth
            self.files =  files
            self.rp = np.array(rp,dtype=float)
            self.rwp = []            
            if not None in temp:
                self.temp = np.array(temp,dtype=float)
            else:
                self.temp = []
            self.lambd = lambd[0]

            progress.setValue(len(files))
            self.setMultiImages(tth,im)
            self.removeSubplots()
            self.updatePatternPlot()
            self.updateParameterPlot()
            self.actionUpdate.setEnabled(True)
        else:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open .prf files!\npath: '+path)    
            
    def readPRF(self,fname):      
        header = []
        mask = [] #Excluded region
        content = []
        with open(fname) as file:
            for i in range(3):
                header.append(file.readline())
            try:
                temp = float(header[0].split()[-1])
            except ValueError:
                temp = None
            lambd =  [float(l) for l in header[1].split()[2:4]]
            for i in range(int(header[2].split()[-1])):
                mask.append(file.readline().split())
            file.readline()
            for i in range(int(header[1].split()[1])):
                content.append(file.readline().split()[0:5])
        content = np.array(content, dtype = float)
        
        tth = content[:,0]
        yobs = content[:,1]
        ycal = content[:,2]
        res = content[:,3]
        bckg = content[:,4]
        mask = np.array(mask, dtype = float)
        if len(mask)>0:
            excl_reg = (tth < mask[0,0]) | (tth > mask[0,1])
        else:
            excl_reg = np.full(tth.shape[0],True)
        for i in mask:
            excl_reg = ((tth < i[0]) | (tth > i[1])) & excl_reg
        #Invert True/False
        excl_reg = excl_reg==False
        return tth, yobs, ycal, res, bckg, temp, excl_reg, lambd

    def openXYY(self,files=None):
        if not isinstance(files,list):
            path = ''
            if not path:
                path = QtCore.QDir.currentPath() 
            files, _ =  QtWidgets.QFileDialog.getOpenFileNames(self, 'Select .xyy files', path , '*.xyy')
        else:
            path = os.path.dirname(files[0])
        if len(files)<1:
            return
        if files[0].endswith('.xyy'):
            progress = self.progressWindow("Reading files", "Abort", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
            im = [[],[],[]]
            bgr = []
            sub_plots = {}
            rwp = []
            temp = []
            rp = []
            for i, file in enumerate(files):
                progress.setValue(i)
                header, data = self.readXYY(file)
                tth = data.pop('tth')
                yobs = data.pop('Y_obs')
                ycal = data.pop('Y_calc')
                res = data.pop('Y_res')
                im[0].append(yobs)
                im[1].append(ycal)
                im[2].append(res)
                bgr.append(data.pop('Background'))
                for key in data:
                    try:
                        sub_plots[key].append(data[key])
                    except KeyError:
                        sub_plots[key]=[data[key]]
                rwp.append(header['R_wp'])
                temp.append(header['Temperature (K)'])
                rp.append(np.sum(abs(res))/np.sum(yobs)*100)
                if progress.wasCanceled():
                    break
            """
            for i, file in enumerate(files):
                progress.setValue(i)
                header, data = self.readXYY(file)
                tth = data['tth']
                im[0].append(data['Y_obs'])
                im[1].append(data['Y_calc'])
                im[2].append(data['Y_res'])
                temp.append(header['Temperature (K)'])
                if progress.wasCanceled():
                    break
            """
            im = np.array(im)
            im = np.rot90(im,k=-1,axes=(1,2))
            self.im = im 
            self.tth = tth
            self.files = files
            self.rwp = np.array(rwp,dtype=float)
            self.rp = np.array(rp,dtype=float)
            self.temp = np.array(temp,dtype=float)
            self.lambd = float(header['Wavelength (Ã…)'])
            self.removeSubplots()
            self.sub_plots = {key:np.array(sub_plots[key]) for key in sub_plots}
            progress.setValue(len(files))
            self.setMultiImages(tth,im)
            for key in sub_plots:
                self.ppw.addSubplot(key=key)
            self.updatePatternPlot()
            self.updateParameterPlot()
            self.actionUpdate.setEnabled(True)
        else:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open .xyy files!\npath: '+path)    
            
    def readXYY(self, fname):
        """Read *.xyy files from TOPAS parametric refinement. Return header and parameter dictionaries"""
        line=''
        header = []
        with open(fname,'r') as f:
            while not 'END OF HEADER' in line:
               line = f.readline() 
               header.append(line)
            parameters = f.readline().split()
            data = np.loadtxt(f,dtype=float)
        h = {'Filename':header[0]}
        comments = header.index('COMMENTS\n')
        h['Comments']=''.join(header[comments+1:-1])
        for s in header[1:comments]:
            if ':' in s:
                key, value = s.split(':')
            h[key]=value
        dic = {p:data[:,i] for i,p in enumerate(parameters)}
        return h, dic
    
    def openDAT(self,files=None):
        if not isinstance(files,list):
            path = ''
            if not path:
                path = QtCore.QDir.currentPath() 
            files, _ =  QtWidgets.QFileDialog.getOpenFileNames(self, 'Select .dat files', path , '*.dat')
        else:
            path = os.path.dirname(files[0])
        if len(files)<1:
            return
        if files[0].endswith('.dat'):
            progress = self.progressWindow("Reading files", "Abort", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
            im =[[],[],[]]
            temp=[]
            for i, file in enumerate(files):
                progress.setValue(i)
                tth,yobs,T,lambd, _, _ = self.readDat(file)
                im[0].append(yobs)
                im[1].append(np.full(yobs.shape,0,dtype=float))
                im[2].append(np.full(yobs.shape,0,dtype=float))
                temp.append(T)
                if progress.wasCanceled():
                    break
            im = np.array(im)
            im = np.rot90(im,k=-1,axes=(1,2))
            self.im = im 
            self.tth = tth
            self.files =  files
            if not None in temp:
                self.temp = np.array(temp,dtype=float)
            else:
                self.temp = []
            self.lambd = lambd
            self.rwp = []
            progress.setValue(len(files))
            self.setMultiImages(tth,im)
            self.removeSubplots()
            self.updatePatternPlot()
            self.updateParameterPlot()
            self.actionUpdate.setEnabled(True)
        else:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open .dat file!\nFile: '+path)  
    
    def readDat(self, fname,temp=None,lamb=None,ts=None,t=None):      
        with open(fname,'r') as file:
            for i in range(6):
                line = file.readline()
                if line.startswith('TEMP'):
                    temp = line.split()[-1]
                elif line.startswith('!Wavelength:'):
                    lamb = float(line.split()[-1])
                elif line.startswith('!Timestamp:'):
                    ts = ' '.join(line.split()[1:])
                elif line.startswith('!Acquisition'):
                    t = float(line.split()[-3])*float(line.split()[-1])
                if i == 3 and len(line.split())>=10:
                    #If alternativ .dat format:
                    tth, I, _ = self.readDatAlt(fname)
                    return tth,I,temp,lamb,ts,t 
            content = np.loadtxt(file, skiprows = 0)
        tth, I = content[:,0], content[:,1]
        return tth,I,temp,lamb,ts,t
    
    def readDatAlt(self,fname):
        """Alternative .dat format using start, step, stop."""
        with open(fname,'r') as file:
            name = file.readline().strip()
            header = file.readline()
            start,step,stop = [float(x) for x in file.readline().split()[0:3]]
            content = file.read()
        tth = np.arange(start,stop+step,step)
        I = content.split()[:len(tth)]
        sig = content.split()[len(tth):len(tth)*2]
        if len(sig)<len(tth):
            sig = np.array(I)**0.5
        return tth, np.array(I,dtype=float), np.array(sig,dtype=float)
    
    def openXYE(self,files=None):
        if not isinstance(files,list):
            path = ''
            if not path:
                path = QtCore.QDir.currentPath() 
            files, _ =  QtWidgets.QFileDialog.getOpenFileNames(self, 'Select .xye files', path , '*.xye')
        else:
            path = os.path.dirname(files[0])
        if len(files)<1:
            return
        if files[0].endswith('.xye'):
            progress = self.progressWindow("Reading files", "Abort", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
            im =[[],[],[]]
            for i, file in enumerate(files):
                progress.setValue(i)
                tth,yobs,_ = self.readXYE(file)
                im[0].append(yobs)
                im[1].append(np.full(yobs.shape,0,dtype=float))
                im[2].append(np.full(yobs.shape,0,dtype=float))
                if progress.wasCanceled():
                    break
            im = np.array(im)
            im = np.rot90(im,k=-1,axes=(1,2))
            self.im = im 
            self.tth = tth
            self.files =  files
            self.rwp = []
            progress.setValue(len(files))
            self.setMultiImages(tth,im)
            self.removeSubplots()
            self.updatePatternPlot()
            self.updateParameterPlot()
            self.actionUpdate.setEnabled(True)
        else:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open .xye file!\nFile: '+path) 
    
    def readXYE(self,fname):
        sig=None
        with open(fname,'r') as file:
            content = np.loadtxt(file, skiprows = 0)
        if content.shape[1]<3:
            tth, I = content[:,0], content[:,1]
        else:
            tth, I, sig = content[:,0], content[:,1], content[:,2]
        return tth, I, sig
    
    def progressWindow(self,label,cancel_label,min_val,max_val,window_title,icon=None):
        progress = QtWidgets.QProgressDialog(label, cancel_label, min_val, max_val)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setWindowTitle(window_title)
        progress.setMinimumDuration(1000)#milliseconds
        if not icon == None:
            progress.setWindowIcon(icon)
        return progress
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setPalette(darkPalette())
    ui = mainWindow()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()