import os
import sys
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_lib'))

try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    import pyqtgraph as pg
    import numpy as np
    from matplotlib import cm

except ModuleNotFoundError as error:
    if error.name in ('PyQt5', 'pyqtgraph', 'numpy'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')
    else:
        print('\n'+error.msg+'\nPlease use PIP to install\n')
    raise

def roundup(x):
    """Return x (int,float) rounded up to nearest 100.0"""
    return np.ceil(x/100)*100

def convertColormapMPtoPG(cmap):
    """Convert matplotlib.cm.cmap [0.0-1.0] to pyqtgraph.ColorMap [0-255]"""
    pos = np.linspace(0,1,9)
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

class MultiImageWidget(pg.GraphicsLayoutWidget):
    
    sigHLineDragged = QtCore.Signal(object)
    
    def __init__(self,n_images=1,labels=()):
        pg.GraphicsLayoutWidget.__init__(self)
        self._setLabels(labels)
        #Create imageItems
        self.images = [pg.ImageItem(border='w') for i in range(n_images)]     
        #Create histograms
        self.hist = pg.HistogramLUTItem()
        self.hist.gradient.setColorMap(convertColormapMPtoPG(cm.get_cmap('cividis')))
        self.hist_2 = pg.HistogramLUTItem()
        self.hist_2.gradient.setColorMap(convertColormapMPtoPG(cm.get_cmap('bwr')))
        # Create a ViewBox for each image -1
        self.views = [self.addViewBox(invertY=True) for i in range(n_images-1)]
        #Add first histogram
        self.addItem(self.hist)
        #Add last viewbox
        self.views.append(self.addViewBox(invertY=True))
        #Add last histogram 
        self.addItem(self.hist_2)
        #Add horizontal lines
        self.hlines = [pg.InfiniteLine(pos=1,angle=0, movable=True, pen='g') for i in range(n_images)] 
        for i,v in enumerate(self.views):
 
            v.setAspectLocked(False)
            v.addItem(self.images[i])
            v.linkView(v.XAxis,self.views[0])
            v.linkView(v.YAxis,self.views[0])           
            v.setLimits(xMin=-5, 
                        minXRange=10, 
                        yMin=-5,
                        minYRange=10)
            ## Create random image
            data = np.random.normal(size=(1, 600, 600), loc=1024, scale=64).astype(np.uint16)
            self.images[i].setImage(data[0])
            ## Set initial view bounds
            #view[i].setRange(QtCore.QRectF(0, 0, 600, 600))
        
            #Add movable horizontal line for data slicing
            v.addItem(self.hlines[i])
            self.hlines[i].sigDragged.connect(self._update_hline)
            #self.views[0].setMouseEnabled(y=False) # makes user interaction a little easier
            #hline.setValue(300)
            #hline.setZValue(1000) # bring iso line above contrast controls
            #hline.sigPositionChanged.connect(lambda: print(hline.value()))        
        
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
        
    def setData(self,index, im):
        xMax, yMax = im.shape
        self.images[index].setImage(im)
        self.views[index].autoRange()
        self.views[index].setLimits(xMin=-5, xMax=xMax+5,
                                    minXRange=10, 
                                    yMin=-2, yMax=yMax+2,
                                    minYRange=10)
        for hl in self.hlines:
                hl.setValue(0.5)
    
    def _setLabels(self,labels=[]):
        for label in labels:
            self.addLabel(label)
        if len(labels)>0:
            self.nextRow()

    def getHorizontalLineVal(self):
        return self.hlines[0].value()
        
class PlotPatternWidget(pg.PlotWidget):
    
    def __init__(self):
        pg.PlotWidget.__init__(self)
        
        #Set Background color to white
        #self.setBackground('w')
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
        
        #Set Background color to white
        #self.setBackground('w')
        self.setLabel('left','Temperature',units='K')
        self.setLabel('bottom','Frame (#)')
        self.addLegend()
        self.setLimits(xMin=0, xMax=10000,
                       yMin=0, yMax=2500)
        
        #Add vertical line
        self.vline = pg.InfiniteLine(pos=1,angle=90, movable=True, pen='g')
        self.addItem(self.vline)
        self.vline.sigDragged.connect(self._update_vline)
        #Add plots
        self.ptemp = self.plot(x=[0],y=[0], name='Temperature', pen=pg.mkPen(color=(238, 127, 0)), symbol='+', symbolPen=(238, 127, 0))
        
    def setTempData(self,x,y):
        self.ptemp.setData(x,y)
        self.setLimits(xMin=0, xMax=len(x)+1,
               yMin=0, yMax=roundup(y.max()))
    def updateVline(self,pos):
        self.vline.setValue(pos)
        
    def _update_vline(self):
        self.sigVLineDragged.emit(self)

class mainWindow(QtWidgets.QMainWindow, uic.loadUiType(os.path.join(os.path.dirname(__file__), '_lib/_main.ui'))[0]):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setupUi(self)
        
        self.action_OpenCSV.triggered.connect(self.openCSV)
        self.action_OpenPRF.triggered.connect(self.openPRF)
        self.action_OpenXYY.triggered.connect(self.openXYY)

        ###Canvas###
        self.miw = MultiImageWidget(n_images=3,labels=('Observed','Calculated','Scale','Residual','Scale'))
        self.ppw = PlotPatternWidget()
        self.parw = PlotParametersWidget()
        self.verticalLayout_surf.insertWidget(0, self.miw)
        self.verticalLayout_pat.insertWidget(0, self.ppw)
        self.verticalLayout_par.insertWidget(0, self.parw)
        
        self.miw.sigHLineDragged.connect(self.updatePatternPlot)
        self.parw.sigVLineDragged.connect(self.updateHLine)
        
        self.files=[]
        self.temp=[]
        self.sub_plots={}
        
    def updatePatternPlot(self):
        h_val = self.miw.getHorizontalLineVal()
        pos = int(np.clip(round(h_val),0,self.im.shape[2]-1))
        temp = ''
        if self.files:
            if len(self.temp)>0:
                temp = ' - Temperature: {:.0f} K'.format(self.temp[-(pos+1)])
            title = '{}{}'.format(self.files[-(pos+1)],temp)
            self.ppw.setTitle(title)
        self.ppw.setObsData(self.tth,self.im[0,:,pos])
        self.ppw.setCalData(self.tth,self.im[1,:,pos])
        self.ppw.setResData(self.tth,self.im[2,:,pos])
        for key in self.sub_plots:
            self.ppw.setSubplotData(key,self.tth,self.sub_plots[key][pos,:])
        
        if len(self.temp)>0:
            self.parw.setTempData(np.arange(1,self.im.shape[2]+1,1,dtype=float),self.temp)
        self.parw.updateVline(len(self.temp)-h_val+0.5)
        
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
    
    def openPRF(self):
        path = ''
        if not path:
            path = QtCore.QDir.currentPath() 
        files, _ =  QtWidgets.QFileDialog.getOpenFileNames(self, 'Select .prf files', path , '*.prf')
        if files[0].endswith('.prf'):
            progress = self.progressWindow("Reading files", "Abort", 0, len(files),'Refinement Evaluator') #,QtGui.QIcon(":icons/MainIcon.png"))
            im =[[],[],[]]
            temp=[]
            for i, file in enumerate(files):
                progress.setValue(i)
                tth, yobs, ycal, res, bckg, T, excl_reg = self.readPRF(file)
                res = np.array([float(yobs[i])-float(ycal[i]) for i in range(len(yobs))])
                res[excl_reg]=0
                ycal[excl_reg]=np.nan
                im[0].append(yobs)
                im[1].append(ycal)
                im[2].append(res)
                temp.append(T)
                if progress.wasCanceled():
                    break
            im = np.array(im)
            im = np.rot90(im,k=-1,axes=(1,2))
            self.im = im 
            self.tth = tth
            self.files = [f.split('/')[-1][:-4] for f in files]
            if not None in temp:
                self.temp = np.array(temp,dtype=float)
            progress.setValue(len(files))
            self.setMultiImages(tth,im)
            self.removeSubplots()
            self.updatePatternPlot()
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
        excl_reg = (tth < mask[0,0]) | (tth > mask[0,1])
        for i in mask:
            excl_reg = ((tth < i[0]) | (tth > i[1])) & excl_reg
        excl_reg = excl_reg==False
        return(tth, yobs, ycal, res, bckg, temp, excl_reg)

    def openXYY(self):
        path = ''
        if not path:
            path = QtCore.QDir.currentPath() 
        files, _ =  QtWidgets.QFileDialog.getOpenFileNames(self, 'Select .xyy files', path , '*.xyy')
        if files[0].endswith('.xyy'):
            progress = self.progressWindow("Reading files", "Abort", 0, len(files),'Refinement Evaluator') #,QtGui.QIcon(":icons/MainIcon.png"))
            im = [[],[],[]]
            bgr = []
            sub_plots = {}
            temp = []
            for i, file in enumerate(files):
                progress.setValue(i)
                header, data = self.readXYY(file)
                tth = data.pop('tth')
                im[0].append(data.pop('Y_obs'))
                im[1].append(data.pop('Y_calc'))
                im[2].append(data.pop('Y_res'))
                bgr.append(data.pop('Background'))
                for key in data:
                    try:
                        sub_plots[key].append(data[key])
                    except KeyError:
                        sub_plots[key]=[data[key]]
                temp.append(header['Temperature (K)'])
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
            self.files = [f.split('/')[-1][:-4] for f in files]
            self.temp = np.array(temp,dtype=float)
            self.removeSubplots()
            self.sub_plots = {key:np.array(sub_plots[key]) for key in sub_plots}
            progress.setValue(len(files))
            self.setMultiImages(tth,im)
            for key in sub_plots:
                self.ppw.addSubplot(key=key)
            self.updatePatternPlot()
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
        
    def setMultiImages(self,tth,im):
        for i in range(3):
            self.miw.setData(i,im[i])
        
    def progressWindow(self,label,cancel_label,min_val,max_val,window_title,icon=None):
        progress = QtWidgets.QProgressDialog(label, cancel_label, min_val, max_val)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setWindowTitle(window_title)
        if not icon == None:
            progress.setWindowIcon(icon)
        return progress
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = mainWindow()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()