from abc import ABC, abstractmethod
from typing import Generic, TypeVar

Input = TypeVar('Input')
Output = TypeVar('Output')

class PipelineStage(Generic[Input, Output], ABC):
    @abstractmethod
    def process(self, data: Input) -> Output:
        pass
