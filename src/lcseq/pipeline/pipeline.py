# src/lcseq/pipeline/pipeline.py
"""
This module contains the definition of the Pipeline class, which is used to process
data  through a sequence of components. Each component in the pipeline processes the
input data and passes the result to the next component in the sequence.

Classes:
    PipelineConfig: Configuration for pipeline behavior.
    Pipeline: Defines a pipeline of processing components.
"""

# Standard library imports
import logging
from dataclasses import dataclass
from typing import List

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import ProcessableInput

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for pipeline behavior.

    Attributes:
        hierarchical (bool): Whether to run the pipeline in hierarchical mode.
        plot_chromatograms (bool): Whether to plot chromatograms.
        input_file_path (str): The path to the input file.
    """

    hierarchical: bool = False
    plot_chromatograms: bool = False
    input_file_path: str = ""


class Pipeline:
    """Pipeline class for processing data through a sequence of components.

    A pipeline takes a list of components and executes them in sequence on an input,
    passing the output of each component as input to the next.

    Attributes:
        components (List[PipelineComponent]): List of PipelineComponent objects
            defining the processing steps.
        config (PipelineConfig): Configuration for pipeline behavior.
        logger (logging.Logger): Logger for logging messages.

    Methods:
        run: Executes the pipeline components in sequence on the input data.
        add_component: Adds a component to the pipeline.
        add_components: Adds multiple components to the pipeline.
        remove_component: Removes a component from the pipeline.
        remove_components: Removes multiple components from the pipeline.
        clear_components: Removes all components from the pipeline.
        get_component: Retrieves a component from the pipeline by index.
        get_components: Retrieves all components from the pipeline.
        get_config: Retrieves the configuration for the pipeline.
        set_config: Sets the configuration for the pipeline.
    """

    def __init__(
        self,
        components: List[PipelineComponent],
        config: PipelineConfig = None,  # type: ignore
    ) -> None:
        """Initializes the Pipeline with the provided components.

        Args:
            components (List[PipelineComponent]): The list of components to be used in
                the pipeline.
        """
        self.components: List[PipelineComponent] = components
        self.config: PipelineConfig = config or PipelineConfig()

        for component in self.components:
            component.pipeline = self

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

        current_data: ProcessableInput = input_data
        for component in self.components:
            current_data = component.process(current_data)
        return current_data

    def add_component(self, component: PipelineComponent) -> None:
        """Adds a component to the pipeline.

        Args:
            component (PipelineComponent): The component to add to the pipeline.
        """
        self.components.append(component)
        component.pipeline = self

    def add_components(self, components: List[PipelineComponent]) -> None:
        """Adds multiple components to the pipeline.

        Args:
            components (List[PipelineComponent]): The components to add to the pipeline.
        """
        for component in components:
            self.add_component(component)
        for component in components:
            component.pipeline = self

    def remove_component(self, component: PipelineComponent) -> None:
        """Removes a component from the pipeline.

        Args:
            component (PipelineComponent): The component to remove from the pipeline.
        """
        self.components.remove(component)

    def remove_components(self, components: List[PipelineComponent]) -> None:
        """Removes multiple components from the pipeline.

        Args:
            components (List[PipelineComponent]): The components to remove from the pipeline.
        """
        for component in components:
            self.remove_component(component)

    def clear_components(self) -> None:
        """Removes all components from the pipeline."""
        self.components = []

    def get_component(self, index: int) -> PipelineComponent:
        """Retrieves a component from the pipeline by index.

        Args:
            index (int): The index of the component to retrieve.

        Returns:
            PipelineComponent: The component at the given index.
        """
        return self.components[index]

    def get_components(self) -> List[PipelineComponent]:
        """Retrieves all components from the pipeline."""
        return self.components

    def get_config(self) -> PipelineConfig:
        """Retrieves the configuration for the pipeline."""
        return self.config

    def set_config(self, config: PipelineConfig) -> None:
        """Sets the configuration for the pipeline.

        Args:
            config (PipelineConfig): The configuration to set for the pipeline.
        """
        self.config = config
