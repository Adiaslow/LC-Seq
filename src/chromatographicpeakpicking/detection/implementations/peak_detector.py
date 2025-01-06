from dataclasses import dataclass, field
from typing import List, Dict, Any
import numpy as np
from scipy.signal import find_peaks
from src.chromatographicpeakpicking.core.interfaces.detector import Detector, DetectionResult
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.prototypes.peak import Peak
from src.chromatographicpeakpicking.core.types.config import (
    BaseConfig,
    ConfigMetadata,
    ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

@dataclass
class PeakDetectorConfig(BaseConfig):
    """Configuration for peak detection."""
    def __init__(
        self,
        height_threshold: float = 0.1,
        prominence_threshold: float = 0.2,
        width_threshold: float = 5
    ):
        super().__init__(metadata=ConfigMetadata(
            name="PeakDetectorConfig",
            version="1.0",
            description="Configuration for Peak Detector",
            defaults={
                "height_threshold": 0.1,
                "prominence_threshold": 0.2,
                "width_threshold": 5
            },
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters={
            "height_threshold": height_threshold,
            "prominence_threshold": prominence_threshold,
            "width_threshold": width_threshold
        })

@dataclass
class PeakDetector(Detector[PeakDetectorConfig]):
    """Detects peaks in chromatogram data."""
    config: PeakDetectorConfig = field(default_factory=PeakDetectorConfig)

    def configure(self, config: PeakDetectorConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def validate_config(self, config: PeakDetectorConfig) -> ValidationResult:
        errors = []
        if config.parameters["height_threshold"] <= 0:
            errors.append("Height threshold must be positive.")
        if config.parameters["prominence_threshold"] <= 0:
            errors.append("Prominence threshold must be positive.")
        if config.parameters["width_threshold"] <= 0:
            errors.append("Width threshold must be positive.")
        return ValidationResult(is_valid=len(errors) == 0, messages=errors)

    def detect(self, chromatogram: Chromatogram) -> DetectionResult:
        """Detect peaks in chromatogram."""
        # Validate input
        self._validate_input(chromatogram)

        # Find peaks
        peak_indices, properties = self._find_peaks(chromatogram)

        # Create peak objects
        peaks = self._create_peaks(chromatogram, peak_indices, properties)

        # Calculate metrics
        metrics = self._calculate_metrics(peaks)

        return DetectionResult(peaks=peaks, metrics=metrics)

    def _validate_input(self, chromatogram: Chromatogram) -> None:
        """Validate chromatogram data."""
        if len(chromatogram.time) == 0 or len(chromatogram.intensity) == 0:
            raise ValueError("Empty chromatogram data")
        if len(chromatogram.time) != len(chromatogram.intensity):
            raise ValueError("Time and intensity arrays must have same length")
        if not np.all(np.isfinite(chromatogram.intensity)):
            raise ValueError("Intensity contains NaN or infinite values")

    def _find_peaks(self, data: Chromatogram) -> tuple[np.ndarray, Dict[str, Any]]:
        """Find peaks using scipy.signal."""
        return find_peaks(
            data.intensity,
            height=self.config.parameters["height_threshold"],
            prominence=self.config.parameters["prominence_threshold"],
            width=self.config.parameters["width_threshold"]
        )

    def _create_peaks(
        self,
        data: Chromatogram,
        indices: np.ndarray,
        properties: Dict[str, Any]
    ) -> List[Peak]:
        """Create Peak objects from detected peaks."""
        peaks = []
        for i, idx in enumerate(indices):
            peak = Peak(
                retention_time=float(data.time[idx]),
                height=float(data.intensity[idx]),
                area=float(properties.get('width_heights', [0])[i]),
                metadata={
                    'prominence': float(properties.get('prominences', [0])[i]),
                    'width': float(properties.get('widths', [0])[i])
                }
            )
            peaks.append(peak)
        return peaks

    def _calculate_metrics(self, peaks: List[Peak]) -> Dict[str, float]:
        """Calculate detection metrics."""
        if not peaks:
            return {
                'num_peaks': 0,
                'avg_height': 0.0,
                'avg_width': 0.0
            }

        return {
            'num_peaks': len(peaks),
            'avg_height': np.mean([p.height for p in peaks]),
            'avg_width': np.mean([p.metadata.get('width', 0) for p in peaks])
        }
