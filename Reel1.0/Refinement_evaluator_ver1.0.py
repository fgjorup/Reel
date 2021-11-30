# -*- coding: utf-8 -*-
"""
Last update: 30/11/2021
Frederik H. Gjørup
"""

"""
To-do
- Open multiple datasets in one dialog session (next,cancel,done dialog buttons)
- Handle HDF5 files
- Implement 1/d, r, and ToF axis

"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '_lib'))
try:
    from PyQt5 import QtCore, QtWidgets, uic, QtGui
    from PyQt5.Qt import Qt
    import numpy as np

except ModuleNotFoundError as error:
    if error.name in ('PyQt5', 'pyqtgraph', 'numpy','matplotlib'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')
    else:
        print('\n'+error.msg+'\nPlease use PIP to install\n')
    raise
    
from _lib.ReelMisc import tth2Q, Q2tth, Q2d, tth2d, scaleArray, gridInterpolation, generateTicks
from _lib.ReelPlotWidgets import MultiImageWidget, PlotPatternWidget, PlotSliceWidget, PlotParametersWidget
from _lib.ReelRead import readCSV, readPRF, readPrfAlt, readXYY, readDAT, readXYE, readFIT, readPAR

from _lib.guipalettes import darkPalette
import ReelUserSettings as us

class mainWindow(QtWidgets.QMainWindow, uic.loadUiType(os.path.join(os.path.dirname(__file__), '_lib/_ReelMain.ui'))[0]):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setupUi(self)
        self.setAcceptDrops(True) # enable dragNdrop
        
        self.actionUpdate.triggered.connect(self.updateFiles)
        self.actionUpdate_2.triggered.connect(self.updateFiles) # toolbar
        
        self.actionAuto_range.triggered.connect(self.autoRangeAll)
        self.actionAuto_range_2.triggered.connect(self.autoRangeAll) # toolbar
        
        self.actionSet_wavelength.triggered.connect(self.setManualWavelength)
        self.actionSet_wavelength_2.triggered.connect(self.setManualWavelength)# toolbar
        
        self.actionToggle_Q.triggered.connect(self.toggleQ)
        
        self.actionOpen_files.triggered.connect(self.openFiles)
        self.actionOpen_files_2.triggered.connect(self.openFiles) # toolbar
        
        self.actionAdd_files.triggered.connect(self.addDataset)
        self.actionAdd_files_2.triggered.connect(self.addDataset) # toolbar
        
        self.actionRemove_dataset.triggered.connect(self.removeDataset)
        self.actionRemove_dataset_2.triggered.connect(self.removeDataset) # toolbar
        
        self.actionRemove_all_datasets.triggered.connect(self.removeAllDatasets)
        self.actionRemove_all_datasets_2.triggered.connect(self.removeAllDatasets) # toolbar
        
        self.actionNext.triggered.connect(self.nextDataset) # toolbar
        self.actionPrevious.triggered.connect(self.previousDataset) # toolbar
        
        self.actionAbout.triggered.connect(self.aboutBox)
        self.actionRestore_default.triggered.connect(self.restoreDefaultSettings)
        
        self.actionSubtract_background.triggered.connect(self.setSubtractBgr)
        self.actionSubtract_background_pat.triggered.connect(self.setSubtractBgrPattern)
        self.enableActions(False)
        
        self.initSubtractBgr()
        
        self.toolBarLabel = QtWidgets.QLabel('')
        self.toolBar.addWidget(self.toolBarLabel)
        
        ###Canvas###
        self.miw = MultiImageWidget(n_images=3,labels=('Observed','Calculated','Scale','Residual','Scale'))
        self.ppw = PlotPatternWidget()
        self.psw = PlotSliceWidget()
        self.parw = PlotParametersWidget()
        self.verticalLayout_surf.insertWidget(0, self.miw)
        self.verticalLayout_pat.insertWidget(0, self.ppw)
        self.verticalLayout_sli.insertWidget(0, self.psw)
        self.verticalLayout_par.insertWidget(0, self.parw)
        
        self.miw.sigHLineDragged.connect(self.updatePatternPlot)
        self.miw.sigVLineDragged.connect(self.updateSlicePlot)
        self.miw.sigDoubleClicked.connect(self.updateCrosshair)
        self.parw.sigVLineDragged.connect(self.updateHLine)
        for image in self.miw.images:
            image.hoverEvent = self.imageHoverEvent
        self.ppw.pobs.getViewBox().hoverEvent = self.patternHoverEvent
        self.psw.pobs.getViewBox().hoverEvent = self.sliceHoverEvent
        self.parw.pI.getViewBox().hoverEvent = self.parameterHoverEvent
        
        self.datasets = ['']
        self.dataset_index = 0
        self.im = [np.zeros((3,100,100))]
        self.tth = [np.arange(0,100,1)]
        self.files = [['']]
        self.par_file = [['']]
        self.lambd = [None]
        self.sub_plots = [{}]
        self.bgr = [[]]
        self.param = [{}]
        self.dev_from_mean = [False]  # use deviation from mean instead of calculated and residual
        
        self.plotLogo()
        self.scale_surf = us.default_surface_scale
        self.scale_pat = us.default_pattern_scale
        self.initScale()
        
        if '-debug' in sys.argv:
            self.openTestfiles()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # make list of paths for all dropped files
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        # find the file extension for the first valid file
        supported = ['.xyy','.prf','.dat','.xye','.xy','.csv']
        for f in files:
            ext = '.'+f.split('.')[-1]
            if ext in supported:
                break
        
        # check that the extension is among the supported formats
        if not ext in supported:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open selected file(s)!') 
            return
        
        # remove all files with different extensions and sort list alphabetically
        files = [f for f in files if f.endswith(ext)]
        files.sort()
        
        if self.actionAdd_files.isEnabled():
            self.addDataset(files=files,ext='*'+ext)
        else:
            self.openFiles(files=files,ext='*'+ext)

    def openTestfiles(self):
        path = os.path.abspath('_test_files')
        test_sets = os.listdir(path)
        for tset in test_sets:
            ts_path = os.path.join(path,tset)
            files = [os.path.join(ts_path,f) for f in os.listdir(ts_path) if f.endswith(tset)]
            ext = '*.'+files[0].split('.')[-1]
            self.addDataset(self,files=files,ext=ext)
        
    def keyPressEvent(self,event):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Left:
                self.previousDataset()
            elif event.key() == Qt.Key_Right:
                self.nextDataset()
            elif event.key() == Qt.Key_Up:
                if isinstance(self.datasets[-1],QtWidgets.QAction):
                    self.datasets[-1].trigger()
            elif event.key() == Qt.Key_Down:
                if isinstance(self.datasets[0],QtWidgets.QAction):
                    self.datasets[0].trigger()
        else:
            if event.key() == Qt.Key_Left:
                self.moveSliceCursor(increment=-1)
            elif event.key() == Qt.Key_Right:
                self.moveSliceCursor(increment=1)
            elif event.key() == Qt.Key_Up:
                self.moveReelCursor(increment=1)
            elif event.key() == Qt.Key_Down:
                self.moveReelCursor(increment=-1)
            elif event.key() == Qt.Key_A:
                self.autoRangeAll()
    
    def mouseDoubleClickEvent(self,event):
        if event.button() == 4: # middle mouse button
            self.autoRangeAll()
            
    def autoRangeAll(self):
        self.miw.autoRange()
        self.parw.autoRange()
        self.ppw.autoRange()
        self.psw.autoRange()
        
    def nextDataset(self):
        if self.actionNext.isEnabled():
            index = self.dataset_index
            index +=1
            index %=len(self.im) # wrap index
            self.datasets[index].trigger()
        
    def previousDataset(self):
        if self.actionPrevious.isEnabled():
            index = self.dataset_index
            index -=1
            index %=len(self.im) # wrap index
            self.datasets[index].trigger()
    
    def moveReelCursor(self,increment=0):
        index = self.dataset_index
        im = self.im[index]
        h_pos = self.miw.getHorizontalLineVal()
        h_pos = np.floor(h_pos)+increment
        h_pos = np.clip(h_pos,0,im.shape[2]-1)
        [self.miw.hlines[i].setValue(h_pos) for i in range(3)]
        #self.parw.updateVline(h_pos)
        self.updatePatternPlot(0)
    
    def moveSliceCursor(self,increment=0):
        index = self.dataset_index
        im = self.im[index]
        v_pos = self.miw.getVerticalLineVal()
        v_pos = np.floor(v_pos)+increment
        v_pos = np.clip(v_pos,0,im.shape[1]-1)
        [self.miw.vlines[i].setValue(v_pos+0.5) for i in range(3)]
        self.updateSlicePlot(1)
    
    def updateCrosshair(self):
        """update pattern and slice plot from new reel cursor crosshair position"""
        index = self.tabWidget_pattern.currentIndex()
        self.updatePatternPlot(index)
        self.updateSlicePlot(index)
    
    def showCurrentWavelength(self):
        index = self.dataset_index
        lambd = self.lambd[index]
        if isinstance(lambd,float):
            s = 'Wavelength: {:.4f}'.format(lambd)
        else:
            s = 'Wavelength: N/A'
        self.actionSet_wavelength.setStatusTip(s)
        self.actionSet_wavelength_2.setStatusTip(s)
    
    def setSurfaceplotLabels(self,index):
        if self.dev_from_mean[index]:
            self.miw.setLabel(2,'Mean')
            self.miw.setLabel(4,'Deviation from mean')
            self.ppw.setCalLabel('Mean')
            self.ppw.setResLabel('Deviation from mean')
        else:
            self.miw.setLabel(2,'Calculated')
            self.miw.setLabel(4,'Residual')
            self.ppw.setCalLabel('Calculated')
            self.ppw.setResLabel('Residual')
    
    def changeDataset(self,index):
        tth = self.tth[index]
        im = self.im[index]
        h_pos = round(self.miw.getHorizontalLineVal(),2)
        v_pos = round(self.miw.getVerticalLineVal(),2)
        scale = self.miw.getScale()
        vrect = self.miw.getViewRect()
        lambd = self.lambd[index]
        if self.actionToggle_Q.isChecked() and isinstance(lambd,type(None)):
            self.setManualWavelength()
        self.setSurfaceplotLabels(index)
        self.setMultiImages(tth,im)
        self.setSubplotActions()
        self.updateSubplots()
        self.setParameterActions()
        self.initParameterPlot()
        [self.miw.vlines[i].setValue(v_pos) for i in range(3)]
        [self.miw.hlines[i].setValue(h_pos) for i in range(3)]
        self.miw.setScale(scale)
        self.miw.setViewRange(vrect)
        self.parw.updateVline(h_pos+0.5)
        self.showCurrentWavelength()
        
    
    def addDataset(self,is_par=False,files=None,ext=None):
        self.im.append(np.zeros((3,100,100)))
        self.tth.append(np.arange(0,100,1))
        self.files.append([''])
        self.par_file.append([''])
        self.lambd.append(None)
        self.dev_from_mean.append(False)
        self.sub_plots.append({})
        self.bgr.append([])
        self.param.append({})
        self.datasets.append('')
        self.dataset_index = len(self.im)-1
        
        if is_par != True:
            self.openFiles(files,ext)
    
    def removeDataset(self):
        if len(self.im)==1:
            self.removeAllDatasets()
            return
        index = self.dataset_index # get target index
        self.im.pop(index)
        self.tth.pop(index)
        self.files.pop(index)
        self.par_file.pop(index)
        self.lambd.pop(index)
        self.dev_from_mean.pop(index)
        self.sub_plots.pop(index)
        self.bgr.pop(index)
        self.param.pop(index)
        ac = self.datasets.pop(index)
        self.removeToolbarAction(ac)
        self.previousDataset()
        
    def removeAllDatasets(self):
        path = self.path
        self.dataset_index = 0
        self.im = [np.zeros((3,100,100))]
        self.tth = [np.arange(0,100,1)]
        self.files = [['']]
        self.par_file = [['']]
        self.lambd = [None]
        self.dev_from_mean = [False]
        self.sub_plots=[{}]
        self.bgr= [[]]
        self.param = [{}]
        self.plotLogo()
        [self.removeToolbarAction(ac) for ac in self.datasets]
        self.datasets=['']
        self.enableActions(False)
        self.path = path
        
    def plotLogo(self):
        self.scale_surf, self.scale_pat = ['linear']*2
        fname = os.path.abspath('_lib/icons/Main.raw')
        self.openFiles(files=[fname],ext='*.raw')
        self.setWindowTitle('Reel')
        self.path = us.work_directory
        
    def addToolbarAction(self,label,index):
        # remove any action already at the index
        ac = self.datasets[index]
        self.removeToolbarAction(ac)
        [ac.setChecked(False) for ac in self.datasets if isinstance(ac,QtWidgets.QAction)]
        # add new action
        action = self.toolBar.addAction(label)
        action.setCheckable(True)
        action.setChecked(True)
        action.triggered.connect(self.toolbarActionTriggered)
        self.datasets[index] = action


    def removeToolbarAction(self,ac):
        if isinstance(ac,QtWidgets.QAction):
            self.toolBar.removeAction(ac)
    
    def toolbarActionTriggered(self):
        index = None
        for i, ac in enumerate(self.datasets):
            if ac.isChecked() and i != self.dataset_index:
                index = i
            else:
                ac.setChecked(False)
        if isinstance(index,type(None)):
            index = self.dataset_index
            self.datasets[index].setChecked(True)
        else:
            self.dataset_index = index
            self.changeDataset(index)
    
    def restoreDefaultSettings(self):
        yes = QtWidgets.QMessageBox.Yes
        cancel = QtWidgets.QMessageBox.Cancel
        reply = QtWidgets.QMessageBox.warning(self,  # parent
                                              'Warning',  # titel
                                              'Are you sure you wish to restore to default settings?',  # label
                                              yes,  # button0
                                              cancel)  # button1
        if reply == yes:
            path = os.path.join(os.getcwd(),'_lib')
            src = os.path.join(path,'_ReelDefaultSettings.py')
            dst = os.path.join(os.getcwd(),'ReelUserSettings.py')
            with open(src,'r') as f:
                s = f.readlines()
            s[2] = 'User defined settings for Reel\n'
            s = ''.join(s)
            with open(dst,'w') as f:
                f.write(s)
                QtWidgets.QMessageBox.information(self,'Attention','Please restart the program to implement changes')
    
    def imageHoverEvent(self,event):
        if event.isExit():
            self.statusbar.clearMessage()
            return
        index = self.dataset_index
        im = self.im[index]
        datapoints  = im.shape[1]
        frames = im.shape[2]
        pos = event.pos()
        i, j = pos.x(), pos.y()
        i = int(np.clip(i, 0, datapoints - 1))
        j = int(np.clip(j, 0, frames - 1))
        tth = self.tth[index][i]
        obs, calc, res = [val[i, frames-(j+1)] for val in im]
        lambd = self.lambd[index]
        if isinstance(lambd,float):
            Q = tth2Q(tth,lambd)
            d = tth2d(tth,lambd)
            if self.dev_from_mean[index]:
                self.statusbar.showMessage('Pattern: {:4d}  |  2θ: {:6.2f} °  |  Q: {:6.3f} Å⁻¹ |  d: {:6.3f} Å  |  Observed: {:8.1f}  |  Mean: {:8.1f}  |  Deviation from mean: {:8.1f} % |'.format(j+1,tth,Q,d,obs,calc,res))
            else:
                self.statusbar.showMessage('Pattern: {:4d}  |  2θ: {:6.2f} °  |  Q: {:6.3f} Å⁻¹ |  d: {:6.3f} Å  |  Observed: {:8.1f}  |  Calculated: {:8.1f}  |  Residual: {:8.1f}  |'.format(j+1,tth,Q,d,obs,calc,res))
        else:
            if self.dev_from_mean[index]:
                self.statusbar.showMessage('Pattern: {:4d}  |  2θ: {:6.2f} °  |  Observed: {:8.1f}  |  Mean: {:8.1f}  |  Deviation from mean: {:8.1f} % |'.format(j+1,tth,obs,calc,res))
            else:
                self.statusbar.showMessage('Pattern: {:4d}  |  2θ: {:6.2f} °  |  Observed: {:8.1f}  |  Calculated: {:8.1f}  |  Residual: {:8.1f}  |'.format(j+1,tth,obs,calc,res))
    
        #     self.statusbar.showMessage('Slice: {:4d}  |  2θ: {:6.2f} °  |  Q: {:6.3f} Å⁻¹ |  d: {:6.3f} Å  |  Observed: {:8.1f}  |  Calculated: {:8.1f}  |  Residual: {:8.1f}  |'.format(frames-j,tth,Q,d,obs,calc,res))
        # else:
        #     self.statusbar.showMessage('Slice: {:4d}  |  2θ: {:6.2f} °  |  Observed: {:8.1f}  |  Calculated: {:8.1f}  |  Residual: {:8.1f}  |'.format(frames-j,tth,obs,calc,res))
    
    def patternHoverEvent(self,event):
        index = self.dataset_index
        if event.isExit():
            self.statusbar.clearMessage()
            return
        pos = event.pos()
        vpos = self.ppw.pobs.getViewBox().mapToView(pos)
        x, I = vpos.x(), vpos.y()
        lambd = self.lambd[index]
        if self.actionToggle_Q.isChecked() and isinstance(lambd,float):
            Q = x
            tth = Q2tth(x,lambd)
            d = Q2d(x,lambd)
        else:
            tth = x
            if isinstance(lambd,float):
                Q = tth2Q(tth,lambd)
                d = tth2d(tth,lambd)
        if isinstance(lambd,float):
            self.statusbar.showMessage('2θ: {:6.2f} °  |  Q: {:6.3f} Å⁻¹ |  d: {:6.3f} Å  |  Intensity: {:8.1f}  |'.format(tth,Q,d,I))
        else:    
            self.statusbar.showMessage('2θ: {:6.2f}  |  Intensity: {:8.1f}  |'.format(tth,I))

    def sliceHoverEvent(self,event):
        if event.isExit():
            self.statusbar.clearMessage()
            return
        pos = event.pos()
        vpos = self.psw.pobs.getViewBox().mapToView(pos)
        x, I = vpos.x(), vpos.y()   
        self.statusbar.showMessage('Slice: {:4.0f}  |  Intensity: {:8.1f}  |'.format(x,I))

    def parameterHoverEvent(self,event):
        if event.isExit():
            self.statusbar.clearMessage()
            return
        pos = event.pos()
        vpos = self.parw.pI.getViewBox().mapToView(pos)
        x, y0 = vpos.x(), vpos.y()
        y1 = self.parw.v2.mapToView(pos).y()
        self.statusbar.showMessage('Pattern: {:4.0f}  |  Primary: {:6.1f}  |  Secondary: {:6.2f}  |'.format(x,y0,y1))
 
    def updateFiles(self):
        index = self.dataset_index
        files = self.files[index]
        if files[0].endswith('.prf'):
            ext='*.prf'
        elif files[0].endswith('.xyy'):
            ext='*.xyy'
        elif files[0].endswith('.dat'):
            ext='*.dat'
        elif files[0].endswith('.xye') or files[0].endswith('.xy'):
            ext='*.xye *.xy'
        elif files[0].endswith('.par'):
            files = self.par_file[index]
            ext='*.par'
        elif files[0].endswith('.csv'):
            self.openFiles(files=None,ext='*.csv')
            return
        self.openFiles(files=files,ext=ext)
    
    def aboutBox(self):
        about = ['<html>',
                        '<p align="center">',
                            '<span style=" font-size:10pt; font-weight:600;">',
                                'Reel1.0<br/>',
                            '</span>',
                            'by<br/>',
                            'Frederik H Gjørup<br/>',
                            'Department of Chemistry<br/>',
                            'Aarhus University<br/>',
                            'November 2021',
                        '</p>',
                '</html>']
        QtWidgets.QMessageBox.about(self,'About',''.join(about))
    
    def setManualWavelength(self):
        index = self.dataset_index
        l = self.lambd
        for i in range(len(l)):
            lambd = l[(index+i)%len(l)]
            if isinstance(lambd,float):
                break
            else:
                lambd = us.default_wavelength
        value, ok = QtWidgets.QInputDialog.getDouble(self,                         # parent
                                                     'Wavelength',                 # titel
                                                     'Set manual wavelength (Å):', # label
                                                     lambd,                        # value
                                                     0.1,                          # minValue
                                                     10,                           # maxValue
                                                     4)                            # decimals
        if ok:
            self.lambd[index] = value
            self.showCurrentWavelength()
        return ok
    
    def toggleQ(self):
        index = self.dataset_index
        x = self.tth[index]
        lambd = self.lambd[index]
        if self.actionToggle_Q.isChecked():
            self.miw.setXLabel('Q (Å<sup>-1</sup>)')
            if isinstance(lambd,float):
                x = tth2Q(x,lambd)
            else:
                if self.setManualWavelength():
                    lambd = self.lambd[index]
                    x = tth2Q(x,lambd)
                else:
                    self.actionToggle_Q.setChecked(False)
                    self.miw.setXLabel('2θ (°)')
        else:
            self.miw.setXLabel('2θ (°)')
        ticks = generateTicks(x)
        for i in range(3):
            self.miw.setTicks(i,ticks)    
        self.updatePatternPlot(index)
        self.autoRangeAll()
        
        
    def updatePatternPlot(self,index=0):
        if not isinstance(index,int):
            index=0
        self.tabWidget_pattern.setCurrentIndex(index)
        h_val = self.miw.getHorizontalLineVal()
        index = self.dataset_index
        im = self.im[index]
        files = self.files[index]
        pos = np.round(h_val)-1
        pos = int(np.clip(pos,0,im.shape[2]-1))
        temp = ''
        if not files[0] == '':
            param = self.param[index]
            for key in param:
                if key=='Temperature (°C)':
                    temp = ' - Temperature: {:.0f} °C'.format(param[key][(pos)])
                elif key=='Temperature (K)':
                    temp = ' - Temperature: {:.0f} K'.format(param[key][(pos)])
            fname = os.path.splitext(os.path.basename(files[(pos)]))[0]
            title = '{}{}'.format(fname,temp)
            self.ppw.setTitle(title)
        scale = self.scale_pat
        obs, calc, res = [im[i,:,-(pos+1)] for i in range(3)]
        if self.subtract_bgr_pat:
            bgr = self.bgr[index][:,-(pos+1)]
            obs, calc, = obs-bgr, calc-bgr
        x = self.tth[index]
        lambd = self.lambd[index]
        if self.actionToggle_Q.isChecked() and isinstance(lambd,float):
            x = tth2Q(x, lambd)
            self.ppw.setLabel('bottom','Q (Å<sup>-1</sup>)')
        else:
            self.ppw.setLabel('bottom','2θ (°)')
        self.ppw.setObsData(x,scaleArray(obs,scale))
        self.ppw.setCalData(x,scaleArray(calc,scale))
        self.ppw.setResData(x,scaleArray(res,scale,retain_sign=True))
        sub_plots = self.sub_plots[index]
        active = self.getSubplotActions()
        for key in active:
            y = sub_plots[key][(pos),:]
            if self.subtract_bgr_pat:
                y = y-bgr
            self.ppw.setSubplotData(key,x,scaleArray(y,scale))
        
        self.parw.updateVline(h_val)
    
    def updateSlicePlot(self,index=1):
        if not isinstance(index,int):
            index=1
        self.tabWidget_pattern.setCurrentIndex(index)
        v_val = self.miw.getVerticalLineVal()
        index = self.dataset_index
        im = self.im[index]
        pos = int(np.clip(np.floor(v_val),0,im.shape[1]-1))
        tth = self.tth[index]
        tth = tth[pos]
        lambd = self.lambd[index]
        if isinstance(lambd,float):
            Q = tth2Q(tth,lambd)
            d = tth2d(tth,lambd)
            titel = '|  2θ: {:6.2f} °  |  Q: {:6.3f} Å⁻¹ |  d: {:6.3f} Å  |'.format(tth,Q,d)
        else:
            titel = '|  2θ: {:6.2f} °  |'.format(tth)
        self.psw.setTitle(titel)
        # Slice integration interval
        intvl = us.default_slice_integration_interval
        coord = np.clip([pos+intvl[0],pos+intvl[1]+1],0,im.shape[1])
        scale = self.scale_pat
        
        x = np.arange(0,im.shape[2],1,dtype='float32')
        ocr = [np.flip(im[i,coord[0]:coord[1],:],axis=1) for i in range(3)] # obs, calc, res
        excl = [np.all(np.isnan(y),axis=0) for y in ocr]
        obs, calc, res = [np.nanmean(y[:,~excl[i]],axis=0) for i,y in enumerate(ocr)]
        if self.subtract_bgr_pat:
            bgr = np.flip(self.bgr[index][coord[0]:coord[1],:],axis=1)
            obs, calc = [y-np.nanmean(bgr[:,~excl[i]],axis=0) for i,y in enumerate((obs, calc))] 
 
        self.psw.setObsData(x[~excl[0]],scaleArray(obs,scale))
        self.psw.setCalData(x[~excl[1]],scaleArray(calc,scale))
        self.psw.setResData(x[~excl[2]],scaleArray(res,scale,retain_sign=True))
        
        sub_plots = self.sub_plots[index]
        active = self.getSubplotActions()
        for key in active:
            y = np.nanmean(sub_plots[key][:,coord[0]:coord[1]][~excl[1],:],axis=1)
            if self.subtract_bgr_pat:
                y = y-np.nanmean(bgr[:,~excl[1]],axis=0)
            self.psw.setSubplotData(key,x[~excl[1]],scaleArray(y,scale))
            
            
    def initParameterPlot(self):
        self.parw.removePrimaryPlots()
        self.parw.removeSecondaryPlots()
        primary = self.getPrimaryParam()
        secondary = self.getSecondaryParam()
        for key in primary:
            self.parw.addPrimaryPlot(key)
        for key in secondary:
            self.parw.addSecondaryPlot(key)
        self.updateParameterPlot()

        
    def updateParameterPlot(self):
        index = self.dataset_index
        im = self.im[index]
        x = np.arange(1,im.shape[2]+1,1,dtype='float32')
        self.parw.clearPlot()
        primary = self.getPrimaryParam()
        secondary = self.getSecondaryParam()
        param = self.param[index]
        for key in param:
            if key in primary:
                self.parw.setPrimaryData(key,x,param[key])
            elif key in secondary:
                self.parw.setSecondaryData(key,x,param[key]) 
        
    def setParameterActions(self):
        index = self.dataset_index
        old_primary = self.getPrimaryParam()
        old_secondary = self.getSecondaryParam()
        params = self.param[index]
        if len(old_primary)<2 and len(params)>1:
            old_primary = us.default_primary_parameter_plot
        if len(old_secondary)<2 and len(params)>1:
            old_secondary = us.default_secondary_parameter_plot
        self.menuPrimary_axis.clear()
        self.menuSecondary_axis.clear()
        #param_actions = [QtWidgets.QAction(param) for param in self.param]
        menu = self.menuPrimary_axis
        param_actions = [menu.addAction(param) for param in params]
        for action in param_actions:
            action.setCheckable(True)
            action.triggered.connect(self.initParameterPlot)
            if action.text() in old_primary:
                action.setChecked(True)
        if len(param_actions)==1:
            param_actions[0].setChecked(True)
        elif len(param_actions)<1:
            ac = menu.addAction('none')
            ac.setCheckable(False)
            ac.setEnabled(False)
            
        menu = self.menuSecondary_axis
        param_actions = [menu.addAction(param) for param in self.param[index]]
        for action in param_actions:
            action.setCheckable(True)
            action.triggered.connect(self.initParameterPlot)
            if action.text() in old_secondary:
                action.setChecked(True)
        if len(param_actions)<1:
            ac = menu.addAction('none')
            ac.setCheckable(False)
            ac.setEnabled(False)
            
    def getPrimaryParam(self):
        return [a.text() for a in self.menuPrimary_axis.actions() if a.isChecked()]
    
    def getSecondaryParam(self):
        return [a.text() for a in self.menuSecondary_axis.actions() if a.isChecked()]
    
    def getSubplotActions(self):
        return [a.text() for a in self.menuSub_plots.actions() if a.isChecked()]
    
    def setSubplotActions(self):
        index = self.dataset_index
        old = self.getSubplotActions()
        menu = self.menuSub_plots
        if len(old)<1:
            old = us.default_sub_plots
        menu.clear()
        subplot_actions = [menu.addAction(sub) for sub in self.sub_plots[index]]
        for action in subplot_actions:
            action.setCheckable(True)
            action.triggered.connect(self.updateSubplots)
            if len(old)<1:
                action.setChecked(True)
            elif action.text() in old:
                action.setChecked(True)
        if len(subplot_actions)<1:
            ac = menu.addAction('none')
            ac.setCheckable(False)
            ac.setEnabled(False)
        
    def updateSubplots(self):
        self.removeSubplots()
        active = self.getSubplotActions()
        for key in active:
            self.ppw.addSubplot(key=key)
            self.psw.addSubplot(key=key)
        index = self.tabWidget_pattern.currentIndex()
        self.updatePatternPlot(index)
        self.updateSlicePlot(index)
            
    def setMultiImages(self,tth,im):
        index = self.dataset_index
        im = im.astype(dtype='float32')
        im = np.rot90(im,k=1,axes=(1,2))
        # generate ticks for images
        lambd = self.lambd[index]
        if self.actionToggle_Q.isChecked() and isinstance(lambd,float):
            x = tth2Q(tth,lambd)
            self.miw.setXLabel('Q (Å<sup>-1</sup>)')
        else:
            x = tth
            self.actionToggle_Q.setChecked(False)
            self.miw.setXLabel('2θ (°)')
        ticks = generateTicks(x)
        scale = self.scale_surf
        bgr = self.bgr[index]
        for i in range(2):
            if self.subtract_bgr:
                im[i] -= np.rot90(bgr,k=1)
                #im[i] -= bgr
            self.miw.setData(i,scaleArray(im[i],scale))
            self.miw.setTicks(i,ticks)
        self.miw.setData(2,scaleArray(im[2],scale,retain_sign=True))
        self.miw.setTicks(2,ticks)
        self.miw.autoRangeHistograms()
    
    def initScale(self):
        for ac in self.menuScaling_surf.actions():
            ac.setChecked(ac.toolTip()==self.scale_surf)
            ac.triggered.connect(self.setScaleSurf)
        for ac in self.menuScaling_pat.actions():
            ac.setChecked(ac.toolTip()==self.scale_pat)
            ac.triggered.connect(self.setScalePattern)
            
    def setScaleSurf(self):
        current_scale = us.default_surface_scale
        for scale in self.menuScaling_surf.actions():
            if scale.isChecked() and scale.toolTip() != self.scale_surf: # 'linear', 'log10', 'logn', 'sqrt'
                current_scale = scale.toolTip()
            else:
                scale.setChecked(False)
        self.scale_surf = current_scale
        index = self.dataset_index
        im = self.im[index]
        tth = self.tth[index]
        self.setMultiImages(tth,im)
        
    def setScalePattern(self):
        current_scale = us.default_pattern_scale
        label = 'Intensity (a.u.)'
        for scale in self.menuScaling_pat.actions():
            if scale.isChecked() and scale.toolTip() != self.scale_pat: # 'linear', 'log10', 'logn', 'sqrt'
                current_scale = scale.toolTip()
                if current_scale != 'linear':
                    label += ' - {}'.format(scale.text())
            else:
                scale.setChecked(False)
        self.scale_pat = current_scale
        self.ppw.setLabel('left',label)
        self.psw.setLabel('left',label)
        index = self.tabWidget_pattern.currentIndex()
        self.updatePatternPlot(index)
        self.updateSlicePlot(index)
        self.ppw.autoRange()
        self.psw.autoRange()
    
    def initSubtractBgr(self):
        # surface
        subtract_bgr = us.default_surface_background_subtraction
        self.actionSubtract_background.setChecked(subtract_bgr)
        self.subtract_bgr = subtract_bgr
        # pattern
        subtract_bgr = us.default_pattern_background_subtraction
        self.actionSubtract_background_pat.setChecked(subtract_bgr)
        self.subtract_bgr_pat = subtract_bgr
        
    def setSubtractBgr(self):
        index = self.dataset_index
        im = self.im[index]
        tth = self.tth[index]
        self.subtract_bgr = self.actionSubtract_background.isChecked()
        self.setMultiImages(tth,im)
    
    def setSubtractBgrPattern(self):
        self.subtract_bgr_pat = self.actionSubtract_background_pat.isChecked()
        index = self.tabWidget_pattern.currentIndex()
        self.updatePatternPlot(index)
        self.updateSlicePlot(index)
    
    def updateHLine(self):
        val = self.parw.vline.value()
        self.miw.hlines[0].setValue(val)
        self.miw._update_hline()
        
    def removeSubplots(self):
        self.ppw.removeSubplots()
        self.psw.removeSubplots()
    
    def enableActions(self,enable):
        self.actionUpdate.setEnabled(enable)
        self.actionUpdate_2.setEnabled(enable)
        self.actionAdd_files.setEnabled(enable)
        self.actionAdd_files_2.setEnabled(enable)
        self.actionRemove_dataset.setEnabled(enable)
        self.actionRemove_dataset_2.setEnabled(enable)
        self.actionRemove_all_datasets.setEnabled(enable)
        self.actionRemove_all_datasets_2.setEnabled(enable)
        self.actionPrevious.setEnabled(enable)
        self.actionNext.setEnabled(enable)
    
####################################################################################################
##                                   Read data methods                                            ##
####################################################################################################

    def openFiles(self,files=None,ext=None):
        if not isinstance(files,list):
            path = self.path
            if not path:
                path = os.getenv('USERPROFILE','')
            if ext != '*.csv':
                ext = us.default_file_extension
            filters = '*.xyy;;*.prf;;*.dat;;*.xye *.xy;;*.csv'    
            filters = ext+';;'+';;'.join([x for x in filters.replace(ext,'').split(';;') if x])
            files, ext =  QtWidgets.QFileDialog.getOpenFileNames(self, 'Select files', path , filters)
        if len(files)<1:
            return
        index = self.dataset_index
        path = os.path.dirname(files[0])
        self.path = path
        try:
            if ext=='*.raw':
                im, tth, files, lambd, param, sub_plots, bgr, par_file, was_canceled = self.openRAW(files[0])
                label = 'Reel1.0'
            else:
                if ext=='*.xyy':
                    im, tth, files, lambd, param, sub_plots, bgr, par_file, was_canceled = self.openXYY(files)
                elif ext=='*.prf':
                    im, tth, files, lambd, param, sub_plots, bgr, par_file, was_canceled = self.openPRF(files)
                elif ext=='*.dat':
                    im, tth, files, lambd, param, sub_plots, bgr, par_file, was_canceled = self.openDAT(files)
                elif ext=='*.xye *.xy' or ext=='*.xye' or ext=='*.xy':
                    im, tth, files, lambd, param, sub_plots, bgr, par_file, was_canceled = self.openXYE(files)
                elif ext=='*.csv':
                    im, tth, files, lambd, param, sub_plots, bgr, par_file, was_canceled = self.openCSV(files[0])
                elif ext=='*.par':
                    # im, tth, files, lambd, param, sub_plots, bgr, par_file, was_canceled = self.openPAR(files[0], path)
                    datasets, par_file, was_canceled = self.openPAR(files[0], path)
                    if was_canceled:
                        return
                    if par_file == self.par_file[index]:
                        self.removeAllDatasets()
                    for i, dataset in enumerate(datasets):
                        im, tth, files, lambd, param, sub_plots, bgr = dataset
                        if i>0:
                            self.addDataset(is_par=True)
                        self.im[i] = im
                        self.tth[i] = tth
                        self.files[i] = files
                        self.lambd[i] = lambd
                        param['Mean intensity'] = np.flip(np.nanmean(im[0,:,:],axis=0))
                        self.param[i] = param
                        self.sub_plots[i] = sub_plots
                        self.bgr[i] = bgr
                        self.par_file[i] = par_file
                        
                        label = '{}'.format(files[0].split(' η')[0])
                        self.addToolbarAction(label,index+i)
                        
                    
                    tth = self.tth[index]
                    im = self.im[index]
                
                if was_canceled:
                    return
                label = '{}'.format(os.path.basename(path))
                self.setWindowTitle('{} - Reel'.format(path))
                self.enableActions(True)
            if not ext=='*.par':
                
                self.addToolbarAction(label,index)
                param['Mean intensity'] = np.flip(np.nanmean(im[0,:,:],axis=0))
                
                # deviation from mean
                if np.all(im[1]==0):
                    self.dev_from_mean[index] = True
                    im[0][im[0]<=0.0]=np.nan
                    mean = np.nanmean(im[0],axis=1)
                    mean = np.full(im[0].T.shape,mean,dtype='float32').T
                    im[1] = mean # mean
                    im[2] = (im[0]-mean)/mean*100 # (obs-mean)/mean*100%

                else:
                    self.dev_from_mean[index] = False
                self.setSurfaceplotLabels(index)
                self.im[index] = im.astype(dtype='float32')
                self.tth[index] = tth
                self.files[index] = files
                self.lambd[index] = lambd
                self.param[index] = param
                self.sub_plots[index] = sub_plots
                self.bgr[index] = bgr
                self.par_file[index] = par_file

            self.setMultiImages(tth,im)
            self.setSubplotActions()
            self.updateSubplots()
            self.setParameterActions()
            self.initParameterPlot()
            self.autoRangeAll()
            self.showCurrentWavelength()
            
        except:
            QtWidgets.QMessageBox.warning(self,'Warning','Unable to open selected files!')    
            self.setWindowTitle('Reel')
            self.toolBarLabel.setText('')
            raise
            
    def openXYY(self,files):
        progress = self.progressWindow("Reading files", "Cancel", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
        im = [[],[],[]]
        bgr, temp, lambd, filenames, comments = [], [], [], [], []
        _, sub_plots, param = {}, {}, {'R_p':[]}
            
        for i, file in enumerate(files):
            progress.setValue(i)
            header, data = readXYY(file)
            # "tth" and "Y_obs" are the only mandatory columns
            tth = data.pop('tth')
            yobs = data.pop('Y_obs')
            keys = list(data.keys())
            # get data with special meaning
            if 'Y_calc' in keys:
                ycal = data.pop('Y_calc')
            else:
                ycal = np.full(yobs.shape,0,dtype='float16')
            if 'Y_res' in keys:
                res = data.pop('Y_res')
            elif np.any(ycal>0):
                res = yobs-ycal
            else:
                res = np.full(yobs.shape,0,dtype='float16')
            if 'Background' in keys:
                bgr.append(data['Background'])
            else:
                bgr.append(np.full(yobs.shape,0,dtype='float16'))
                
            im[0].append(yobs)
            im[1].append(ycal)
            im[2].append(res)
                
            for key in data:
                try:
                    sub_plots[key].append(data[key])
                except KeyError:
                    sub_plots[key]=[data[key]]
            param['R_p'].append(np.sum(abs(res))/np.sum(yobs)*100)
            temp.append(header['Temperature (K)'])
            lambd.append(header.pop('Wavelength (Å)'))
            filenames.append(header.pop('Filename'))
            comments.append(header.pop('Comments'))
            for key in header:
                try:
                    param[key].append(header[key])
                except KeyError:
                    param[key]=[header[key]]
            if progress.wasCanceled():
                return [], [], [], [], {}, {}, [''], True
        
        im = np.array(im, dtype='float32')
        im = np.rot90(im,k=-1,axes=(1,2))
        bgr = np.array(bgr)
        bgr = np.rot90(bgr,k=-1)
        lambd = np.mean([float(l) for l in lambd])
        param = {key:np.array(param[key],dtype='float32') for key in param}
        sub_plots = {key:np.array(sub_plots[key]) for key in sub_plots}
        progress.setValue(len(files))
        return im, tth, files, lambd, param, sub_plots, bgr, [''], False

    def openPRF(self,files):
        progress = self.progressWindow("Reading files", "Cancel", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
        im =[[],[],[]]
        bgr = []
        temp=[]
        param = {'R_p':[]}
        sub_plots = {}
        for i, file in enumerate(files):
            progress.setValue(i)
            try:
                tth, yobs, ycal, res, bckg, T, excl_reg, lambd = readPRF(file)
                res = np.array([float(yobs[i])-float(ycal[i]) for i in range(len(yobs))])
                sub_plot = {}
            except ValueError:
                tth, yobs, ycal, res, bckg, excl_reg, sub_plot = readPrfAlt(file)
                T, lambd = None, [None]
            res[excl_reg]=0
            ycal[excl_reg]=np.nan
            im[0].append(yobs)
            im[1].append(ycal)
            im[2].append(res)
            bgr.append(bckg)
            temp.append(T)
            for key in sub_plot:
                try:
                    sub_plots[key].append(sub_plot[key])
                except KeyError:
                    sub_plots[key]=[sub_plot[key]]
            param['R_p'].append(np.sum(abs(res[excl_reg==False]))/np.sum(yobs[excl_reg==False])*100)
            if progress.wasCanceled():
                return [], [], [], [], {}, {}, [''], True
        im = np.array(im, dtype='float32')
        im = np.rot90(im,k=-1,axes=(1,2))
        bgr = np.array(bgr)
        bgr = np.rot90(bgr,k=-1)
        sub_plots = {key:np.array(sub_plots[key]) for key in sub_plots}
        if not None in temp:
            if min(temp)<273.15: # Guess the unit based on minimum value
                key = 'Temperature (°C)'
            else:
                key = 'Temperature (K)'
            param[key] = temp    
        param = {key:np.array(param[key],dtype='float32') for key in param}
        progress.setValue(len(files))
        return im, tth, files, lambd[0], param, sub_plots, bgr, [''], False
            
    def openPAR(self, file, path):
        """Open MAUD .par file"""
        #try:
        datasets=[]
        # im = [[],[],[]]
        # sub_plots={}
        #####  Open the primary .par file  #####
        progress = self.progressWindow("Reading files", "Cancel", 0, 1,'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
        progress.setLabelText('{}\nReading'.format(file))
        
        r, obs, dist, lambd, x_corr , y_corr, dataset_id, datafile_id, eta = readPAR(file)
        num = len(dataset_id)*2
        progress.setMaximum(num)
        
        # Determine number of bins for each datasets
        bins = [len(x) for x in obs]
        # Determine length of longest datafile across all n datasets
        length = max([max(map(len,n)) for n in r])
        empty = np.full((2,length),np.nan,dtype='float16') # empty row(s) to separate each dataset
        empty[:,0] = 0.0 # Add a single non-nan value to suppress All-NaN slice RuntimeWarning

        for n, name in enumerate(dataset_id):
            im = [[],[],[]]
            sub_plots={}
            progress.setValue(n*2)
            #progress.setLabelText('Reading dataset {}:{}'.format(n+1,len(dataset_id)))
            progress.setLabelText('{} {}:{}\nReading .fit files'.format(name,n+1,len(dataset_id)))
            # Open subsequent .fit files for each dataset
            files = datafile_id[n*bins[n]:(n+1)*bins[n]]

            r_cal, cal, bckg, data = self.openFITs(path, files)  #, dist[n], x_corr[n], y_corr[n])

            progress.setValue(n*2+1)
            progress.setLabelText('{} {}:{}\nMapping to grid coordinates'.format(name,n+1,len(dataset_id)))
            xi, yi, zi_obs, mask = gridInterpolation(r[n],obs[n],eta[n],x_corr[n],y_corr[n],dist[n],length,xi=None,yi=None,mask=None)
            xi_calc, yi_calc, zi_calc, mask_calc = gridInterpolation(r_cal,cal,eta[n],x_corr[n],y_corr[n],dist[n],length,xi=xi,yi=yi,mask=None)
            _, _, zi_bgr, _ = gridInterpolation(r_cal,bckg,eta[n],x_corr[n],y_corr[n],dist[n],length,xi=xi,yi=yi,mask=mask_calc)
            zi_res = zi_obs-zi_calc 
            for key in data:
                I = data[key]
                xi_sub, yi_sub, zi_sub, mask_sub = gridInterpolation(r_cal,I,eta[n],x_corr[n],y_corr[n],dist[n],length,xi=xi,yi=yi,mask=mask_calc)
                sub_plots[key] = zi_sub
            if progress.wasCanceled():
                return [], [], [], [], {}, {}, [''], True
            yobs, ycal, res, bgr = zi_obs, zi_calc, zi_res, zi_bgr
            rp = np.divide(np.nansum(np.abs(res),axis=1),np.nansum(yobs,axis=1))*100
            files = ['{} η: {:5.1f} °.par'.format(name, e) for e in eta[n]]
  
            im[0] = yobs
            im[1] = ycal
            im[2] = res  
    
            im = np.array(im, dtype='float32')
            im = np.rot90(im,k=-1,axes=(1,2))
            bgr = np.array(bgr)
            bgr = np.rot90(bgr,k=-1)
            param = {'R_p':np.array(rp,dtype='float32')}
            datasets.append((im, xi, files, np.mean(lambd), param, sub_plots, bgr))
        progress.setValue(num)
        return datasets, [file], False   
        
    def openFITs(self,path, datafile_id):  #, dist, x_corr, y_corr):
        """Open multiple .fit files from a list of filenames - called by openPAR"""
        sub_plots = {}
        r = []
        I   = []
        bgr = []
        for f, enabled in datafile_id:
            try:
                if enabled:
                    fname = '{}/{}{}.fit'.format(path,*f.split('.esg'))
                    data = readFIT(fname)  #, dist, x_corr, y_corr)
                    r.append(data.pop('r'))
                    I.append(data.pop('I'))
                    bgr.append(data.pop('background'))
                    for key in data:
                        y = data[key]
                        try:
                            sub_plots[key].append(y)
                        except KeyError:
                            sub_plots[key]=[y]
                else:
                    raise FileNotFoundError
            except FileNotFoundError:
                r.append(np.array([0.0]))
                I.append(np.array([np.nan]))
                bgr.append(np.array([np.nan]))
                for key in sub_plots.keys():
                    try:
                        sub_plots[key].append(np.array([np.nan]))
                    except KeyError:
                        sub_plots[key] = [np.array(np.nan)]

        for key in sub_plots.keys():
            sub_plots[key] = np.array(sub_plots[key],dtype=object)
        return r, I, bgr, sub_plots
    
    def openDAT(self,files):
        progress = self.progressWindow("Reading files", "Cancel", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
        im =[[],[],[]]
        temp=[]
        for i, file in enumerate(files):
            progress.setValue(i)
            x,yobs,T,lambd, _, _ = readDAT(file)
            if i<1:
                tth = x
                length = yobs.shape[0]
            if yobs.shape[0]>length:
                rest = length-yobs.shape[0]
                yobs = np.append(yobs,[np.nan]*rest)
            im[0].append(yobs[:length])
            im[1].append(np.full(length,0,dtype='float16'))
            im[2].append(np.full(length,0,dtype='float16'))
            temp.append(T)
            if progress.wasCanceled():
                return [], [], [], [], {}, {}, [''], True
        im = np.array(im, dtype='float32')
        im = np.rot90(im,k=-1,axes=(1,2))
        bgr = np.full(im[0].shape,0,dtype='float32')
        if not None in temp:
            if min(temp)<273.15: # Guess the unit based on minimum value
                key = 'Temperature (°C)'
            else:
                key = 'Temperature (K)'
            param = {key:np.array(temp,dtype='float32')}
        else:
            param = {}
        progress.setValue(len(files))
        return im, tth, files, lambd, param, {}, bgr, [''], False
 
    def openXYE(self,files):
        progress = self.progressWindow("Reading files", "Cancel", 0, len(files),'Refinement Evaluator',QtGui.QIcon(":icons/Main.png"))
        im =[[],[],[]]
        for i, file in enumerate(files):
            progress.setValue(i)
            x,yobs,_ = readXYE(file)
            if i<1:
                tth = x
                length = yobs.shape[0]
            if yobs.shape[0]<length:
                rest = length-yobs.shape[0]
                yobs = np.append(yobs,[np.nan]*rest)
            im[0].append(yobs[:length])
            im[1].append(np.full(length,0,dtype='float16'))
            im[2].append(np.full(length,0,dtype='float16'))
            if progress.wasCanceled():
                return [], [], [], [], {}, {}, [''], True
        im = np.array(im, dtype='float32')
        im = np.rot90(im,k=-1,axes=(1,2))
        bgr = np.full(im[0].shape,0,dtype='float16')
        progress.setValue(len(files))
        return im, tth, files, None, {}, {}, bgr, [''], False

    def openCSV(self,file):
        file = file.replace('_meta.csv','.csv')
        tth, im_obs = readCSV(file)
        im = np.full((3,im_obs.shape[0],im_obs.shape[1]),0, dtype='float32')
        im[0,:,:] = im_obs.astype('float32')
        #im = np.fliplr(im)
        bgr = np.full(im[0].shape,0,dtype='float16')
        fname = os.path.split(file)[-1][:-4]
        files = ['{}: {}.csv'.format(fname,i+1) for i in range(im.shape[2])]
        return im, tth, files, None, {}, {}, bgr, [''], False
    
    def openRAW(self,file):
        img = np.fromfile(file, dtype='ubyte').reshape(230,230).astype(float)
        img = img/img.max()
        img = np.abs(img-img.max()) #Invert
        img = np.flipud(np.rot90(img))
        im = np.full((3,img.shape[0],img.shape[1]),0, dtype='float32')
        im[0:2,:,:] = img
        im[2,:,:] = (img-0.5)/5
        bgr = np.full(im[0].shape,0,dtype='float16')
        tth = np.linspace(0,180,im.shape[1])
        files = ['Reel1.0.' for i in range(im.shape[2])]
        return im, tth, files, None, {}, {}, bgr, [''], False
        
        
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