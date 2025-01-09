# src/lcseq/core/chromatogram.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np

@dataclass
class Peak:
    """Represents a chromatographic peak."""
    start_time: float
    apex_time: float
    end_time: float
    start_intensity: float
    apex_intensity: float
    end_intensity: float
    properties: Dict = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Calculate peak duration."""
        return self.end_time - self.start_time

@dataclass
class Chromatogram:
    """Represents a chromatographic trace."""
    times: np.ndarray
    intensities: np.ndarray
    properties: Dict = field(default_factory=dict)
    peaks: List[Peak] = field(default_factory=list)

    def __post_init__(self):
        """Ensure times and intensities are numpy arrays."""
        self.times = np.array(self.times)
        self.intensities = np.array(self.intensities)
        if len(self.times) != len(self.intensities):
            raise ValueError("Times and intensities must have the same length")

    def get_slice(self, start_time: float, end_time: float) -> 'Chromatogram':
        """Get a sub-section of the chromatogram."""
        mask = (self.times >= start_time) & (self.times <= end_time)
        return Chromatogram(
            times=self.times[mask],
            intensities=self.intensities[mask],
            properties=self.properties.copy()
        )
