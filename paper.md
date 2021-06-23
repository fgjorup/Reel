
---
title: 'Reel1.0 - A visualization tool for evaluating powder diffraction refinements'
tags:
  - Python
  - diffraction
  - TOPAS
  - Rietveld
  - pxrd
authors:
  - name: Frederik H. Gjørup , Mathias Mørch, & Mogens Christensen
    orcid: 0000-0003-3902-0247, 0000-0002-8022-5538, 0000-0001-6805-1232
    affiliation: "1"
affiliations:
 - name: Department of Chemistry and Interdisciplinary Nanoscience Center (iNANO), Aarhus University, Langelandsgade 140, 8000 Aarhus C, Denmark
   index: 1
date: 23 June 2021
bibliography: paper.bib

---

# Summary
The ever-growing  community for parameter-resolved x-ray and neutron diffraction, spurred by the rapid improvements in both detectors and sources for large-scale facilities, gives rise to the need for a fast and efficient evaluation approach for the large quantities of data produced during such experiments. As diffraction scientists we need to be able to compare both our raw data and our refined models in a consistent and user-friendly way. This is particularly true when refining in parameter-space (parametric refinement), where parameters such as time, temperature, field strength, pressure, etc. might be included in the models. Our proposed strategy focus on 2D visualizations (heatmaps) of the data, in order to qualitatively evaluate the observed, calculated, and residual data in parameter-space, with cross-comparison to key parameters.  

# Statement of need

`Reel1.0` is a Python based GUI, based on the `PyQt5` and `pyqtgraph` packages. The graphical interface is intended to make `Reel1.0` appealing to a broad audience (within the community), even for users with limited programming knowledge. User-friendliness is a key feature, as `Reel1.0` is a visualization tool, intended to be used on combination with other refinement software, such as TOPAS[@topas] or FullProf[@fullprof], and with room for expansion in the future.

`Reel1.0` is intended for users working with large x-ray and neutron diffraction datasets, such as in-situ and operando studies, across several scientific fields (chemistry, physics, materials science). The simplistic interface, efficiency, and user-friendliness of `Reel1.0` will allow the powder diffraction community to pursue increasingly advanced parameter-resolved experiments and the modeling of these.

# Acknowledgements

We acknowledge help, guidance, and fruitful discussions from Dr. Lennard Krause.

# References
