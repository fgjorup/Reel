# -*- coding: utf-8 -*-
"""
Last update: 26/11/2021
Frederik H. Gjørup
"""
try:
    import numpy as np
except ModuleNotFoundError as error:
    if error.name in ('numpy'):
        print('\n'+error.msg+'\nPlease use PIP to install: "pip install '+error.name+'"\n')

def readXYY(fname):
    """Read *.xyy files from TOPAS parametric refinement. Return header and parameter dictionaries"""
    line=''
    header = []
    with open(fname,'r') as f:
        while not 'END OF HEADER' in line:
           line = f.readline() 
           header.append(line)
        parameters = f.readline().split()
        data = np.loadtxt(f,dtype='float32')
        # set columns values to nan, when calculated is 0
        data[:,2:][data[:,2]==0]=np.nan
    h = {'Filename':header[0]}
    comments = header.index('COMMENTS\n')
    h['Comments']=''.join(header[comments+1:-1])
    for s in header[1:comments]:
        if ':' in s:
            key, value = s.split(':')
            if key == 'Wavelength (Ã…)':
                key = 'Wavelength (Å)'
        h[key]=value
    dic = {p:data[:,i] for i,p in enumerate(parameters)}
    return h, dic


def readPRF(fname):      
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
    content = np.array(content, dtype='float32')
    
    tth = content[:,0]
    yobs = content[:,1]
    ycal = content[:,2]
    res = content[:,3]
    bckg = content[:,4]
    mask = np.array(mask, dtype='float32')
    if len(mask)>0:
        excl_reg = (tth < mask[0,0]) | (tth > mask[0,1])
    else:
        excl_reg = np.full(tth.shape[0],True)
    for i in mask:
        excl_reg = ((tth < i[0]) | (tth > i[1])) & excl_reg
    #Invert True/False
    excl_reg = excl_reg==False
    return tth, yobs, ycal, res, bckg, temp, excl_reg, lambd


def readPrfAlt(fname):
    # Jana format
    tth, yobs, ycal, sig, tth_corr, flag, sub_plots, bckg, res = [],[],[],[],[],[],[],[],[]
    with open(fname,'r') as f:
       content = f.read()
    content = content.strip().strip('999.').split('999\n')
    header = content.pop(0)
    for n, s in enumerate(content):
        s =  np.array([x.split() for x in s.strip().split('\n') if not x =='999'],dtype='float32')
        tth.append(s[:,0])
        yobs.append(s[:,1])
        ycal.append(s[:,2])
        sig.append(s[:,3])
        tth_corr.append(s[:,4])
        flag.append(s[:,5])
        sub_plots.append({'Phase_{}'.format(i+1): val for i,val in enumerate(s[:,6:-1].T)})
        bckg.append(s[:,-1])
        res.append(yobs[n]-ycal[n])
    excl_reg = [x==False for x in flag]
    return tth_corr[0], yobs[0], ycal[0], res[0], bckg[0], excl_reg[0], sub_plots[0]


