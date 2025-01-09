# src/chromatographicpeakpicking/core/prototypes/chromatogram.py
"""This module implements the Chromatogram prototype, which represents a chromatographic signal.

    Classes:
        Chromatogram: Represents a chromatographic signal with time and intensity data.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
import numpy as np

from src.chromatographicpeakpicking.core.interfaces.prototype import Prototype
from src.chromatographicpeakpicking.core.prototypes.peak import Peak

@dataclass
class Chromatogram(Prototype['Chromatogram']):
    """
    Represents a chromatographic signal with time and intensity data.

    Includes support for peaks, baseline, and corrected signals along with
    metadata for analysis results.
    """
    time: np.ndarray
    intensity: np.ndarray
    peaks: Set[Peak] = field(default_factory=set)
    baseline: Optional[np.ndarray] = None
    corrected_intensity: Optional[np.ndarray] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate inputs after initialization."""
        if not isinstance(self.time, np.ndarray):
            self.time = np.array(self.time)
        if not isinstance(self.intensity, np.ndarray):
            self.intensity = np.array(self.intensity)

    def clone(self, **kwargs: Any) -> 'Chromatogram':
        """Create a copy of the chromatogram with optional overrides."""
        return Chromatogram(
            time=kwargs.get('time', self.time.copy()),
            intensity=kwargs.get('intensity', self.intensity.copy()),
            peaks=kwargs.get('peaks', {p.clone() for p in self.peaks}),
            baseline=kwargs.get('baseline', self.baseline.copy() if self.baseline is not None else None),
            corrected_intensity=kwargs.get('corrected_intensity',
                self.corrected_intensity.copy() if self.corrected_intensity is not None else None),
            properties=kwargs.get('properties', self.properties.copy()),
            metadata=kwargs.get('metadata', self.metadata.copy())
        )

    def with_properties(self, **kwargs: Any) -> 'Chromatogram':
        """Create a new chromatogram with updated properties."""
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs: Any) -> 'Chromatogram':
        """Create a new chromatogram with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def validate(self) -> List[str]:
        """Validate the chromatogram and return any errors."""
        errors = []

        # Check data existence
        if len(self.time) == 0 or len(self.intensity) == 0:
            errors.append("Time and intensity arrays cannot be empty")

        # Check array lengths match
        if len(self.time) != len(self.intensity):
            errors.append("Time and intensity arrays must have the same length")

        # Check data types
        if not isinstance(self.time, np.ndarray):
            errors.append("Time must be a numpy array")
        if not isinstance(self.intensity, np.ndarray):
            errors.append("Intensity must be a numpy array")

        # Check for NaN/infinite values
        if np.any(~np.isfinite(self.time)):
            errors.append("Time array contains NaN or infinite values")
        if np.any(~np.isfinite(self.intensity)):
            errors.append("Intensity array contains NaN or infinite values")

        # Validate baseline if present
        if self.baseline is not None:
            if len(self.baseline) != len(self.intensity):
                errors.append("Baseline array length must match intensity array")
            if np.any(~np.isfinite(self.baseline)):
                errors.append("Baseline contains NaN or infinite values")

        # Validate corrected intensity if present
        if self.corrected_intensity is not None:
            if len(self.corrected_intensity) != len(self.intensity):
                errors.append("Corrected intensity array length must match intensity array")
            if np.any(~np.isfinite(self.corrected_intensity)):
                errors.append("Corrected intensity contains NaN or infinite values")

        # Validate peaks
        for peak in self.peaks:
            peak_errors = peak.validate()
            errors.extend(f"Peak validation error: {error}" for error in peak_errors)
            if peak.retention_time < np.min(self.time) or peak.retention_time > np.max(self.time):
                errors.append(f"Peak at {peak.retention_time} is outside chromatogram time range")

        return errors

    def with_peaks(self, peaks: Set[Peak]) -> 'Chromatogram':
        """Create a new chromatogram with updated peaks."""
        return self.clone(peaks=peaks)

    def with_baseline(self, baseline: np.ndarray) -> 'Chromatogram':
        """Create a new chromatogram with updated baseline."""
        return self.clone(baseline=baseline)

    def with_corrected_intensity(self, corrected: np.ndarray) -> 'Chromatogram':
        """Create a new chromatogram with updated corrected intensity."""
        return self.clone(corrected_intensity=corrected)

    def get_intensity_at(self, time: float) -> float:
        """Get intensity value at a specific time point (interpolated)."""
        return float(np.interp(time, self.time, self.intensity))

    def get_baseline_at(self, time: float) -> Optional[float]:
        """Get baseline value at a specific time point (interpolated)."""
        if self.baseline is None:
            return None
        return float(np.interp(time, self.time, self.baseline))

    def get_time_range(self) -> tuple[float, float]:
        """Get the time range of the chromatogram."""
        return float(np.min(self.time)), float(np.max(self.time))

    def get_intensity_range(self) -> tuple[float, float]:
        """Get the intensity range of the chromatogram."""
        return float(np.min(self.intensity)), float(np.max(self.intensity))
