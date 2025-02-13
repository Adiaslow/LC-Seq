# tests/pipeline/test_hierarchical.py
"""
This module contains the tests for the hierarchical pipeline.
"""

# Standard library imports
import os
from pathlib import Path
from typing import Generator, List

import pytest
import yaml
import numpy as np

# Local application imports
from src.lcseq.pipeline.input_types import ProcessableInput, PeptideHierarchyInput
from src.lcseq.core.hierarchy import PeptideHierarchy
from src.lcseq.pipelines.hierarchical import HierarchicalPipe
from src.lcseq.core.building_block import BuildingBlock
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.chromatogram import Chromatogram


@pytest.fixture
def test_data_path() -> str:
    """Get path to test data file.

    Returns:
        Path to test data file.
    """
    return os.path.join("tests", "data", "prepared_data.yaml")


@pytest.fixture
def output_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create temporary output directory.

    Args:
        tmp_path: Pytest temporary path fixture.

    Yields:
        Path to temporary output directory.
    """
    output_dir: Path = tmp_path / "output"
    output_dir.mkdir()
    yield output_dir


def create_hierarchy_from_data(data: dict) -> PeptideHierarchy:
    """Create a PeptideHierarchy from dictionary data.

    Args:
        data: Dictionary containing peptide data and building block definitions.

    Returns:
        PeptideHierarchy containing the peptides.
    """
    hierarchy = PeptideHierarchy()

    if not data or "peptides" not in data or "building_blocks" not in data:
        return hierarchy

    # Create building blocks dictionary for lookup
    building_blocks: dict = data["building_blocks"]

    # First create all peptides to establish nodes
    peptides: List[Peptide] = []
    for peptide_data in data["peptides"]:
        # Get sequence and look up building block definitions
        sequence: List[BuildingBlock] = []
        for block_name in peptide_data["sequence"]:
            # Find the building block definition in the correct BB group
            for bb_group in building_blocks.values():
                if block_name in bb_group:
                    block_def = bb_group[block_name]
                    properties = {
                        "smiles": block_def["smiles"],
                        "stereochem": block_def["stereochem"],
                    }
                    block = BuildingBlock(identifier=block_name, properties=properties)
                    sequence.append(block)
                    break

        if sequence:  # Only create peptide if we found all building blocks
            peptide: Peptide = Peptide(sequence=sequence)

            # Add chromatogram data if available
            if "chromatogram" in peptide_data:
                chromatogram_data = peptide_data["chromatogram"]
                chromatogram = Chromatogram(
                    times=np.array(chromatogram_data["times"]),
                    intensities=np.array(chromatogram_data["intensities"]),
                )
                encoding = PeptideEncoding(blocks=sequence, chromatogram=chromatogram)
                peptide.add_encoding(encoding)

            peptides.append(peptide)

    # Sort peptides by length (longest first)
    sorted_peptides = sorted(peptides, key=lambda p: len(p.sequence), reverse=True)

    # Add all peptides to hierarchy
    for peptide in sorted_peptides:
        hierarchy.add_node(peptide)

    return hierarchy


def test_hierarchical_pipeline_no_plots(test_data_path: str, output_dir: Path) -> None:
    # Clean up both plot directories before test
    for plot_dir in ["hierarchy_plots", "chromatogram_plots"]:
        if os.path.exists(plot_dir):
            for file in os.listdir(plot_dir):
                os.remove(os.path.join(plot_dir, file))
            os.rmdir(plot_dir)

    # Initialize pipeline with visualization disabled
    pipeline = HierarchicalPipe(
        input_file_path=test_data_path,
        plot_chromatograms=False,
    )

    # Process the data
    with open(test_data_path, "r") as f:
        raw_data = yaml.safe_load(f)
    hierarchy = create_hierarchy_from_data(raw_data)
    input_data = PeptideHierarchyInput(hierarchy=hierarchy)
    result = pipeline.run(input_data)

    # Verify plots were not created
    assert not os.path.exists(
        "hierarchy_plots"
    ), "Hierarchy plots created when disabled"
    assert not os.path.exists(
        "chromatogram_plots"
    ), "Chromatogram plots created when disabled"


def test_hierarchical_pipeline(test_data_path: str, output_dir: Path) -> None:
    """Test the hierarchical pipeline end-to-end.

    Args:
        test_data_path: Path to test data file.
        output_dir: Path to output directory.
    """
    # Initialize pipeline with visualization enabled
    pipeline = HierarchicalPipe(
        input_file_path=test_data_path,
        plot_chromatograms=True,
    )

    # Process the data
    with open(test_data_path, "r") as f:
        raw_data = yaml.safe_load(f)
    hierarchy = create_hierarchy_from_data(raw_data)

    # Test direct visualization
    hierarchy_viz_path = output_dir / "direct_hierarchy_viz.png"
    hierarchy.visualize_hierarchy()  # This will save to the default location

    # Verify direct visualization was created
    assert os.path.exists(
        "hierarchy_plots/peptide_hierarchy.png"
    ), "Direct hierarchy visualization not created"
    assert os.path.exists(
        "hierarchy_plots/peptide_hierarchy.svg"
    ), "Direct hierarchy SVG not created"

    # Run the pipeline
    input_data = PeptideHierarchyInput(hierarchy=hierarchy)
    result = pipeline.run(input_data)

    # Verify pipeline output files exist
    hierarchy_plot = os.path.join("hierarchy_plots", "peptide_hierarchy.png")
    assert os.path.exists(hierarchy_plot), "Hierarchy plot not created"
    assert os.path.getsize(hierarchy_plot) > 0, "Hierarchy plot is empty"

    # Check chromatogram plots
    chromatogram_plots = os.listdir("chromatogram_plots")
    assert len(chromatogram_plots) > 0, "No chromatogram plots created"

    # Verify expected number of peptides were processed
    assert len(hierarchy.peptides) > 0, "No peptides in hierarchy"


def test_hierarchical_pipeline_invalid_input() -> None:
    """Test the hierarchical pipeline with invalid input."""
    with pytest.raises(FileNotFoundError):
        HierarchicalPipe(input_file_path="nonexistent.yaml")


def test_hierarchical_pipeline_empty_input(tmp_path: Path) -> None:
    """Test the hierarchical pipeline with empty input.

    Args:
        tmp_path: Pytest temporary path fixture.
    """
    # Create empty YAML file
    empty_file: Path = tmp_path / "empty.yaml"
    empty_file.write_text("{}")

    pipeline = HierarchicalPipe(input_file_path=str(empty_file))
    with pytest.warns(UserWarning, match="No peptides found in input data"):
        with open(empty_file, "r") as f:
            raw_data = yaml.safe_load(f)
        hierarchy = create_hierarchy_from_data(raw_data)
        input_data = PeptideHierarchyInput(hierarchy=hierarchy)
        result = pipeline.run(input_data)