def readPAR(fname):
    """
    return:
    r           - np.array  shape: (datasets, datafiles, datapoints)
    I           - np.array  shape: (datasets, datafiles, datapoints)
    dist        - list [float, ...]
    lambd       - list [float, ...]
    x_corr      - list [float, ...]
    y_corr      - list [float, ...]
    dataset_id  - list [str, ..]
    datafile_id - list of tuple [(str,bool), ...]
    eta         - list [float, ...]
    """
    
    dataset_id = []
    datafile_id = []
    enabled = []
    dist = []
    x_corr = []
    y_corr = []
    lambd = []
    eta = [[]]
    r = [[[]]]
    I = [[[]]]
    i = 0
    n = 0
    with open(fname,'r') as f:
        for line in f: # Loop through all n datasets
            if '_pd_meas_dataset_id' in line:
                dataset_id.append(line.split()[-1].strip("'"))
                
                for line in f: # Reading header for each dataset
                    if '_riet_meas_datafile_name' in line:
                        datafile_id.append(line.split()[-1].strip("'"))
                        break
                    if line.startswith('_pd_instr_dist_spec/detc'):
                         dist.append(float(line.replace('(',' ').split()[1]))
                    if line.startswith('_inst_ang_calibration_center_x'):
                         x_corr.append(float(line.replace('(',' ').split()[1]))
                    if line.startswith('_inst_ang_calibration_center_y'):
                         y_corr.append(float(line.replace('(',' ').split()[1])) 
                    if line.startswith('_diffrn_radiation_wavelength '):
                        lambd.append(float(line.replace('(',' ').split()[1]))
                
                for line in f:
                    if '#end_subordinateObject_{}\n'.format(dataset_id[-1]) in line:
                        break
                    if '_riet_meas_datafile_name' in line:
                        datafile_id.append(line.split()[-1].strip("'"))
                    if '_pd_meas_angle_eta' in line:
                        e = float(line.split()[-1])
                    if '_riet_meas_datafile_fitting' in line:
                        enabled.append(line.split()[-1])
                    if '_pd_meas_number_of_points' in line:
                        num  = int(line.split()[-1])
                    if '_pd_meas_intensity_total' in line:
                        for line in f: # Reading observed data for each datafile
                            if line == '\n':
                                break 
                            x, y, _ = [float(s) for s in line.split()]
                            r[n][i].append(x)
                            I[n][i].append(y)
  
                        eta[n].append(e)
                        #End of datafile
                        if num<1: # Append nan in case of an empty datafile
                            # r[n][i].append(np.nan)
                            # I[n][i].append(np.nan)
                            try:
                                rmin=np.min(r[n][0])
                                #print(rmin)
                            except:
                                rmin=0.0
                            r[n][i].append(rmin)
                            I[n][i].append(0)
                            enabled[-1] = 'false' # Failsafe disabling of the corresponding .fit file
                            
                        if r[n][i][0]>r[n][i][-1]: # Reverse order if appropriate
                            r[n][i].reverse()
                            I[n][i].reverse()

                        r[n][i] = np.array(r[n][i]) # Convert list to array
                        r[n].append([]) # Append empty list for next datafile
                        I[n].append([])

                        i += 1
                #End of dataset
                r[n].pop(-1) # Remove empty list when all datafiles are appended
                r.append([[]]) # Append empty list for next dataset
                I[n].pop(-1)            
                I.append([[]])
                eta.append([])
                n += 1
                i = 0
    # Remove empty list when all dataset are appended            
    r.pop(-1) 
    I.pop(-1)
    eta.pop(-1)
    # Convert from list to numpy array
    r = np.array(r,dtype=object)
    I = np.array(I,dtype=object)
    datafile_id = [(datafile_id[i],s=='true') for i, s in enumerate(enabled)]
    return r, I, dist, lambd, x_corr ,y_corr, dataset_id, datafile_id, eta
    

def readFIT(fname):  #,dist,x_corr,y_corr):
    """Read *.fit file from MAUD. 2theta values are calculated from provided detector distance. Return dictionary with tth, I, and additional columns."""
    keys = ['r','I']
    with open(fname,'r') as f:
        # Read header
        for line in f:
            if 'loop_' in line:
                break  
        for line in f:
            if '#' in line:
                keys.append(line.split('#')[-1].strip())
            if not '_' in line:
                data = np.array([line.split()],dtype='float32')
                break
        s = np.array([l.split() for l in f.readlines()],dtype='float32')
        data = np.append(data,s,axis=0)
        if data[0,0]>data[1,0]:
            data = np.flipud(data)
    dic = {k:data[:,i] for i,k in enumerate(keys)}        
    return dic       # Read column labels


def readCSV(fname):
    c = np.loadtxt(fname,dtype='float32',delimiter=',')
    tth = c[0]
    im = np.rot90(c[1:,:],k=-1)
    return tth, im


def readDAT(fname,temp=None,lamb=None,ts=None,t=None):      
    with open(fname,'r') as file:
        for i in range(6):
            line = file.readline()
            if line.startswith('TEMP'):
                temp = float(line.split()[-1])
            elif line.startswith('!Wavelength:'):
                lamb = float(line.split()[-1])
            elif line.startswith('!Timestamp:'):
                ts = ' '.join(line.split()[1:])
            elif line.startswith('!Acquisition'):
                t = float(line.split()[-3])*float(line.split()[-1])
            if i == 3 and len(line.split())>=10:
                #If alternativ .dat format:
                tth, I, _ = readDatAlt(fname)
                return tth,I,temp,lamb,ts,t 
        content = np.loadtxt(file, skiprows = 0)
    tth, I = content[:,0], content[:,1]
    return tth,I,temp,lamb,ts,t


def readDatAlt(fname):
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
    return tth, np.array(I,dtype='float32'), np.array(sig,dtype='float32')


def readXYE(fname):
    sig=None
    with open(fname,'r') as file:
        content = np.loadtxt(file, skiprows = 0)
    if content.shape[1]<3:
        tth, I = content[:,0], content[:,1]
    else:
        tth, I, sig = content[:,0], content[:,1], content[:,2]
    return tth, I, sig

