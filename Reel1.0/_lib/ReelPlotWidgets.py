# -*- coding: utf-8 -*-
"""
Last update: 27/08/2021
Frederik H. Gjørup
"""
import os
try:
    from PyQt5 import QtCore
    import pyqtgraph as pg
    import numpy as np
    from matplotlib import cm

except ModuleNotFoundError as error:
    if error.name in ('PyQt5', 'pyqtgraph', 'numpy','matplotlib'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')
    else:
        print('\n'+error.msg+'\nPlease use PIP to install\n')
    raise

from _lib.ReelMisc import roundup
from _lib.AUColors import AUlight, getColor
import ReelUserSettings as us

def convertColormapMPtoPG(cmap):
    """Convert matplotlib.cm.cmap [0.0-1.0] to pyqtgraph.ColorMap [0-255]"""
    pos = np.linspace(0,1,5)
    colors = [tuple(color*255) for color in cmap(pos)]
    return pg.ColorMap(pos=pos,color=colors)

class MultiImageWidget(pg.GraphicsLayoutWidget):
    
    sigHLineDragged = QtCore.Signal(object)
    sigVLineDragged = QtCore.Signal(object)
    
    def __init__(self,n_images=1,labels=()):
        pg.GraphicsLayoutWidget.__init__(self)
        self._setLabels(labels)
        self.setBackground((25,25,25))
        #Create imageItems
        self.images = [pg.ImageItem(border='w') for i in range(n_images)]     
        #Create histograms
        self.hist = pg.HistogramLUTItem()
        self.hist.gradient.setColorMap(convertColormapMPtoPG(cm.get_cmap(us.default_linear_colormap)))
        self.hist_2 = pg.HistogramLUTItem()
        self.hist_2.gradient.setColorMap(convertColormapMPtoPG(cm.get_cmap(us.default_divergent_colormap)))
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
        #Add vertical lines
        self.vlines = [pg.InfiniteLine(pos=1,angle=90, movable=True, pen='g') for i in range(n_images)]
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
            fname = os.path.abspath('_lib/icons/Main.raw')
            im = np.fromfile(fname, dtype='ubyte').reshape(230,230).astype(float)
            im = np.abs(im-im.max())
            data = np.flipud(np.rot90(im))
            if i<2:
                self.images[i].setImage(data)
            else:
                data = data-0.5
                self.images[i].setImage(data)
            
            #Add movable horizontal and vertical lines for data slicing
            v.addItem(self.hlines[i])
            v.addItem(self.vlines[i])
            self.hlines[i].sigDragged.connect(self._update_hline)
            self.vlines[i].sigDragged.connect(self._update_vline)       
            
        self.nextRow()
        for i,v in enumerate(self.views):
            #Add axis
            self.addItem(self.axes[i])
            if i == 1:
                self.nextCol()
            
        #Register initial horizontal line values
        self._hv_old = [round(v.value(),2) for v in self.hlines]
        self._vv_old = [round(v.value(),2) for v in self.vlines]
        #Register initial divergent colormap level
        self._l_old = [-1,1]
        #Histogram
        self.hist.setImageItem(self.images[0])
        self.hist.sigLevelsChanged.connect(self._setSharedLevels)
        self.hist.sigLookupTableChanged.connect(self._setSharedLookupTable)
        
        self.hist_2.setImageItem(self.images[-1])
        self.hist_2.sigLevelsChanged.connect(self._setDivergentLevels)
        
    def _update_hline(self):
        v_new = [v.value() for v in self.hlines if not round(v.value(),2) in self._hv_old]
        for hl in self.hlines:
            try:
                hl.setValue(v_new[0])
            except IndexError:
                pass
        self._hv_old = [round(v.value(),2) for v in self.hlines]
        self.sigHLineDragged.emit(self)

    def _update_vline(self):
        v_new = [v.value() for v in self.vlines if not round(v.value(),2) in self._vv_old]
        for vl in self.vlines:
            try:
                vl.setValue(v_new[0])
            except IndexError:
                pass
        self._vv_old = [round(v.value(),2) for v in self.vlines]
        self.sigVLineDragged.emit(self)

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
            if level<0.1:
                level=0.1
            self.hist_2.setLevels(min=-level ,max=level)
        self._l_old = self.hist_2.getLevels()
    
    def _setLinearRange(self):
        ymin,ymax = self.hist.getLevels()
        self.hist.setHistogramRange(ymin,ymax)
    
    def _setDivergentRange(self):
        _,level = self.hist_2.getLevels()
        self.hist_2.setHistogramRange(-level,level)
    
    def setData(self,index, im):
        xMax, yMax = im.shape
        self.images[index].setImage(im)
        self.views[index].setLimits(xMin=-5, xMax=xMax+5,
                                    minXRange=10, 
                                    yMin=-2, yMax=yMax+2,
                                    minYRange=10)
        self.views[index].autoRange()
        [h.setBounds((-1,yMax+1)) for h in self.hlines]
        [v.setBounds((-1,xMax+1)) for v in self.vlines]
    
    def autoRangeHistograms(self):
        self._setLinearRange()
        self._setDivergentRange()
    
    def autoRange(self):
        [v.autoRange() for v in self.views]
        self.autoRangeHistograms()
        
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

    def getVerticalLineVal(self):
        return self.vlines[0].value()
    
    def getScale(self):
        return (self.hist.getLevels(), self.hist_2.getLevels())
    
    def setScale(self,scale):
        lmin, lmax = scale[0]
        dmin, dmax = scale[1]
        self.hist.setLevels(min=lmin ,max=lmax)
        self.hist_2.setLevels(min=dmin ,max=dmax)
    
    def getViewRect(self):
        return self.views[0].viewRect()
    
    def setViewRange(self,vrect=None,xRange=None,yRange=None):
        """
        rect - (QRectF)
        xRange - [xmin, xmax]
        yRange - [ymin, ymax]
        """
        if not isinstance(vrect,type(None)):
            self.views[0].setRange(vrect,padding=0.0)
        elif not isinstance(xRange,type(None)):
            self.views[0].setRange(xRange)
        if not isinstance(yRange,type(None)):
            self.views[0].setRange(yRange)
            
            
#######################################################################################################################

class PlotPatternWidget(pg.PlotWidget):
    
    def __init__(self):
        pg.PlotWidget.__init__(self)
        self.setMenuEnabled(False,enableViewBoxMenu=None)
        #Set Background color to gray
        self.setBackground((25,25,25))
        self.setLabel('left','Intensity (a.u.)')
        self.setLabel('bottom','2θ (°)')
        self.addLegend()
        self.setLimits(xMin=0, xMax=180)
        #Add plots
        self.pobs = self.plot(x=[0],y=[0], name='Observed', pen=None, symbol='o', symbolPen='r', symbolSize=2)
        self.pcal = self.plot(x=[0],y=[0], name='Calculated')
        self.pres = self.plot(x=[0],y=[0], name='Residual', pen=pg.mkPen(color=(0,0,255), width=0.5))
        
        self.psub = {}
    
        self._getColors(exclude=('red','blue','gray'))
        
    def _getColors(self,user_colors=us.default_sub_plot_colors, exclude=()):
        colors = [getColor(c) for c in user_colors]
        colors += [getColor(c) for c in AUlight(exclude=exclude) if getColor(c) not in colors]
        self.colors = colors

    def addSubplot(self,key=None):
        try:
            color = self.colors.pop(0)
        except KeyError:
            self._getColors(exclude=('red','blue','gray'))
            color = self.colors.pop(0)
        pen = pg.mkPen(color=color, style=QtCore.Qt.DashLine)
        self.psub[key]=self.plot(x=[0],y=[0], name=key, pen=pen)

    def removeSubplots(self):
        for item in self.psub.values():
            self.removeItem(item)
        self._getColors(exclude=('red','blue','gray'))
        
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

#######################################################################################################################

class PlotSliceWidget(pg.PlotWidget):
    
    def __init__(self):
        pg.PlotWidget.__init__(self)
        self.setMenuEnabled(False,enableViewBoxMenu=None)
        #Set Background color to gray
        self.setBackground((25,25,25))
        self.setLabel('left','Intensity (a.u.)')
        self.setLabel('bottom','Slice (#)')
        self.addLegend()
        self.setLimits(xMin=0)
        #Add plots
        self.pobs = self.plot(x=[0],y=[0], name='Observed', pen=None, symbol='o', symbolPen='r', symbolSize=2)
        self.pcal = self.plot(x=[0],y=[0], name='Calculated')
        self.pres = self.plot(x=[0],y=[0], name='Residual', pen=pg.mkPen(color='b', width=0.5))
        
        self.psub = {}
        
        self._getColors(exclude=('red','blue','gray'))
        
    def _getColors(self,user_colors=us.default_sub_plot_colors, exclude=()):
        colors = [getColor(c) for c in user_colors]
        colors += [getColor(c) for c in AUlight(exclude=exclude) if getColor(c) not in colors]
        self.colors = colors
        
    def addSubplot(self,key=None):
        try:
            color = self.colors.pop(0)
        except KeyError:
            self._getColors(exclude=('red','blue','gray'))
            color = self.colors.pop(0)
        pen = pg.mkPen(color=color, style=QtCore.Qt.DashLine)
        self.psub[key]=self.plot(x=[0],y=[0], name=key, pen=pen)

    def removeSubplots(self):
        for item in self.psub.values():
            self.removeItem(item)
        self._getColors(exclude=('red','blue','gray'))
        
    def setSubplotData(self,key,x,y):    
        self.psub[key].setData(x,y)
        
    def setObsData(self,x,y):
         self.pobs.setData(x,y)
    
    def setCalData(self,x,y):
        #Remove NAN values 
        y = y[~np.isnan(y)]
        self.pcal.setData(x,y)    
        
    def setResData(self,x,y):
         self.pres.setData(x,y)

#######################################################################################################################

class PlotParametersWidget(pg.PlotWidget):
    
    sigVLineDragged = QtCore.Signal(object)
    
    def __init__(self):
        pg.PlotWidget.__init__(self)
        self.setMenuEnabled(False,enableViewBoxMenu=None)
        #Set Background color to gray
        self.setBackground((25,25,25))
        self.setLabel('left',us.primary_parameter_axis_label)
        self.setLabel('bottom','Pattern (#)')
        self.legend = self.addLegend()
        self.setLimits(xMin=-5, xMax=10000)#,
                       #yMin=0, yMax=2500)
        self.setRange(xRange=(-5,250),yRange=(0,100))
        #self.enableAutoRange(enable=True)
        #Add vertical line
        self.vline = pg.InfiniteLine(pos=1,angle=90, movable=True, pen='g')
        self.addItem(self.vline)
        self.vline.sigDragged.connect(self._update_vline)

        #Create first plotItem
        self.pI = self.plotItem
        self.pI.setLabels(left=us.primary_parameter_axis_label)
        self.pI.showAxis('right', show=True)
        self.pI.getAxis('right').setLabel(us.secondary_parameter_axis_label)   
        
        #Create a new ViewBox, link the right axis to its coordinate system
        self.v2 = pg.ViewBox()
        self.pI.scene().addItem(self.v2)
        self.pI.getAxis('right').linkToView(self.v2)
        self.v2.setXLink(self.pI)
        
        #Primary and secondary plots dictionary
        self.p0 = {}
        self.p1 = {}
    
        self._updateViews()
        self.pI.vb.sigResized.connect(self._updateViews)        
        
        self.pens = {}
        self.colors = {}
        self.symbols = {}
        
        #make a list of the unused colors from AUlight
        self.colorList = [getColor(c) for c in AUlight() if getColor(c) not in [getColor(s['color']) for s in us.styles.values()]]
            
        self.symbolList = ['o','s','t','d','+'] # Symbols:  * ‘o’ circle (default) * ‘s’ square * ‘t’ triangle * ‘d’ diamond * ‘+’ plus *
            
    def addPrimaryPlot(self,key):
        label, pen, color, symbol, symbolSize = self._getStyle(key)
        self.p0[key]=self.pI.plot(x=[0], 
                                  y=[0],
                                  name='← '+label,
                                  pen=pen,
                                  symbol=symbol,
                                  symbolPen=color,
                                  symbolBrush=color,
                                  symbolSize=symbolSize)

    def addSecondaryPlot(self,key):
        label, pen, color, symbol, symbolSize = self._getStyle(key)
        self.p1[key] = pg.PlotDataItem(x=[0],
                                       y=[0], 
                                       name=label+' →',
                                       pen=pen,
                                       symbol=symbol,
                                       symbolPen=color,
                                       symbolBrush=color,
                                       symbolSize=symbolSize)
        self.v2.addItem(self.p1[key])
        
    ## Handle view resizing 
    def _updateViews(self):
        ## view has resized; update auxiliary views to match
        self.v2.setGeometry(self.pI.vb.sceneBoundingRect())
        self.v2.linkedViewChanged(self.pI.vb, self.v2.XAxis)
        
    def clearPlot(self):
        for key in self.p0:
            self.p0[key].setData([-1],[-1])
        for key in self.p1:
            self.p1[key].setData([-1],[-1])
        self.legend.clear()
    
    def removePrimaryPlots(self):
        for item in self.p0.values():
            self.pI.removeItem(item)
        self.p0 = {}
    
    def removeSecondaryPlots(self):
        for item in self.p1.values():
            self.v2.removeItem(item)
        self.p1 = {}
            
    def setPrimaryData(self,key,x,y):
        p = self.p0[key]
        self.legend.addItem(p, p.name())
        p.setData(x,y)
        yMax = roundup(np.abs(y).max())
        if yMax < 1:
            yMax = 1.0
        self.setLimits(xMin=-2, xMax=len(x)+2,
               yMin=-yMax, yMax=yMax*2)
        self.vline.setBounds((-1,len(x)+1))
        self.autoRange()
    
    def setSecondaryData(self,key,x,y):
        p = self.p1[key]
        self.legend.addItem(p, p.name())
        self.pI.showAxis('right',show=True)
        p.setData(x,y)
        yMax = roundup(np.abs(y).max())
        if yMax < 1:
            yMax = 1.0
        self.v2.setLimits(xMin=-2, xMax=len(x)+2,
               yMin=-yMax, yMax=yMax*2)
        self.v2.autoRange()
            
    def updateVline(self,pos):
        self.vline.setValue(pos)
        
    def _update_vline(self):
        self.sigVLineDragged.emit(self)
        
    def _getColor(self,key):
        try:
            color = self.colors[key]
        except KeyError:
            if len(self.colorList)<1:
                #make a list of the unused colors from AUlight
                self.colorList = [getColor(c) for c in AUlight() if getColor(c) not in [getColor(s['color']) for s in us.styles.values()]]
            color = self.colorList.pop(0)
            self.colors[key] = color
        return color
    
    def _getSymbol(self,key):
        try:
            symbol = self.symbols[key]
        except KeyError:
            if len(self.symbolList)<1:
                self.symbolList = ['o','s','t','d','+'] # Symbols:  * ‘o’ circle (default) * ‘s’ square * ‘t’ triangle * ‘d’ diamond * ‘+’ plus *
            symbol = self.symbolList.pop(0)
            self.symbols[key] = symbol
        return symbol
    
    def _getPen(self,key):
        try:
            pen = self.pens[key]
        except KeyError:
            color = self._getColor(key)
            pen = pg.mkPen(color=color,
                           style=QtCore.Qt.SolidLine)
            self.pens[key] = pen
        return pen
    
    def _getStyle(self,key):
        """Get style as defined in user setting"""
        lineStyles = {'-'  :QtCore.Qt.SolidLine,
                  '--' :QtCore.Qt.DashLine,
                  '.'  :QtCore.Qt.DotLine,
                  '-.' :QtCore.Qt.DashDotLine,
                  '-..':QtCore.Qt.DashDotDotLine}
        try:
            style = us.styles[key]
            label = style['label']
            try:
                color = getColor(style['color'])
            except:
                #default to gray
                color = getColor('gray')
            lineStyle = lineStyles[style['lineStyle']]
            pen = pg.mkPen(color=color,
                           style=lineStyle)
            symbol = style['symbol']
            symbolSize = style['symbolSize']
        except:
            label = key
            pen = self._getPen(key)
            color = self._getColor(key)
            symbol = self._getSymbol(key)
            symbolSize = 4
        return label, pen, color, symbol, symbolSize
            



