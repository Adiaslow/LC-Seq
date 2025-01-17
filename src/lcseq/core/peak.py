# src/lcseq/core/peak.py
from dataclasses import dataclass, field
from typing import Dict

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
