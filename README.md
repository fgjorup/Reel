# Refinement-evaluator
Tool for visualizing Rietveld refinement results
By Frederik Gjørup

### Running the program ###
Please run the setup.bat the first time you use the program. After that, run it by running the "run_Reel.bat" file or double-clicking the corresponding short-cut.  
If the program does not open, check that the path to python.exe in "run_Reel.bat" line 5 is valid.

Files are opened from *Files->Open* by selected the desired files in the dialog box. **NB:** The file order might depend on the sorting order of the current folder!
Open several datasets by clicking the *Add dataset* button, and change between them by clicking their names, the *Next* or *Previous* buttons, or with ctrl+arrow keys.

"Reel" through frames by dragging the green lines, either in the *Surface* plots or in the *Parameter* plot, or by using the arrow keys.

Select which parameters to plot and which axis to plot them on in the *Parameter plot* menu.

You can change the user defined default settings by editing the *ReelUserSettings.py* file, and restore the default settings from the *Help* menu in Reel.

### Data formats ###
Reel accepts several common data formats, but for the full range of option, use the *.xyy* format, as described in the *Reel1.0 Quick Guide.pdf*.

### MAC Users ###
Open a terminal in the program folder and run "Refinement_evaluator_ver1.0.py" in python.

### Requirements ###
Python 3.8.3 (Other versions of python 3 and modules might still work)  
Non-built-in python modules:  
| Module | Version | pip install command |
| ------ | ------- | ------------------- |
| PyQt5 | v. 5.14.2 | pip install PyQt5 |
| pyqtgraph | v. 0.11.1 | pip install pyqtgraph |
| matplotlib | v. 3.3.3 | pip install matplotlib |
| numpy | v. 1.19.5 | pip install numpy |
| scipy | v. 1.6.0 | pip install scipy |

\+ Requirements imposed by the modules. See `pip show [module]` for more information.

### Contributing, feedback, and support ###
You can open a series of test files intended for debugging by running `Refinement_evaluator_ver1.0.py -debug`. 

All users are welcome to provide feedback, report issues, or suggest changes to the program, either by creating a new issue on the GitHub [repository](https://github.com/fgjorup/Reel) or by contacting me at <fgjorup@chem.au.dk>.  
