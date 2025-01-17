# tests/pipeline/test_standard.py
import pytest
import yaml
import logging
import numpy as np
from pathlib import Path
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.peak import Peak
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput
from src.lcseq.pipelines.standard import StandardPipe

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the BuildingBlockRegistry before and after each test."""
    BuildingBlockRegistry.clear()
    yield
    BuildingBlockRegistry.clear()

@pytest.fixture
def sample_data():
    """Load sample data from YAML file."""
    data_path = Path("tests/data/prepared_data.yaml")
    with open(data_path, "r") as f:
        return yaml.safe_load(f)

@pytest.fixture
def building_blocks(sample_data):
    """Create and register BuildingBlock objects from sample data."""
    bb_dict = {}
    for position, blocks in sample_data["building_blocks"].items():
        for name, block_data in blocks.items():
            bb = BuildingBlock(
                identifier=name,
                properties={
                    "name": name,
                    "smiles": block_data["smiles"],
                    "stereochem": block_data["stereochem"]
                }
            )
            BuildingBlockRegistry.register(bb)
            bb_dict[name] = bb
    return bb_dict

@pytest.fixture
def peptide_encodings(sample_data, building_blocks):
    """Create PeptideEncoding objects from sample data."""
    encodings = []
    for peptide_data in sample_data["peptides"]:
        # Create sequence from building blocks
        sequence = []
        for bb_name in peptide_data["sequence"]:
            try:
                block = BuildingBlockRegistry.get(bb_name)
                sequence.append(block)
            except KeyError:
                logger.warning(f"Could not find building block {bb_name}")
                continue

        # Skip if we couldn't find all building blocks
        if len(sequence) != len(peptide_data["sequence"]):
            continue

        # Create chromatogram with proper numpy arrays
        chromatogram = Chromatogram(
            times=np.array(peptide_data["chromatogram"]["times"], dtype=float),
            intensities=np.array(peptide_data["chromatogram"]["scaled_intensities"], dtype=float)
        )

        # Create peptide encoding with proper identifier and properties
        properties = {
            "identifier": peptide_data["identifier"],
            **peptide_data.get("properties", {})
        }
        encoding = PeptideEncoding(
            blocks=sequence,
            chromatogram=chromatogram,
            properties=properties
        )
        encodings.append(encoding)

    return encodings

@pytest.fixture
def single_peptide_input(peptide_encodings):
    """Create SinglePeptideInput from first valid peptide encoding."""
    if not peptide_encodings:
        pytest.skip("No valid peptide encodings available")

    encoding = peptide_encodings[0]
    peptide = Peptide(
        sequence=encoding.blocks,
        properties={"identifier": encoding.properties["identifier"], **encoding.properties}
    )
    peptide.add_encoding(encoding)
    return SinglePeptideInput(peptide)

def test_building_block_registry(building_blocks):
    """Test BuildingBlockRegistry functionality."""
    # Test registration
    assert len(BuildingBlockRegistry._blocks) > 0

    # Test structure and retrieval
    leu = BuildingBlockRegistry.get("Leu")
    assert leu.identifier == "Leu"
    assert leu.properties["name"] == "Leu"
    assert "smiles" in leu.properties
    assert "stereochem" in leu.properties
    assert "position" not in leu.properties  # Verify position is not stored

    # Test deep copy
    leu_copy = BuildingBlockRegistry.get("Leu")
    assert leu is not leu_copy
    assert leu == leu_copy

def test_peptide_structure(single_peptide_input):
    """Test peptide structure and encoding."""
    peptide = single_peptide_input.peptide
    assert peptide is not None
    assert len(peptide.sequence) == 3

    # Test encoding
    assert len(peptide.encodings) == 1
    encoding = peptide.encodings[0]
    assert encoding.chromatogram is not None
    assert isinstance(encoding.chromatogram.times, np.ndarray)
    assert isinstance(encoding.chromatogram.intensities, np.ndarray)

def test_chromatogram_data(peptide_encodings):
    """Test chromatogram data structure and validation."""
    for encoding in peptide_encodings:
        chromatogram = encoding.chromatogram
        assert len(chromatogram.times) == len(chromatogram.intensities)
        assert isinstance(chromatogram.times, np.ndarray)
        assert isinstance(chromatogram.intensities, np.ndarray)

        # Test slice functionality
        start_time = chromatogram.times[0]
        end_time = chromatogram.times[-1]
        slice_chrom = chromatogram.get_slice(start_time, end_time)
        assert len(slice_chrom.times) == len(chromatogram.times)

def test_pipeline_processing(single_peptide_input, caplog):
    """Test pipeline processing with sample data."""
    pipeline = StandardPipe("tests/data/prepared_data.yaml", plot_chromatograms=True)
    with caplog.at_level(logging.INFO):
        result = pipeline.run(single_peptide_input)

    assert result is not None
    assert isinstance(result, SinglePeptideInput)
    assert any("input for peptide" in record.message for record in caplog.records)

    # Test peak detection results
    peptide = result.peptide
    for encoding in peptide.encodings:
        if encoding.chromatogram.peaks: # type: ignore
            for peak in encoding.chromatogram.peaks: # type: ignore
                assert isinstance(peak, Peak)
                assert peak.start_time < peak.apex_time < peak.end_time
                assert peak.duration > 0

if __name__ == "__main__":
    pytest.main([__file__])
