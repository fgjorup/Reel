# -*- coding: utf-8 -*-
"""
Last update: 07/06/2021
Frederik H. Gjørup
"""

def AUlight(exclude=()):
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

def AUdark(exclude=()):
    """Return AU standard colors (light).
    Available colors: 'blue', 'purple', 'cyan', 'turquoise', 'green', 'yellow', 'orange', 'red', 'magenta', and 'gray'.
    
    Keyword arguments:
    exclude -- tuple of strings (default empty)
    """
    AU_colors = {'blue'     :(  0, 37, 70),
                 'purple'   :( 40, 28, 65),
                 'cyan'     :(  0, 62, 92),
                 'turquoise':(  0, 69, 67),
                 'green'    :( 66, 88, 33),
                 'yellow'   :( 99, 75,  3),
                 'orange'   :( 95, 52,  8),
                 'red'      :( 91, 12, 12),
                 'magenta'  :( 95,  0, 48),
                 'gray'     :( 75, 75, 74)}
    for ex in exclude:
        AU_colors.pop(ex)
    return AU_colors

def getColor(color,alpha=None,rgb_0to1=False):
    """Accepts a 0-255 rgb or rgba color as tuple or one of the following keywords:
        'blue', 'purple', 'cyan', 'turquoise', 'green', 'yellow', 'orange', 'red', 'magenta', or 'gray'
    or any of the above, preceded by 'dark ' (i.e. 'dark blue').
    
    alpha    - set the alpha-channel (int or float)
    rgb_0to1 - toggle 0-1 rgb or rgba format (bool) 
    
    return 0-255 rgb or rgba color as tuple.
    """
    if isinstance(color,tuple):
        color = color
    elif color.startswith('dark'):
        color = AUdark()[color.strip('dark ')]
    else:
        color = AUlight()[color]
    if isinstance(alpha,(int,float)):
        color = tuple([*color[0:3],alpha])
    if rgb_0to1:
        color = tuple([round(c/255,4) for c in color])
    return color