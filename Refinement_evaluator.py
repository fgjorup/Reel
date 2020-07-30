import os
import sys
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_lib'))

try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    import pyqtgraph as pg
    import numpy as np

except ModuleNotFoundError as error:
    if error.name in ('PyQt5', 'pyqtgraph', 'numpy'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')
    else:
        print('\n'+error.msg+'\nPlease use PIP to install\n')
    raise



def findFiles(path,extension='.dat'):
    files = [path+'/'+f for f in os.listdir(path) if f.endswith(extension)]        
    files.sort()
    return files

def readXYY():
    

    return

class MultiImageWidget(pg.GraphicsLayoutWidget):
    
    def __init__(self,n_images=1,labels=()):
        pg.GraphicsLayoutWidget.__init__(self)
        self._setLabels(labels)
        # Create a ViewBox for each image
        self.views = [self.addViewBox() for i in range(n_images)]
        self.images = [pg.ImageItem(border='w') for i in range(n_images)]   
        self.hlines = [pg.InfiniteLine(angle=0, movable=True, pen='g') for i in range(n_images)] 
        for i,v in enumerate(self.views):
 
            v.setAspectLocked(False)
            v.addItem(self.images[i])
            v.linkView(v.XAxis,self.views[0])
            v.linkView(v.YAxis,self.views[0])           
            v.setLimits(xMin=0, 
                        minXRange=10, 
                        yMin=0,
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
        
        #Add histogram of first image to layout
        self.hist = pg.HistogramLUTItem()
        self.hist.setImageItem(self.images[0])
        self.addItem(self.hist)
        self.hist.sigLevelsChanged.connect(self._setSharedLevels)
        self.hist.sigLookupTableChanged.connect(self._setSharedLookupTable)
        

    def _update_hline(self):
        v_new = [v.value() for v in self.hlines if not round(v.value(),2) in self._v_old]
        for hl in self.hlines:
            try:
                hl.setValue(v_new[0])
            except IndexError:
                pass
        self._v_old = [round(v.value(),2) for v in self.hlines]
    
    def _setSharedLevels(self):
        levels = self.images[0].getLevels()
        for im in self.images[1:]:
            im.setLevels(levels)

    def _setSharedLookupTable(self):
        lut = self.images[0].lut
        for im in self.images[1:]:
            im.setLookupTable(lut)
    
    def setData(self,index, im):
        xMax, yMax = im.shape
        self.images[index].setImage(im)
        self.views[index].autoRange()
        self.views[index].setLimits(xMin=0, xMax=xMax,
                                    minXRange=10, 
                                    yMin=0, yMax=yMax,
                                    minYRange=10)

    
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
        self.setLimits(xMin=0, xMax=180,
                       yMin=0)
        #Add plots
        self.pobs = self.plot(x=[0],y=[0], name='Observed', pen=None, symbol='o', symbolPen='r', symbolSize=2)
        self.pcal = self.plot(x=[0],y=[0], name='Calculated')
        self.pres = self.plot(x=[0],y=[0], name='Residual', pen=pg.mkPen(color='b', width=0.5))
        
        
    def setObsData(self,x,y):
         self.pobs.setData(x,y)
    
    def setCalData(self,x,y):
         self.pcal.setData(x,y)    
        
    def setResData(self,x,y):
         self.pres.setData(x,y)

class mainWindow(QtWidgets.QMainWindow, uic.loadUiType(os.path.join(os.path.dirname(__file__), '_lib/_main.ui'))[0]):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setupUi(self)
        
        self.action_OpenCSV.triggered.connect(self.openCSV)
        


        ###Canvas###
        self.miw = MultiImageWidget(n_images=3,labels=('Observed','Calculated','Residual'))
        self.pw1 = PlotPatternWidget()
        self.pw2 = pg.PlotWidget()
        self.verticalLayout_surf.insertWidget(0, self.miw)
        self.verticalLayout_pat.insertWidget(0, self.pw1)
        self.verticalLayout_par.insertWidget(0, self.pw2)
        
        self.miw.hlines[i].sigDragged.connect(self.updatePatternPlot)
        
        
    def updatePatternPlot(self):
        print(self.miw.getHorizontalLineVal())        



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
            self.setMultiImages(path)
        else:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open .csv file!\nFile: '+path)    



    def readMatrix(self,fname):
        with open(fname,'r') as f:
           content = f.read()
        c = content.strip().split('\n')
        rows = len(c)
        tth = np.array(c[0].strip().split(','), dtype=float)
        im = np.array(','.join(c[1:]).strip().split(','), dtype = float).reshape(rows-1,len(tth))
        return tth, im

    def setMultiImages(self,path):
        self.tth, self.im = self.readMatrix(path)
        for i in range(3):
            self.miw.setData(i,np.rot90(self.im,k=-1))
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = mainWindow()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()