# src/lcseq/core/chromatogram.py
from dataclasses import dataclass, field
from typing import List, Dict
import numpy as np
from src.lcseq.core.peak import Peak

@dataclass
class Chromatogram:
    """Represents a chromatographic trace."""
    times: np.ndarray
    intensities: np.ndarray
    properties: Dict = field(default_factory=dict)
    peaks: List[Peak] = field(default_factory=list)

    def __post_init__(self):
        """Ensure times and intensities are numpy arrays and validate inputs."""
        # Convert to numpy arrays if needed
        self.times = np.array(self.times, dtype=float)
        self.intensities = np.array(self.intensities, dtype=float)

        # Validate inputs
        if len(self.times) != len(self.intensities):
            raise ValueError("Times and intensities must have the same length")

        if not np.issubdtype(self.times.dtype, np.number):
            raise ValueError("Times must be numeric")

        if not np.issubdtype(self.intensities.dtype, np.number):
            raise ValueError("Intensities must be numeric")

        if len(self.times) > 0 and self.times[0] < 0:
            raise ValueError("Time values cannot be negative")

    def get_slice(self, start_time: float, end_time: float) -> 'Chromatogram':
        """Get a sub-section of the chromatogram."""
        mask = (self.times >= start_time) & (self.times <= end_time)
        return Chromatogram(
            times=self.times[mask],
            intensities=self.intensities[mask],
            properties=self.properties.copy()
        )
