# src/lcseq/core/peak.py
"""
This module defines the Peak class, which represents a chromatographic peak.

Classes:
    Peak: Represents a chromatographic peak.
"""

# Standard library imports
from dataclasses import dataclass, field
from typing import Dict

# Local application imports

@dataclass
class Peak:
    """Represents a chromatographic peak.
    
    Attributes:
        start_time (float): The start time of the peak.
        apex_time (float): The apex time of the peak.
        end_time (float): The end time of the peak.
        start_intensity (float): The start intensity of the peak.
        apex_intensity (float): The apex intensity of the peak.
        end_intensity (float): The end intensity of the peak.
        properties (Dict): The properties of the peak.

    Methods:
        duration: Calculate the duration of the peak.
    """
    start_time: float
    apex_time: float
    end_time: float
    start_intensity: float
    apex_intensity: float
    end_intensity: float
    properties: Dict = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Calculate peak duration.
        
        Returns:
            float: The duration of the peak.
        """
        return self.end_time - self.start_time
