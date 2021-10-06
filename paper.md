
---
title: 'Reel1.0 - A visualization tool for evaluating powder diffraction refinements'  
tags:  
  - Python  
  - diffraction  
  - TOPAS  
  - Rietveld  
  - pxrd  
authors:  
- name: Frederik H. Gjørup
  orcid: 0000-0003-3902-0247
  affiliation: "1"

- name: Mathias Mørch
  orcid: 0000-0002-8022-5538
  affiliation: "1"

- name: Mogens Christensen
  orcid: 0000-0001-6805-1232
  affiliation: "1"

affiliations:
 - name: Department of Chemistry and Interdisciplinary Nanoscience Center (iNANO), Aarhus University, Langelandsgade 140, 8000 Aarhus C, Denmark
   index: 1
date: 23 June 2021
bibliography: paper.bib

---

# Summary
The ever-growing  community for parameter-resolved x-ray and neutron diffraction, spurred by the rapid improvements in both detectors and sources for large-scale facilities, gives rise to the need for a fast and efficient evaluation approach for the large quantities of data produced during such experiments. As diffraction scientists we need to be able to both visually and analytically compare our raw data and refined models in a consistent and user-friendly way. This is particularly true when refining in two dimensions, such as sequential or parametric refinements, where parameters such as time, temperature, field strength, pressure, etc. might be included in the models. Our proposed strategy focus on combined 1D and 2D visualizations (heatmaps) of the data, in order to qualitatively evaluate the observed, calculated, and residual data in parameter-space, with cross-comparison to key parameters. We accomplish this with a single-window interface, illustrated in \autoref{fig:figure_1}, where 1D and 2D data are easily compared with the moveable lines (or *Reel cursors*). Several datasets can be opened at once to quickly compare models. Using the simple customized *.xyy* file format allows any number of user-defined parameters to be plotted, such as temperature, pressure, R-values, or mean intensity.  

![Illustration of the single-window interface of Reel1.0. The interface is divided in three main sections: 2D surface plots (heatmaps), 1D diffraction pattern plot, and 1D parameter plot.\label{fig:figure_1}](figure_1.tiff)

# Statement of Need

`Reel1.0` is a Python based GUI, based on the `PyQt5` and `pyqtgraph` packages [@pyqtgraph]. The graphical interface is intended to make `Reel1.0` appealing to a broad audience (within the community), even for users with limited programming knowledge. User-friendliness is a key feature, as `Reel1.0` is a visualization tool, intended to be used on combination with other refinement software, such as TOPAS[@topas] or FullProf[@fullprof], and with room for expansion in the future.

`Reel1.0` is intended for users working with large x-ray and neutron diffraction datasets, such as in-situ and operando studies, across several scientific fields (chemistry, physics, materials science). The visualization tools provided by the `pyqtgraph` libraries allow multiple datasets of several hundred patterns to be evaluated at once, without compromising the stability of the program. The simplistic interface, efficiency, and user-friendliness of `Reel1.0` will allow the powder diffraction community to pursue increasingly advanced parameter-resolved experiments and the modeling of these.  
`Reel1.0` can be used at several steps in the diffraction data processing, both for evaluating raw data and for evaluating and comparing refinement models. A suggested workflow for diffraction data evaluation using Reel1.0 is outlined in \autoref{fig:figure_2}. During data collection, the raw data can be evaluated to ensure that an appropriate data quality is acquired. This includes evaluating parameters such as the signal-to-noise ratio, signal-to-background ratio, time-resolution, and angular-resolution. During initial assessment, a more thorough pre-modeling evaluation can be performed. Here, the now collected data is evaluated, in order to gather information needed for the modeling. This includes phase transition, impurity formation, changes in background, mean scattered intensity, and external parameters (when available). The initial assessment also serves as a quick quality-check, before the more time-consuming refinement is performed. The refinement is performed in an external software, e.g. FullProf or TOPAS, and the resulting output files are evaluated in `Reel1.0`. The modeling evaluation is particularly useful for direct visual assessment, both of 1D and 2D plots, but also for evaluating R-values and user-provided parameters (only for the *.xyy* format). The 2D residual surface plot is an exceptional tool for identifying systematic deviations in the model, such as asymmetry, diffuse scattering, or incorrect background modeling.  

![Example of a data processing flowchart using Reel1.0, along with examples of the associated data file formats. The formats .dat and .prf are based on standard FullProf formats, while the .xyy format is a custom file format, defined in the Ree1.0 Quick Guide.\label{fig:figure_2}](figure_2.tiff)

# Statement of Field

To our knowledge, no other software in the community provide an as easy and fast evaluation of both 1D and 2D diffraction patterns. While refinement software, such as FullProf Suite, MAUD[@maud], or TOPAS come with visualization tools for both 1D and 2D patterns, they lack the ability to combine the two. Examples of the visualization tools in FullProf Suite, MAUD, and TOPAS are illustrated in \autoref{fig:figure_3}.	
The aesthetics of the visualizations are of course subjective, however, it has been shown that certain colormaps, such as “rainbow” maps, can be misleading and in the worst case, result in scientifically wrong conclusions.[@nunez2018] As such, one should strive for using perceptually linear colormaps. Reel1.0 uses the perceptually linear and color vision deficiency friendly `cividis` colormap as default, but any colormap contained in the `Matplotlib` package is available.  

![Examples of other visualization tools in the powder diffraction community. a) A 1D diffraction pattern as visualized in FullProf Suites WinPlotr. b) 2D observed-calculated heatmaps for 72 patterns as visualized in MAUD. c) Observed, calculated, and residual waterfall plot as visualized in TOPAS.\label{fig:figure_3}](figure_3.tiff)

# Acknowledgements

We acknowledge help, guidance, and fruitful discussions from Dr. Lennard Krause.

# References
