# Chromatographic Peak Picking

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
![pytest](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pytest.yml/badge.svg)
[![Pylint](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pylint.yml/badge.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking/actions/workflows/pylint.yml)
[![GitHub last commit](https://img.shields.io/github/last-commit/Adiaslow/ChromatographicPeakPicking.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking/commits/main)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Adiaslow/ChromatographicPeakPicking.svg)](https://github.com/Adiaslow/ChromatographicPeakPicking)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project is a Python-based tool for chromatographic peak picking and analysis using the modular LC-Seq pipeline framework. The framework is designed to be highly configurable and extensible, allowing for the addition of custom components, configurations, and pipelines. The built-in pipelines are designed to replicate the behavior of the original LC-Seq pipeline (see GPP and CC), as well as a Standard (basic) pipeline that can be used as-is or as a starting point for new pipelines.

---

### Stock Pipelines

#### GPP

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

#### CC

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

#### Standard (demonstration/test pipeline)

The Standard pipeline is a basic demonstration/testing pipeline that can be used as-is or as a starting point for new pipelines. It relies on the following components:

- StandardInput: Reads the input data from a CSV file.
- StandardChromatogramAnalyzer: Analyzes the chromatogram data.
- StandardPeakDetector: Detects the peaks in the chromatogram data.
- StandardPeakAnalyzer: Analyzes the peaks in the chromatogram data.
- StandardChromatogramVisualizer: Visualizes the chromatogram data.
- StandardOutput: Writes the output data to a CSV file.

#### Hierarchical (demonstration/test pipeline)

The Hierarchical pipeline is a basic demonstration/testing pipeline that can also be used as-is or as a starting point for new pipelines which take advantage of the hierarchical truncation relationships of a null-encoded library. It relies on the following components:

- StandardInput: Reads the input data from a CSV file.
- StandardChromatogramAnalyzer: Analyzes the chromatogram data.
- StandardPeakDetector: Detects the peaks in the chromatogram data.
- StandardPeakAnalyzer: Analyzes the peaks in the chromatogram data.
- HierarchicalPeakSelector: Selects the peaks in the chromatogram data based on the hierarchical structure of the peptide and chromatogram.
- HierarchicalSynthesisValidator: Validates the synthesis of the peptide.
- HierarchyVisualizer: Visualizes the constructed hierarchy of the peptide library.
- HierarchicalChromatogramVisualizer: Visualizes the chromatogram with added hierarchy information.
- StandardOutput: Writes the output data to a CSV file.

---

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

---

## Installation

The base package can be installed using pip:

```bash
pip install lcseq
```

## Usage

### Stock Pipelines

#### GPP

```python
from lcseq.pipelines import GPPPipe

gpp = GPPPipe(input_file_path="data/gpp_input.csv")
gpp.run()
```

#### CC

```python
from lcseq.pipelines import CCPipe

cc = CCPipe(input_file_path="data/cc_input.csv")
cc.run()
```

#### StandardPipe

```python
from lcseq.pipelines import StandardPipe

standard = StandardPipe(input_file_path="data/standard_input.csv")
standard.run()
```

---

## Custom Pipelines

Custom pipelines can be created by extending the `Pipeline` class and implementing the `run` method. See `src/lcseq/pipelines/standard.py` for a basic example.

```python
# path/to/custom/pipeline.py

# Import the Pipeline class
from lcseq.pipeline import Pipeline

# Import the StandardInput and StandardOutput components
from lcseq.pipeline.components.io import StandardInput, StandardOutput

# Import custom components
from ..path.to.custom.components import (
    CustomComponent1,
    CustomComponent2,
    ...,
    CustomComponentN
)

# Initialize components with custom parameters
custom_component1 = CustomComponent1()
custom_component1.config.parameter1 = "value11"
custom_component1.config.parameter2 = "value21"
...
custom_component1.config.parameterN = "valueN1"

custom_component2 = CustomComponent2()
custom_component2.config.parameter1 = "value12"
custom_component2.config.parameter2 = "value22"
...
custom_component2.config.parameterN = "valueN2"

...

custom_componentN = CustomComponentN()
custom_componentN.config.parameter1 = "value1N"
custom_componentN.config.parameter2 = "value2N"
...
custom_componentN.config.parameterN = "valueNN"

# Initialize the pipeline
class CustomPipeline(Pipeline):
    def __init__(self, input_file_path: str, plot_chromatograms: bool):
        super().__init__([
            StandardInput(), # or CustomInput()
            custom_component1, # if custom config or CustomComponent1() for default config
            custom_component2, # if custom config or CustomComponent2() for default config
            ...,
            custom_componentN, # if custom config or CustomComponentN() for default config
            StandardChromatogramVisualizer(plot_chromatograms=plot_chromatograms) # or HierarchicalChromatogramVisualizer(),
            StandardOutput(input_file_path) # or CustomOutput(input_file_path)
        ])

    def run(self, input_data: ProcessableInput) -> ProcessableInput:
        return super().run(input_data)
        # Add custom logic here
        ...
        return input_data
```

---

## Custom Components

Custom components can be created by extending the `PipelineComponent` class and implementing the `process` method. See `src/lcseq/pipeline/base.py` for basic structure or any of the standard components for examples.

```python
# path/to/custom/component.py

# Standard library imports
import logging
...

# Import the PipelineComponent class
from lcseq.pipeline.components import PipelineComponent

# Local application imports
from src.lcseq.pipeline.input_types import (
    ProcessableInput,
    SinglePeptideInput,
    PeptideSetInput,
    PeptideHierarchyInput
)
from src.lcseq.core.peptide import Peptide
from src.lcseq.core.hierarchy import PeptideHierarchy

class CustomComponentConfig:
    ...

class CustomComponent(PipelineComponent):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = CustomComponentConfig()
    def process(self, input_data: ProcessableInput) -> ProcessableInput:
        # Add custom logic here
        ...
        return input_data

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        return super().process_peptide(input_data)
        # Add custom logic here
        ...
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        return super().process_peptide_set(input_data)
        # Add custom logic here
        ...
        return input_data

    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        return super().process_hierarchy(input_data)
        # Add custom logic here
        ...
        return input_data
```
