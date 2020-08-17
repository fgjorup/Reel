# Refinement-evaluator
Tool for visualizing Rietveld refinement results
By Frederik Gjørup

The software provided here is intended only for internal use at Department of Chemistry, Aarhus University, and should not be distributed outside of the institute.  

### Running the program ### 
The program is opened by running the "run_Reel.bat" file or double-clicking the corresponding short-cut.  
If the program does not open, check that the path to python.exe in "run_Reel.bat" line 4 is valid.

Files are opened from *Files->Open* by selected the desired files in the dialog box. **NB:** The file order might depend on the sorting order of the current folder!

"Reel" through frames by dragging the green lines, either in the *Surface* plots or in the *Parameter* plot.

### Requirements ###
Python 3.8.3 (Other versions of python 3 and modules might still work)  
Non-built-in python modules:  
Module | Version | pip install command
------ | ------- | -------------------
PyQt5 | v. 5.14.2 | pip install PyQt5
pyqtgraph | v. 0.11.0rc0 | pip install pyqtgraph
matplotlib | v. 3.2.1 | pip install matplotlib
numpy | v. 1.18.4+mkl | pip install numpy

\+ Requirements imposed by the modules. See `pip show [module]` for more information.
