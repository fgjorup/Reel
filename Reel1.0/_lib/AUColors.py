# -*- coding: utf-8 -*-
"""
Last update: 12/01/2021
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