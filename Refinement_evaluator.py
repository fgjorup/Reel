import os
import sys
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
    
    def __init__(self,n_images=1):
        pg.GraphicsLayoutWidget.__init__(self)
        
        # Create a ViewBox for each image
        self.views = [self.addViewBox() for i in range(n_images)]
        self.images = [pg.ImageItem(border='w') for i in range(n_images)]       
        for i,v in enumerate(self.views):
 
            v.setAspectLocked(False)
            v.addItem(self.images[i])
            v.linkView(v.XAxis,self.views[0])
            v.linkView(v.YAxis,self.views[0])           
            v.setLimits(xMin=0, xMax=600, 
             minXRange=10, 
             yMin=0, yMax=600,
             minYRange=10)
            
            ## Create random image
            data = np.random.normal(size=(1, 600, 600), loc=1024, scale=64).astype(np.uint16)
            self.images[i].setImage(data[0])
            ## Set initial view bounds
            #view[i].setRange(QtCore.QRectF(0, 0, 600, 600))


            
    def setData(self,index, im):
        self.images[index].setImage(im)
        
        

class mainWindow(QtWidgets.QMainWindow, uic.loadUiType(os.path.join(os.path.dirname(__file__), '_lib/_main.ui'))[0]):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setupUi(self)
        
        

        ## Create window with GraphicsView widget
        miw = MultiImageWidget(n_images=3)

        
        ###Canvas###
        self.pw0 = miw
        self.pw1 = pg.PlotWidget()
        self.pw2 = pg.PlotWidget()
        self.verticalLayout_surf.insertWidget(0, self.pw0)
        self.verticalLayout_pat.insertWidget(0, self.pw1)
        self.verticalLayout_par.insertWidget(0, self.pw2)


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = mainWindow()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()