# src/lcseq/pipeline/pipeline.py
from typing import List
from .input_types import ProcessableInput
from .base import PipelineComponent

class Pipeline:
    def __init__(self, components: List[PipelineComponent]):
        self.components = components

    def run(self, input_data: ProcessableInput) -> ProcessableInput:
        """
        Run the pipeline on the given input data.

        Args:
            input_data: ProcessableInput object to be processed

        Returns:
            ProcessableInput: Processed data

        Raises:
            ValueError: If input_data is None or not a ProcessableInput instance
        """
        if input_data is None:
            raise ValueError("Input data cannot be None")

        if not isinstance(input_data, ProcessableInput):
            raise ValueError(f"Input data must be an instance of ProcessableInput, got {type(input_data)}")

        current_data = input_data
        for component in self.components:
            current_data = component.process(current_data)
        return current_data
