from dataclasses import dataclass, field
import numpy as np
from scipy.optimize import curve_fit
from typing import Dict, Any, Optional
from src.chromatographicpeakpicking.core.interfaces.analyzer import (
    Analyzer,
    AnalysisResult
)
from src.chromatographicpeakpicking.core.types.config import (
    BaseConfig,
    ConfigMetadata,
    ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.prototypes.peak import Peak

from dataclasses import dataclass, field
import numpy as np
from scipy.optimize import curve_fit
from typing import Dict, Any, Optional
from src.chromatographicpeakpicking.core.interfaces.analyzer import (
    Analyzer,
    AnalysisResult
)
from src.chromatographicpeakpicking.core.types.config import (
    BaseConfig,
    ConfigMetadata,
    ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.prototypes.peak import Peak

@dataclass
class PeakAnalyzerConfig(BaseConfig):
    """Configuration for peak analysis."""
    def __init__(
        self,
        window_size: int = 20,
        min_signal_to_noise: float = 0.0,
        min_r2_score: float = 0.0
    ):
        super().__init__(metadata=ConfigMetadata(
            name="PeakAnalyzerConfig",
            version="1.0",
            description="Configuration for Peak Analyzer",
            defaults={
                "window_size": 20,
                "min_signal_to_noise": 0.0,
                "min_r2_score": 0.0
            },
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters={
            "window_size": window_size,
            "min_signal_to_noise": min_signal_to_noise,
            "min_r2_score": min_r2_score
        })

class PeakAnalysisResult:
    """Results from peak analysis."""
    def __init__(
        self,
        fit_params: Dict[str, float],
        quality_metrics: Dict[str, float]
    ):
        self.fit_params = fit_params
        self.quality_metrics = quality_metrics

@dataclass
class PeakAnalyzer(Analyzer[PeakAnalyzerConfig, Peak, PeakAnalysisResult]):
    """Analyzes individual peak characteristics."""
    config: PeakAnalyzerConfig = field(default_factory=PeakAnalyzerConfig)
    time_points: np.ndarray = field(default_factory=lambda: np.array([]))
    intensities: np.ndarray = field(default_factory=lambda: np.array([]))

    def configure(self, config: PeakAnalyzerConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def validate_config(self, config: PeakAnalyzerConfig) -> ValidationResult:
        errors = []
        if config.parameters["window_size"] <= 0:
            errors.append("Window size must be positive")
        if config.parameters["min_signal_to_noise"] < 0:
            errors.append("Minimum signal to noise ratio must be non-negative")
        if not 0 <= config.parameters["min_r2_score"] <= 1:
            errors.append("Minimum R² score must be between 0 and 1")
        return ValidationResult(is_valid=len(errors) == 0, messages=errors)

    def analyze(self, data: Peak) -> AnalysisResult[PeakAnalysisResult]:
        """Analyze a single peak."""
        peak = data
        self._validate_peak(peak)

        fit_params = self._fit_gaussian(peak)
        quality_metrics = self._calculate_quality_metrics(peak, fit_params)

        result = PeakAnalysisResult(
            fit_params=fit_params,
            quality_metrics=quality_metrics
        )

        return AnalysisResult(
            result=result,
            metadata={**fit_params, **quality_metrics}
        )

    def _validate_peak(self, peak: Peak) -> None:
        """Validate peak data."""
        if len(self.time_points) == 0 or len(self.intensities) == 0:
            raise ValueError("Time points and intensities must be set before analysis")
        if len(self.time_points) != len(self.intensities):
            raise ValueError("Time points and intensities must have same length")
        if peak.retention_time < min(self.time_points) or peak.retention_time > max(self.time_points):
            raise ValueError("Peak retention time outside of data range")

    def _fit_gaussian(self, peak: Peak) -> Dict[str, float]:
        """Fit Gaussian to peak."""
        def gaussian(x: np.ndarray, amplitude: float, mean: float, std: float) -> np.ndarray:
            return amplitude * np.exp(-(x - mean)**2 / (2 * std**2))

        # Get region around peak
        peak_idx = np.argmin(np.abs(self.time_points - peak.retention_time))
        window = self.config.parameters["window_size"]
        start_idx = max(0, peak_idx - window)
        end_idx = min(len(self.time_points), peak_idx + window)

        x = self.time_points[start_idx:end_idx]
        y = self.intensities[start_idx:end_idx]

        try:
            popt, _ = curve_fit(
                gaussian, x, y,
                p0=[peak.height, peak.retention_time, 1.0]
            )
            return {
                'amplitude': float(popt[0]),
                'mean': float(popt[1]),
                'std': float(popt[2])
            }
        except RuntimeError:
            return {
                'amplitude': peak.height,
                'mean': peak.retention_time,
                'std': 1.0
            }

    def _calculate_quality_metrics(
        self,
        peak: Peak,
        fit_params: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate peak quality metrics."""
        peak_idx = np.argmin(np.abs(self.time_points - peak.retention_time))
        window = self.config.parameters["window_size"]
        start_idx = max(0, peak_idx - window)
        end_idx = min(len(self.time_points), peak_idx + window)

        signal = self.intensities[start_idx:end_idx]
        noise = np.std(signal - np.mean(signal))

        return {
            'signal_to_noise': float(peak.height / noise if noise > 0 else 0.0),
            'gaussian_r2': self._calculate_r2(
                self.time_points[start_idx:end_idx],
                signal,
                fit_params
            ),
            'peak_symmetry': self._calculate_symmetry(signal),
            'peak_capacity': self._calculate_capacity(fit_params['std'])
        }

    def _calculate_r2(
        self,
        x: np.ndarray,
        y: np.ndarray,
        fit_params: Dict[str, float]
    ) -> float:
        """Calculate R² for Gaussian fit."""
        def gaussian(x: np.ndarray) -> np.ndarray:
            return fit_params['amplitude'] * np.exp(
                -(x - fit_params['mean'])**2 / (2 * fit_params['std']**2)
            )

        y_pred = gaussian(x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)

        return float(1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0)

    def _calculate_symmetry(self, signal: np.ndarray) -> float:
        """Calculate peak symmetry."""
        peak_idx = np.argmax(signal)
        left_half = signal[:peak_idx]
        right_half = signal[peak_idx:]

        # Interpolate to same length if necessary
        if len(left_half) != len(right_half):
            target_length = min(len(left_half), len(right_half))
            left_half = np.interp(
                np.linspace(0, 1, target_length),
                np.linspace(0, 1, len(left_half)),
                left_half
            )
            right_half = np.interp(
                np.linspace(0, 1, target_length),
                np.linspace(0, 1, len(right_half)),
                right_half
            )

        return float(np.sum(np.abs(left_half - np.flip(right_half))) / len(left_half))

    def _calculate_capacity(self, std: float) -> float:
        """Calculate peak capacity."""
        return float((max(self.time_points) - min(self.time_points)) / (4 * std))
