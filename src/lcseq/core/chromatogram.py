# src/lcseq/core/chromatogram.py
"""
This module defines the Chromatogram class, which represents a chromatographic trace.

Classes:
    Chromatogram: Represents a chromatographic trace.
"""

# Standard library imports
from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np

# Local application imports
from src.lcseq.core.peak import Peak


@dataclass
class Chromatogram:
    """Represents a chromatographic trace.

    Attributes:
        times (np.ndarray): The times of the chromatogram.
        intensities (np.ndarray): The intensities of the chromatogram.
        properties (Dict): The properties of the chromatogram.
        peaks (List[Peak]): The peaks of the chromatogram.

    Methods:
        __post_init__: Ensure times and intensities are numpy arrays and validate inputs.
        get_slice: Get a sub-section of the chromatogram.
    """

    times: np.ndarray
    intensities: np.ndarray
    properties: Dict = field(default_factory=dict)
    peaks: List[Peak] = field(default_factory=list)

    def __post_init__(self):
        """Ensure times and intensities are numpy arrays and validate inputs.

        Raises:
            ValueError: If times and intensities do not have the same length or are not numeric.
        """
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

    def get_slice(self, start_time: float, end_time: float) -> "Chromatogram":
        """Get a sub-section of the chromatogram.

        Args:
            start_time (float): The start time of the sub-section.
            end_time (float): The end time of the sub-section.

        Returns:
            Chromatogram: A new Chromatogram object containing the sub-section.
        """
        mask = (self.times >= start_time) & (self.times <= end_time)
        new_properties = self.properties.copy()
        if "corrected_intensities" in self.properties:
            new_properties["corrected_intensities"] = self.properties[
                "corrected_intensities"
            ][mask]

        return Chromatogram(
            times=self.times[mask],
            intensities=self.intensities[mask],
            properties=new_properties,
        )
