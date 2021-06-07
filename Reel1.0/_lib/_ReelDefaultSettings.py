# -*- coding: utf-8 -*-
"""
Default settings for Reel - DO NOT MODIFY
"""
# General
work_directory = r''
default_file_extension = '*.xyy'  # '*.xyy, *.prf, *.par, *.dat, *.xye *.xy, *.csv'  

# Manual wavelength
default_wavelength = 1.7902 # Å

# Pattern plot
default_pattern_scale = 'linear' # 'linear', 'log10', 'logn', 'sqrt'
default_slice_integration_interval = (0,0) # integrate around index i from [i+x : i+(x+1)]
default_pattern_background_subtraction = False
default_sub_plots = ''
default_sub_plot_colors = ['yellow', 'turquoise', 'purple', 'dark gray','green'] # See note at bottom

# Surface plots
default_surface_scale = 'linear' # 'linear', 'log10', 'logn', 'sqrt'
default_surface_background_subtraction = False
default_linear_colormap = 'cividis' # For additional colormaps go to https://matplotlib.org/stable/tutorials/colors/colormaps.html
default_divergent_colormap = 'bwr' 

# Parameter plot
default_primary_parameter_plot = ['R_wp','R_p']
default_secondary_parameter_plot = ['Temperature (°C)','Temperature (K)']
primary_parameter_axis_label = 'Primary axis'
secondary_parameter_axis_label = 'Secondary axis'  
styles = {'R_wp'            :{'label'     :'<html>R<sub>wp</sub></html>',
                             'color'     :'dark green',
                             'symbol'    :'o',
                             'symbolSize':4,
                             'lineStyle' :'-',
                             'lineWidth' :1},
         
         
         'R_p'             :{'label'     :'<html>R<sub>p</sub></html>',
                             'color'     :'blue',
                             'symbol'    :'s',
                             'symbolSize':4,
                             'lineStyle' :'-',
                             'lineWidth' :1},
         
         
         'Temperature (°C)':{'label'     :'Temperature (°C)',
                             'color'     :'orange',
                             'symbol'    :'t',
                             'symbolSize':4,
                             'lineStyle' :'--',
                             'lineWidth' :1},
         
         
         'Temperature (K)' :{'label'     :'Temperature (K)',
                             'color'     :'orange',
                             'symbol'    :'t',
                             'symbolSize':4,
                             'lineStyle' :'--',
                             'lineWidth' :1},}

# symbols:   ‘o’ circle, ‘s’ square, ‘t’ triangle, ‘d’ diamond, ‘+’ plus
# linestyle: '-', '--' , '.', '-.', or '-..'
# colors:    0-255 rgb color as tuple or one of the following keywords:
#            'blue', 'purple', 'cyan', 'turquoise', 'green', 'yellow', 'orange', 'red', 'magenta', or 'gray'
#            or any of the above, preceded by 'dark ' (i.e. 'dark blue')