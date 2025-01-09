from pathlib import Path
import yaml
from typing import Dict, Any, List

class CompactChromDumper(yaml.SafeDumper):
    """Custom YAML Dumper that formats chromatogram lists in flow style."""

    def represent_sequence(self, tag, sequence, flow_style=None):
        """Force flow style (single line) for numeric lists."""
        # If it's a list of numbers, use flow style
        if (isinstance(sequence, list) and
            len(sequence) > 0 and
            all(isinstance(x, (int, float)) for x in sequence)):
            flow_style = True
        return super().represent_sequence(tag, sequence, flow_style)

yaml.add_representer(list, CompactChromDumper.represent_sequence, Dumper=CompactChromDumper)

class PeptideDataWriter:
    """Handles writing peptide data to various formats."""

    @staticmethod
    def write_yaml(data: Dict[str, Any], output_path: Path) -> None:
        """Write data to YAML format with special handling for chromatogram data.

        Chromatogram time series data (times, intensities, scaled_intensities)
        will be written in a compact, single-line format instead of as individual
        YAML entries.

        Args:
            data: Dictionary containing peptide data
            output_path: Path to write the YAML file
        """
        with open(output_path, 'w') as f:
            yaml.dump(data, f, Dumper=CompactChromDumper, sort_keys=False)
