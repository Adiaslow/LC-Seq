# tests/pipeline/test_pipeline.py
import pytest
import yaml
import logging
from pathlib import Path
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.building_block import BuildingBlock
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.hierarchy import PeptideHierarchy

from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput
from src.lcseq.pipelines.tpipe import TPipe

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def test_data():
    data_path = Path("tests/data/prepared_data.yaml")
    with open(data_path, 'r') as file:
        return yaml.safe_load(file)

@pytest.fixture
def building_blocks(test_data):
    """Create BuildingBlock objects from sample data."""
    bb_dict = {}
    for position, blocks in test_data["building_blocks"].items():
        for name, block_data in blocks.items():
            bb = BuildingBlock(
                identifier=name,
                properties={
                    "name": name,
                    "smiles": block_data["smiles"],
                    "stereochem": block_data["stereochem"]
                }
            )
            bb_dict[name] = bb
    return bb_dict

@pytest.fixture
def single_peptide_input(test_data, building_blocks):
    peptide_data = test_data['peptides'][0]
    sequence = [building_blocks[bb_id] for bb_id in peptide_data['sequence']]
    chromatogram = Chromatogram(
        times=peptide_data['chromatogram']['times'],
        intensities=peptide_data['chromatogram']['intensities']
    )
    peptide = Peptide(
        sequence=sequence,
        properties={"identifier": peptide_data["identifier"], **peptide_data.get('properties', {})}
    )
    peptide.add_encoding(PeptideEncoding(blocks=sequence, chromatogram=chromatogram))
    return SinglePeptideInput(peptide)

@pytest.fixture
def peptide_set_input(test_data, building_blocks):
    peptides = []
    for peptide_data in test_data['peptides']:
        sequence = [building_blocks[bb_id] for bb_id in peptide_data['sequence']]
        chromatogram = Chromatogram(
            times=peptide_data['chromatogram']['times'],
            intensities=peptide_data['chromatogram']['intensities']
        )
        peptide = Peptide(
            sequence=sequence,
            properties={"identifier": peptide_data["identifier"], **peptide_data.get('properties', {})}
        )
        peptide.add_encoding(PeptideEncoding(blocks=sequence, chromatogram=chromatogram))
        peptides.append(peptide)
    return PeptideSetInput(set(peptides))

@pytest.fixture
def peptide_hierarchy_input(test_data, building_blocks):
    root_peptide_data = test_data['peptides'][0]
    sequence = [building_blocks[bb_id] for bb_id in root_peptide_data['sequence']]
    chromatogram = Chromatogram(
        times=root_peptide_data['chromatogram']['times'],
        intensities=root_peptide_data['chromatogram']['intensities']
    )
    root_peptide = Peptide(
        sequence=sequence,
        properties={"identifier": root_peptide_data["identifier"], **root_peptide_data.get('properties', {})}
    )
    root_peptide.add_encoding(PeptideEncoding(blocks=sequence, chromatogram=chromatogram))
    hierarchy = PeptideHierarchy(root=root_peptide)
    return PeptideHierarchyInput(hierarchy=hierarchy)
