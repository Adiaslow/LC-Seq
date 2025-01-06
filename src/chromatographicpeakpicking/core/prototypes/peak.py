from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from src.chromatographicpeakpicking.core.interfaces.prototype import Prototype

@dataclass
class Peak(Prototype['Peak']):
    """
    Represents a chromatographic peak with its characteristics.

    Stores peak attributes like retention time, height, area, and associated
    metadata such as integration parameters, quality metrics, etc.
    """
    retention_time: float
    height: float
    area: Optional[float] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self, **kwargs: Any) -> 'Peak':
        """Create a copy of the peak with optional overrides."""
        return Peak(
            retention_time=kwargs.get('retention_time', self.retention_time),
            height=kwargs.get('height', self.height),
            area=kwargs.get('area', self.area),
            start_time=kwargs.get('start_time', self.start_time),
            end_time=kwargs.get('end_time', self.end_time),
            properties=kwargs.get('properties', self.properties.copy()),
            metadata=kwargs.get('metadata', self.metadata.copy())
        )

    def with_properties(self, **kwargs: Any) -> 'Peak':
        """Create a new peak with updated properties."""
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs: Any) -> 'Peak':
        """Create a new peak with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def validate(self) -> List[str]:
        """Validate the peak and return any errors."""
        errors = []

        # Validate basic attributes
        if not isinstance(self.retention_time, (int, float)):
            errors.append("Retention time must be a number")
        if self.retention_time < 0:
            errors.append("Retention time must be non-negative")

        if not isinstance(self.height, (int, float)):
            errors.append("Height must be a number")
        if self.height <= 0:
            errors.append("Height must be positive")

        # Validate optional attributes
        if self.area is not None:
            if not isinstance(self.area, (int, float)):
                errors.append("Area must be a number")
            if self.area <= 0:
                errors.append("Area must be positive")

        if self.start_time is not None:
            if not isinstance(self.start_time, (int, float)):
                errors.append("Start time must be a number")
            if self.start_time < 0:
                errors.append("Start time must be non-negative")
            if self.start_time >= self.retention_time:
                errors.append("Start time must be before retention time")

        if self.end_time is not None:
            if not isinstance(self.end_time, (int, float)):
                errors.append("End time must be a number")
            if self.end_time <= self.retention_time:
                errors.append("End time must be after retention time")

        if self.start_time is not None and self.end_time is not None:
            if self.start_time >= self.end_time:
                errors.append("Start time must be before end time")

        return errors

    def width(self) -> Optional[float]:
        """Calculate peak width if start and end times are available."""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return None

    def with_integration_bounds(self, start_time: float, end_time: float) -> 'Peak':
        """Create a new peak with updated integration bounds."""
        return self.clone(start_time=start_time, end_time=end_time)

    def with_area(self, area: float) -> 'Peak':
        """Create a new peak with updated area."""
        return self.clone(area=area)

    def to_dict(self) -> Dict[str, Any]:
        """Convert peak to dictionary representation."""
        return {
            'retention_time': self.retention_time,
            'height': self.height,
            'area': self.area,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'width': self.width(),
            'properties': self.properties,
            'metadata': self.metadata
        }
