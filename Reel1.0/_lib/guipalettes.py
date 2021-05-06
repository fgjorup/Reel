# -*- coding: utf-8 -*-
"""
Last update: 25/01/2021
Frederik H. Gjørup
"""
try:
    from PyQt5 import QtGui
except ModuleNotFoundError as error:
    if error.name in ('PyQt5'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')

def darkPalette():
    """Return a QPalette with predetermined colors (0-255 RGB)"""
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window,          QtGui.QColor( 53,  53,  53))
    palette.setColor(QtGui.QPalette.WindowText,      QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Base,            QtGui.QColor( 25,  25,  25))
    palette.setColor(QtGui.QPalette.AlternateBase,   QtGui.QColor( 53,  53,  53))
    palette.setColor(QtGui.QPalette.ToolTipBase,     QtGui.QColor(  0,   0,   0))
    palette.setColor(QtGui.QPalette.ToolTipText,     QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Text,            QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Button,          QtGui.QColor( 53,  53,  53))
    palette.setColor(QtGui.QPalette.ButtonText,      QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.BrightText,      QtGui.QColor(255,   0,   0))
    palette.setColor(QtGui.QPalette.Link,            QtGui.QColor( 42, 130, 218))
    palette.setColor(QtGui.QPalette.Highlight,       QtGui.QColor( 42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(  0,   0,   0))
    #QPalette.setColorGroup(cr, windowText, button, light, dark, mid, text, bright_text, base, window)
    palette.setColorGroup(QtGui.QPalette.Disabled,   QtGui.QColor( 53,  53,  53),
                                                     QtGui.QColor(  0,   0,   0),
                                                     QtGui.QColor( 25,  25,  25),
                                                     QtGui.QColor( 25,  25,  25),
                                                     QtGui.QColor( 25,  25,  25),
                                                     QtGui.QColor( 53,  53,  53),
                                                     QtGui.QColor(255,   0,   0),
                                                     QtGui.QColor( 25,  25,  25),
                                                     QtGui.QColor( 53,  53,  53))
    return palette
