from dataclasses import dataclass, field
import logging
import numpy as np
from scipy import stats, signal
from typing import List, Tuple, Dict
from src.chromatographicpeakpicking.core.interfaces.analyzer import (
    Analyzer,
    AnalysisResult
)
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.types.config import (
    BaseConfig,
    ConfigMetadata,
    ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

@dataclass
class ChromatogramAnalyzerConfig(BaseConfig):
    """Configuration for chromatogram analysis."""
    def __init__(
        self,
        window_width: int = 15,
        window_overlap: float = 0.5,
        min_window_points: int = 5,
        variation_threshold: float = 1.5,
        min_region_width: int = 5,
        max_region_gap: int = 20,
        noise_percentile: float = 50.0,
        min_regions_required: int = 3,
        max_noise_variance: float = 2.0,
        edge_exclusion: float = 0.05,
        baseline_percentile: float = 10.0,
        drift_window: int = 100,
        smoothing_window: int = 5,
        outlier_threshold: float = 3.0
    ):
        super().__init__(metadata=ConfigMetadata(
            name="ChromatogramAnalyzerConfig",
            version="1.0",
            description="Configuration for Chromatogram Analyzer",
            defaults={
                "window_width": 15,
                "window_overlap": 0.5,
                "min_window_points": 5,
                "variation_threshold": 1.5,
                "min_region_width": 5,
                "max_region_gap": 20,
                "noise_percentile": 50.0,
                "min_regions_required": 3,
                "max_noise_variance": 2.0,
                "edge_exclusion": 0.05,
                "baseline_percentile": 10.0,
                "drift_window": 100,
                "smoothing_window": 5,
                "outlier_threshold": 3.0
            },
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters=locals())

class ChromatogramMetrics:
    """Container for chromatogram analysis metrics."""
    def __init__(self, metrics: Dict[str, float]):
        self.noise_metrics: Dict[str, float] = {}
        self.baseline_metrics: Dict[str, float] = {}
        self.area_metrics: Dict[str, float] = {}
        self.distribution_metrics: Dict[str, float] = {}
        self.quality_metrics: Dict[str, float] = {}
        self.process_metrics(metrics)

    def process_metrics(self, metrics: Dict[str, float]) -> None:
        """Organize metrics into categories."""
        for key, value in metrics.items():
            if key.startswith('noise_') or key == 'signal_to_noise':
                self.noise_metrics[key] = value
            elif key.startswith('baseline_'):
                self.baseline_metrics[key] = value
            elif key.endswith('_area'):
                self.area_metrics[key] = value
            elif key in ['skewness', 'kurtosis', 'dynamic_range']:
                self.distribution_metrics[key] = value
            elif key.startswith('signal_') or key.endswith('_roughness'):
                self.quality_metrics[key] = value

@dataclass
class ChromatogramAnalyzer(Analyzer[ChromatogramAnalyzerConfig, Chromatogram, ChromatogramMetrics]):
    """Analyzes chromatogram data to extract quality metrics."""
    config: ChromatogramAnalyzerConfig = field(default_factory=ChromatogramAnalyzerConfig)
    logger: logging.Logger = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def configure(self, config: ChromatogramAnalyzerConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def validate_config(self, config: ChromatogramAnalyzerConfig) -> ValidationResult:
        # Validation remains the same
        ...

    def analyze(self, data: Chromatogram) -> AnalysisResult[ChromatogramMetrics]:
        """Analyze chromatogram and compute metrics."""
        chromatogram = data
        self._validate_chromatogram(chromatogram)

        metrics = {}
        try:
            # Calculate all metrics
            metrics.update(self._calculate_noise_metrics(chromatogram))
            metrics.update(self._calculate_baseline_metrics(chromatogram))
            metrics.update(self._calculate_area_metrics(chromatogram))
            metrics.update(self._calculate_distribution_metrics(chromatogram))
            metrics.update(self._calculate_quality_metrics(chromatogram))

        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise RuntimeError(f"Failed to calculate metrics: {str(e)}") from e

        result = ChromatogramMetrics(metrics)
        return AnalysisResult(result=result, metadata=metrics)

    def _validate_chromatogram(self, chrom: Chromatogram) -> None:
        """Validate input chromatogram."""
        if not isinstance(chrom, Chromatogram):
            raise TypeError("Input must be a Chromatogram object")
        if chrom.intensity is None or chrom.time is None:
            raise ValueError("Chromatogram contains no signal data")
        if not isinstance(chrom.intensity, np.ndarray) or not isinstance(chrom.time, np.ndarray):
            raise ValueError("Chromatogram signals must be numpy arrays")
        if len(chrom.intensity) != len(chrom.time):
            raise ValueError("Time and intensity arrays must have same length")
        if not np.all(np.isfinite(chrom.time)) or not np.all(np.isfinite(chrom.intensity)):
            raise ValueError("Chromatogram signals contain NaN or infinite values")

    def _calculate_noise_metrics(self, chrom: Chromatogram) -> Dict[str, float]:
        moving_std = self._calculate_moving_std(chrom.intensity)
        quiet_regions = self._find_minimal_variation_regions(moving_std)

        if len(quiet_regions) < self.config.parameters["min_regions_required"]:
            noise_level = float(np.std(chrom.intensity))
        else:
            quiet_stds = []
            for start, end in quiet_regions:
                quiet_stds.extend(moving_std[start:end])
            noise_level = float(np.percentile(quiet_stds,
                                            self.config.parameters["noise_percentile"]))

        signal_range = float(np.max(chrom.intensity) - np.min(chrom.intensity))
        snr = float('inf') if noise_level == 0 else signal_range / noise_level

        return {
            'noise_level': noise_level,
            'signal_to_noise': snr
        }

    def _calculate_baseline_metrics(self, chrom: Chromatogram) -> Dict[str, float]:
        baseline_mean = float(np.percentile(chrom.intensity,
                                          self.config.parameters["baseline_percentile"]))
        try:
            coefficients = np.polyfit(chrom.time, chrom.intensity, 1)
            drift = float(coefficients[0])
        except np.exceptions.RankWarning:
            drift = float(np.nan)

        return {
            'baseline_mean': baseline_mean,
            'baseline_drift': drift
        }

    def _calculate_area_metrics(self, chrom: Chromatogram) -> Dict[str, float]:
        """Calculate area-related metrics."""
        zeros = np.zeros_like(chrom.intensity)
        positive_y = np.where(chrom.intensity > zeros, chrom.intensity, zeros)
        negative_y = np.where(chrom.intensity < zeros, chrom.intensity, zeros)

        total_area = float(np.trapezoid(chrom.intensity, chrom.time))
        positive_area = float(np.trapezoid(positive_y, chrom.time))
        negative_area = float(np.trapezoid(negative_y, chrom.time))

        return {
            'total_area': total_area,
            'positive_area': positive_area,
            'negative_area': negative_area
        }

    def _calculate_distribution_metrics(self, chrom: Chromatogram) -> Dict[str, float]:
        """Calculate distribution-related metrics."""
        skewness = float(stats.skew(chrom.intensity))
        kurtosis = float(stats.kurtosis(chrom.intensity))
        dynamic_range = float(np.max(chrom.intensity) - np.min(chrom.intensity))

        return {
            'skewness': skewness,
            'kurtosis': kurtosis,
            'dynamic_range': dynamic_range
        }

    def _calculate_quality_metrics(self, chrom: Chromatogram) -> Dict[str, float]:
        """Calculate signal quality metrics."""
        smoothness = float(np.mean(np.abs(np.diff(chrom.intensity))))
        roughness = float(np.std(np.diff(chrom.intensity)))

        return {
            'signal_smoothness': smoothness,
            'baseline_roughness': roughness
        }

    def _calculate_moving_std(self, intensity: np.ndarray) -> np.ndarray:
        """Calculate moving standard deviation."""
        pad_width = self.config.parameters["window_width"] // 2
        intensity_padded = np.pad(intensity, pad_width, mode='edge')

        window = np.ones(self.config.parameters["window_width"]) / self.config.parameters["window_width"]
        moving_mean = signal.convolve(intensity_padded, window, mode='valid')

        intensity_squared = intensity_padded ** 2
        moving_mean_squared = signal.convolve(intensity_squared, window, mode='valid')
        moving_var = moving_mean_squared - moving_mean ** 2

        moving_var = np.maximum(moving_var, 0)
        return np.sqrt(moving_var)

    def _find_minimal_variation_regions(self, moving_std: np.ndarray) -> List[Tuple[int, int]]:
        """Identify regions of minimal variation in the signal."""
        min_std = np.min(moving_std)
        threshold = min_std * self.config.parameters["variation_threshold"]

        start_idx = int(len(moving_std) * self.config.parameters["edge_exclusion"])
        end_idx = len(moving_std) - start_idx

        below_threshold = moving_std[start_idx:end_idx] < threshold

        regions = []
        current_start = None

        for i, is_quiet in enumerate(below_threshold, start=start_idx):
            if is_quiet and current_start is None:
                current_start = i
            elif not is_quiet and current_start is not None:
                if i - current_start >= self.config.parameters["min_region_width"]:
                    regions.append((current_start, i))
                current_start = None

        if current_start is not None and end_idx - current_start >= self.config.parameters["min_region_width"]:
            regions.append((current_start, end_idx))

        # Merge nearby regions
        merged_regions = []
        if regions:
            current_start, current_end = regions[0]
            for start, end in regions[1:]:
                if start - current_end <= self.config.parameters["max_region_gap"]:
                    current_end = end
                else:
                    merged_regions.append((current_start, current_end))
                    current_start, current_end = start, end
            merged_regions.append((current_start, current_end))

        return merged_regions
