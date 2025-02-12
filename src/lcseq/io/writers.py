# src/lcseq/io/writers.py
"""
This module provides classes for writing peptide data to various formats.
It includes a CompactChromDumper class for custom YAML dumping and a PeptideDataWriter
class for writing peptide data to YAML format with special handling for chromatogram data.

Classes:
    CompactChromDumper: Custom YAML Dumper that formats chromatogram lists in flow style.
    PeptideDataWriter: Handles writing peptide data to various formats.
"""

# Standard library imports
from pathlib import Path
import yaml
from typing import Dict, Any, List

# Local application imports

class CompactChromDumper(yaml.SafeDumper):
    """Custom YAML Dumper that formats chromatogram lists in flow style.
    
    Methods:
        represent_list: Force flow style (single line) for numeric lists.
    """
    def represent_list(self, data):
        """Force flow style (single line) for numeric lists.

        Args:
            data: The data to represent.

        Returns:
            yaml.Node: The represented data.
        """
        if (isinstance(data, list) and
            len(data) > 0 and
            all(isinstance(x, (int, float)) for x in data)):
            return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
        return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=None)

class PeptideDataWriter:
    """Handles writing peptide data to various formats.
    
    Methods:
        write_yaml: Write data to YAML format with special handling for chromatogram data.
    """
    @staticmethod
    def write_yaml(data: Dict[str, Any], output_path: Path) -> None:
        """Write data to YAML format with special handling for chromatogram data.

        Args:
            data (Dict[str, Any]): The data to write.
            output_path (Path): The path to the output file.
        """
        with open(output_path, 'w') as f:
            yaml.dump(data, f, Dumper=CompactChromDumper, sort_keys=False)
