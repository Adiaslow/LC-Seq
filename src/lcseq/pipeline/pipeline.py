# src/lcseq/pipeline/pipeline.py
"""
This module contains the definition of the Pipeline class, which is used to process
data  through a sequence of components. Each component in the pipeline processes the
input data and passes the result to the next component in the sequence.

Classes:
    Pipeline: Defines a pipeline of processing components.
"""

from typing import List
from .input_types import ProcessableInput
from .base import PipelineComponent

class Pipeline:
    """Pipeline class for processing data through a sequence of components.

    A pipeline takes a list of components and executes them in sequence on an input,
    passing the output of each component as input to the next.

    Attributes:
        components (List[PipelineComponent]): List of PipelineComponent objects
            defining the processing steps.
    """

    def __init__(self, components: List[PipelineComponent]):
        """Initializes the Pipeline with the provided components.

        Args:
            components (List[PipelineComponent]): The list of components to be used in
                the pipeline.
        """
        self.components = components

    def run(self, input_data: ProcessableInput) -> ProcessableInput:
        """Executes the pipeline components in sequence on the input data.

        Args:
            input_data (ProcessableInput): The input data to be processed.

        Returns:
            ProcessableInput: The processed data.

        Raises:
            ValueError: If the input_data is None or not an instance of
                ProcessableInput.
        """
        if input_data is None:
            raise ValueError("Input data cannot be None")

        if not isinstance(input_data, ProcessableInput):
            raise ValueError(
                "Input data must be an instance of ProcessableInput, "
                f"got {type(input_data)}"
            )

        current_data = input_data
        for component in self.components:
            current_data = component.process(current_data)
        return current_data
