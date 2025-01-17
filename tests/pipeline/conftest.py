# tests/pipeline/conftest.py
"""Shared fixtures for pipeline tests."""
import pytest
import yaml
import logging
import numpy as np
from pathlib import Path
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.hierarchy import PeptideHierarchy
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput

@pytest.fixture
def test_data():
    """Load test data from YAML file."""
    data_path = Path("tests/data/prepared_data.yaml")
    with open(data_path, "r") as f:
        return yaml.safe_load(f)

@pytest.fixture
def pipeline_building_blocks(test_data):
    """Create BuildingBlock objects from test data."""
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
def pipeline_single_input(test_data, pipeline_building_blocks):
    """Create SinglePeptideInput from test data."""
    peptide_data = test_data["peptides"][0]
    sequence = [pipeline_building_blocks[bb_id] for bb_id in peptide_data["sequence"]]
    chromatogram = Chromatogram(
        times=np.array(peptide_data["chromatogram"]["times"], dtype=float),
        intensities=np.array(peptide_data["chromatogram"]["intensities"], dtype=float)
    )

    peptide = Peptide(
        sequence=sequence,
        properties={"identifier": peptide_data["identifier"], **peptide_data.get("properties", {})}
    )
    peptide.add_encoding(PeptideEncoding(blocks=sequence, chromatogram=chromatogram))
    return SinglePeptideInput(peptide)

@pytest.fixture
def pipeline_set_input(test_data, pipeline_building_blocks):
    """Create PeptideSetInput from test data."""
    peptides = []
    for peptide_data in test_data["peptides"]:
        sequence = [pipeline_building_blocks[bb_id] for bb_id in peptide_data["sequence"]]
        chromatogram = Chromatogram(
            times=np.array(peptide_data["chromatogram"]["times"], dtype=float),
            intensities=np.array(peptide_data["chromatogram"]["intensities"], dtype=float)
        )
        peptide = Peptide(
            sequence=sequence,
            properties={"identifier": peptide_data["identifier"], **peptide_data.get("properties", {})}
        )
        peptide.add_encoding(PeptideEncoding(blocks=sequence, chromatogram=chromatogram))
        peptides.append(peptide)
    return PeptideSetInput(set(peptides))

@pytest.fixture
def pipeline_hierarchy_input(pipeline_single_input):
    """Create PeptideHierarchyInput from test data."""
    hierarchy = PeptideHierarchy(root=pipeline_single_input.peptide)
    return PeptideHierarchyInput(hierarchy=hierarchy)
