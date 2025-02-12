# Chromatographic Peak Picking
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
![pytest](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pytest.yml/badge.svg)
[![Pylint](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pylint.yml/badge.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pylint.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/Adiaslow/ChromatographicPeakPicking.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking/commits/main)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Adiaslow/ChromatographicPeakPicking.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project is a Python-based tool for chromatographic peak picking and analysis using the modular LC-Seq pipeline framework. The framework is designed to be highly configurable and extensible, allowing for the addition of custom components, configurations, and pipelines. The built-in pipelines are designed to replicate the behavior of the original LC-Seq pipeline (see GPP and CC), as well as a Standard (basic) pipeline that can be used as-is or as a starting point for new pipelines.

### GPP
The GPP pipeline is designed to replicate the behavior of the original LC-Seq Gaussian Peak Picking pipeline. It relies on the following components:
- StandardInput: Reads the input data from a CSV file.
- StandardChromatogramAnalyzer: Analyzes the chromatogram data.
- SWMChromatogramCorrector: Corrects the chromatogram data.
- StandardPeakDetector: Detects the peaks in the chromatogram data.
- StandardPeakAnalyzer: Analyzes the peaks in the chromatogram data.
- GPPPeakAnalyzer: Computes the Gaussian curve fit on the corrected chromatogram data.
- GPPPeakSelector: Selects the peaks in the chromatogram data based on the corrected Gaussian curve fit.
- StandardChromatogramVisualizer: Visualizes the chromatogram data.
- StandardOutput: Writes the output data to a CSV file.

### CC
The CC pipeline is designed to replicate the behavior of the original LC-Seq Classic Chrome pipeline. It relies on the following components:
- StandardInput: Reads the input data from a CSV file.
- StandardChromatogramAnalyzer: Analyzes the chromatogram data.
- AALSChromatogramCorrector: Corrects the chromatogram data using the Adaptive Asymmetric Least Squares (AALS) algorithm.
- StandardPeakDetector: Detects the peaks in the chromatogram data.
- StandardPeakAnalyzer: Analyzes the peaks in the chromatogram data.
- HierarchicalPeakSelector: Selects the peaks in the chromatogram data based on the hierarchical structure of the peptide and chromatogram and peak properties.
- HierarchicalChromatogramVisualizer: Visualizes the chromatogram with added hierarchy information.
- HierarchyVisualizer: Visualizes the constructed hierarchy of the peptide library.
- StandardOutput: Writes the output data to a CSV file.

### StandardPipe
The Standard pipeline is a basic pipeline that can be used as-is or as a starting point for new pipelines. It relies on the following components:
- StandardInput: Reads the input data from a CSV file.
- StandardChromatogramAnalyzer: Analyzes the chromatogram data.
- StandardPeakDetector: Detects the peaks in the chromatogram data.
- StandardPeakAnalyzer: Analyzes the peaks in the chromatogram data.
- StandardChromatogramVisualizer: Visualizes the chromatogram data.
- StandardOutput: Writes the output data to a CSV file.

## Features

- Configurable pipelines with a modular design
- Highly extensible
  - Components are designed to be as independent as possible
  - Components can be reused in different pipelines
  - Components can be swapped out with custom implementations
  - Components can be used in different orders
- Highly configurable
  - Pipelines can be configured with custom parameters
  - Components can be configured with custom parameters
- Visualization of chromatogram data
  - Single chromatogram
  - Multiple chromatograms
  - Hierarchy of chromatograms

## Installation
The base package can be installed using pip:
```bash
pip install lcseq
```

## Usage

