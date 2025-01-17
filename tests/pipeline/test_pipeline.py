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
def single_peptide_input(test_data):
    peptide_data = test_data['peptides'][0]
    sequence = [BuildingBlock(identifier=bb_id, properties=test_data['building_blocks'][bb_id]) for bb_id in peptide_data['sequence']]
    chromatogram = Chromatogram(times=peptide_data['chromatogram']['times'], intensities=peptide_data['chromatogram']['intensities'])
    peptide = Peptide(sequence=sequence, properties=peptide_data['properties'])
    peptide.add_encoding(PeptideEncoding(blocks=sequence, chromatogram=chromatogram))
    return SinglePeptideInput(peptide)

@pytest.fixture
def peptide_set_input(test_data):
    peptides = []
    for peptide_data in test_data['peptides']:
        sequence = [BuildingBlock(identifier=bb_id, properties=test_data['building_blocks'][bb_id]) for bb_id in peptide_data['sequence']]
        chromatogram = Chromatogram(times=peptide_data['chromatogram']['times'], intensities=peptide_data['chromatogram']['intensities'])
        peptide = Peptide(sequence=sequence, properties=peptide_data['properties'])
        peptide.add_encoding(PeptideEncoding(blocks=sequence, chromatogram=chromatogram))
        peptides.append(peptide)
    return PeptideSetInput(set(peptides))

@pytest.fixture
def peptide_hierarchy_input(test_data):
    root_peptide_data = test_data['peptides'][0]
    root_sequence = [BuildingBlock(identifier=bb_id, properties=test_data['building_blocks'][bb_id]) for bb_id in root_peptide_data['sequence']]
    root_chromatogram = Chromatogram(times=root_peptide_data['chromatogram']['times'], intensities=root_peptide_data['chromatogram']['intensities'])
    root_peptide = Peptide(sequence=root_sequence, properties=root_peptide_data['properties'])
    root_peptide.add_encoding(PeptideEncoding(blocks=root_sequence, chromatogram=root_chromatogram))
    hierarchy = PeptideHierarchy(root=root_peptide)
    return PeptideHierarchyInput(hierarchy=hierarchy)

def test_single_peptide_pipeline(single_peptide_input, caplog):
    pipeline = TPipe()
    with caplog.at_level(logging.INFO):
        result = pipeline.run(single_peptide_input)
    assert result is not None
    assert isinstance(result, SinglePeptideInput)
    assert "Handling input for peptide" in caplog.text
    assert "Analyzing chromatogram for peptide" in caplog.text
    assert "Detecting peaks for peptide" in caplog.text
    assert "Analyzing peaks for peptide" in caplog.text
    assert "Selecting peaks for peptide" in caplog.text
    assert "Outputting results for peptide" in caplog.text
    logger.info("Single peptide pipeline test passed.")

def test_peptide_set_pipeline(peptide_set_input, caplog):
    pipeline = TPipe()
    with caplog.at_level(logging.INFO):
        result = pipeline.run(peptide_set_input)
    assert result is not None
    assert isinstance(result, PeptideSetInput)
    assert "Handling input for peptide set" in caplog.text
    assert "Analyzing chromatogram for peptide set" in caplog.text
    assert "Detecting peaks for peptide set" in caplog.text
    assert "Analyzing peaks for peptide set" in caplog.text
    assert "Selecting peaks for peptide set" in caplog.text
    assert "Outputting results for peptide set" in caplog.text
    logger.info("Peptide set pipeline test passed.")

def test_peptide_hierarchy_pipeline(peptide_hierarchy_input, caplog):
    pipeline = TPipe()
    with caplog.at_level(logging.INFO):
        result = pipeline.run(peptide_hierarchy_input)
    assert result is not None
    assert isinstance(result, PeptideHierarchyInput)
    assert "Handling input for peptide hierarchy" in caplog.text
    assert "Analyzing chromatogram for peptide hierarchy" in caplog.text
    assert "Detecting peaks for peptide hierarchy" in caplog.text
    assert "Analyzing peaks for peptide hierarchy" in caplog.text
    assert "Selecting peaks for peptide hierarchy" in caplog.text
    assert "Outputting results for peptide hierarchy" in caplog.text
    logger.info("Peptide hierarchy pipeline test passed.")
