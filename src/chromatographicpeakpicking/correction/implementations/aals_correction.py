from dataclasses import dataclass, field
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from src.chromatographicpeakpicking.core.interfaces.corrector import Corrector
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.types.config import (
    BaseConfig, ConfigMetadata, ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

@dataclass
class AALSConfig(BaseConfig):
    """Configuration for the AALS baseline correction."""
    def __init__(
        self,
        lambda_value: float = 1e4,
        p_value: float = 0.001,
        max_iterations: int = 10
    ):
        super().__init__(metadata=ConfigMetadata(
            name="AALSConfig",
            version="1.0",
            description="Configuration for AALS Baseline Corrector",
            defaults={
                "lambda_value": 1e2,
                "p_value": 0.001,
                "max_iterations": 10
            },
            schema={},
            validation_level=ConfigValidation.STRICT
        ), parameters={
            "lambda_value": lambda_value,
            "p_value": p_value,
            "max_iterations": max_iterations
        })

@dataclass
class AALSCorrector(Corrector[AALSConfig]):
    """Asymmetric Least Squares (AALS) baseline correction algorithm."""
    config: AALSConfig = field(default_factory=AALSConfig)

    def configure(self, config: AALSConfig) -> ValidationResult:
        validation_result = self.validate_config(config)
        if validation_result.is_valid:
            self.config = config
        return validation_result

    def validate_config(self, config: AALSConfig) -> ValidationResult:
        errors = []
        if config.parameters["lambda_value"] <= 0:
            errors.append("Lambda value must be greater than 0.")
        if config.parameters["p_value"] <= 0 or config.parameters["p_value"] >= 1:
            errors.append("P value must be between 0 and 1.")
        if config.parameters["max_iterations"] <= 0:
            errors.append("Maximum iterations must be greater than 0.")
        return ValidationResult(is_valid=len(errors) == 0, messages=errors)

    def correct(self, chromatogram: Chromatogram) -> Chromatogram:
        """Apply AALS baseline correction."""
        # Input validation
        self._validate_inputs(chromatogram)

        y = chromatogram.intensity
        length = len(y)

        # Create difference matrix
        diff_matrix = sparse.diags([1, -2, 1], [0, 1, 2], shape=(length, length))

        # Initialize weights and baseline
        weights = np.ones(length)
        baseline = np.ones(length)

        # Iterative optimization
        for _ in range(self.config.parameters["max_iterations"]):
            # Create weight matrix
            weight_matrix = sparse.spdiags(weights, 0, length, length)

            # Compute z matrix
            z_matrix = weight_matrix + \
                self.config.parameters["lambda_value"] * \
                diff_matrix.T.dot(diff_matrix)

            # Solve for baseline
            baseline = spsolve(z_matrix, weights * y)

            # Update weights
            weights = self.config.parameters["p_value"] * \
                (y > baseline) + (1 - self.config.parameters["p_value"]) * \
                (y <= baseline)

        return Chromatogram(
            time=chromatogram.time,
            intensity=chromatogram.intensity - baseline,
            metadata=chromatogram.metadata,
            peaks=chromatogram.peaks,
            baseline=baseline
        )

    def _validate_inputs(self, chromatogram: Chromatogram) -> None:
        """Validate chromatogram can be processed."""
        if len(chromatogram.intensity) < 3:
            raise ValueError("Chromatogram too short for baseline correction")
        if not np.all(np.isfinite(chromatogram.intensity)):
            raise ValueError("Input signal contains NaN or infinite values")
