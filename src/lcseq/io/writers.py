from pathlib import Path
import yaml
from typing import Dict, Any, List

class CompactChromDumper(yaml.SafeDumper):
    """Custom YAML Dumper that formats chromatogram lists in flow style."""
    def represent_list(self, data):
        """Force flow style (single line) for numeric lists."""
        if (isinstance(data, list) and
            len(data) > 0 and
            all(isinstance(x, (int, float)) for x in data)):
            return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
        return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=None)

class PeptideDataWriter:
    """Handles writing peptide data to various formats."""
    @staticmethod
    def write_yaml(data: Dict[str, Any], output_path: Path) -> None:
        """Write data to YAML format with special handling for chromatogram data."""
        with open(output_path, 'w') as f:
            yaml.dump(data, f, Dumper=CompactChromDumper, sort_keys=False)
