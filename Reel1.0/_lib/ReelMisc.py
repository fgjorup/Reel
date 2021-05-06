# -*- coding: utf-8 -*-
"""
Last update: 05/05/2021
Frederik H. Gjørup
"""
import os
try:
    import numpy as np
    from scipy.interpolate import griddata
except ModuleNotFoundError as error:
    if error.name in ('numpy','scipy'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')
        
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

def r2tth(x,dist):
    """Convert a numpy array of azimuthal radii to 2 theta"""
    return np.arctan(x/dist)*180/np.pi

def findFiles(path,extension='.dat'):
    files = [path+'/'+f for f in os.listdir(path) if f.endswith(extension)]        
    files.sort()
    return files

def commonName(names):
    """return common name from list of names"""
    name = names[0]
    for n in names[1:]:
        while not name in n:
            name = name[:-1]
    # strip common endings
    for s in [' ','(','.','/','\\','_']:
        name = name.strip(s)
    return name

def scaleArray(a,scale='linear',retain_sign=False):
        if scale == 'linear' or np.all(a==0.0):
            return a
        sign = np.sign(a)
        a = np.abs(a)
        if scale == 'log10':
            a = np.log10(a,where=a!=0)
        elif scale == 'logn':
            a = np.log(a,where=a!=0)
        elif scale == 'sqrt':
            a = np.sqrt(a,where=a!=0)
        if retain_sign:
            a *= sign
        return a

def centerCorrection(r, eta, x_corr, y_corr):
    """Correct detector center offset"""
    # Geometry correction
    # Pixel position
    p = np.array([np.cos(eta*np.pi/180)*r,np.sin(eta*np.pi/180)*r])
    # x/y center correction
    xy_corr = np.array([x_corr,y_corr])
    # Corrected azimuthal radius
    r_corr = np.array([np.linalg.norm(p_i-xy_corr) for p_i in p.T])
    return r_corr

def gridInterpolation(r,I,eta,x_corr,y_corr,dist,length,xi=None,yi=None,mask=None):
    """
    Interpolate z data from old unstructured x/y coordinates to new equidistant grid coordinates
        return
            xi   -  (m,) array - grid x coordinates 
            yi   -  (n,) array - grid y coordinates 
            zi   - (n,m) array - interpolated z values 
            mask - (n,m) array - boolean mask based on "original" x/y ranges
    """
    # Flatten to 1D arrays
    x = np.concatenate(r)
    y = np.concatenate([[eta[i]]*l.shape[0] for i,l in enumerate(r)])
    z = np.concatenate(I)

    # Correct for detector center offset
    x = centerCorrection(x, y, x_corr, y_corr)
    # Convert to 2 theta
    x = np.arctan(x/dist)*180/np.pi
    # Determine tth range
    tth_range = [r2tth(centerCorrection(np.array([ri[0],ri[-1]]), eta[i], x_corr, y_corr),dist) for i, ri in enumerate(r)]
    
    # Create equidistant grid values
    if isinstance(xi,type(None)):
        xi = np.linspace(x.min(), x.max(), length)
    if isinstance(yi,type(None)):
        yi = np.linspace(y.min(), y.max(), len(eta))
    Xi, Yi = np.meshgrid(xi,yi)
    # Create mask based on "original" 2theta range
    if isinstance(mask,type(None)):
        mask = np.full(Xi.shape,False, dtype=bool)
        for i, row in enumerate(Xi):
            mask[i,:][row<tth_range[i][0]] = True
            mask[i,:][row>tth_range[i][1]] = True
    
    # interpolate z data from old unstructured x/y coordinates to new equidistant grid coordinates
    zi = griddata((x,y), z, (Xi, Yi), method='linear')
    zi[mask]=np.nan
    return xi, yi, zi, mask




