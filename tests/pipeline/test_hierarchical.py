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
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.pipeline.components.visualizers.hierarchy_visualizer import (
    HierarchyVisualizer,
    HierarchyVisualizerConfig,
)


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
    # First register the null building block
    try:
        BuildingBlockRegistry.clear()  # Clear any existing blocks
    except ValueError:
        pass

    null_block = BuildingBlock(
        identifier="AgxNull", properties={"smiles": "", "stereochem": "none"}
    )
    BuildingBlockRegistry.register(null_block)

    if not data or "peptides" not in data or "building_blocks" not in data:
        hierarchy = PeptideHierarchy()  # Create hierarchy after registering null block
        return hierarchy

    # Register all building blocks from the data
    building_blocks = data["building_blocks"]
    for position_data in building_blocks.values():
        if isinstance(position_data, dict):
            for identifier, properties in position_data.items():
                if isinstance(properties, dict):
                    block = BuildingBlock(
                        identifier=identifier,
                        properties={
                            "smiles": properties.get("smiles", ""),
                            "stereochem": properties.get("stereochem", "none"),
                        },
                    )
                    BuildingBlockRegistry.register(block)

    # Create hierarchy after all blocks are registered
    hierarchy = PeptideHierarchy()

    # Create peptides and organize by depth
    peptides_by_depth: dict[int, List[Peptide]] = {1: [], 2: [], 3: []}

    for peptide_data in data.get("peptides", []):
        # Get sequence and look up building block definitions
        blocks: List[BuildingBlock] = []
        for block_name in peptide_data.get("sequence", []):
            try:
                block = BuildingBlockRegistry.get(block_name)
                blocks.append(block)
            except KeyError:
                continue  # Skip if building block not found

        if blocks:  # Only create peptide if we found all building blocks
            peptide = Peptide(blocks=blocks)

            # Add chromatogram data if available
            if "chromatogram" in peptide_data:
                chromatogram_data = peptide_data["chromatogram"]
                if chromatogram_data.get("times") and chromatogram_data.get(
                    "intensities"
                ):
                    chromatogram = Chromatogram(
                        times=np.array(chromatogram_data["times"]),
                        intensities=np.array(chromatogram_data["intensities"]),
                    )
                    encoding = PeptideEncoding(blocks=blocks, chromatogram=chromatogram)
                    peptide.add_encoding(encoding)

            # Add to appropriate depth group
            depth = len([b for b in blocks if b.identifier != "AgxNull"])
            if depth in peptides_by_depth:
                peptides_by_depth[depth].append(peptide)

    # Add peptides to hierarchy in order of increasing depth
    for depth in [1, 2, 3]:
        for peptide in peptides_by_depth[depth]:
            hierarchy.add_peptide(peptide)

    return hierarchy


def test_hierarchical_pipeline_no_plots(test_data_path: str, output_dir: Path) -> None:
    """Test the hierarchical pipeline with plotting disabled."""
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
    """Test the hierarchical pipeline end-to-end."""
    # Initialize pipeline with visualization enabled
    pipeline = HierarchicalPipe(
        input_file_path=test_data_path,
        plot_chromatograms=True,
    )

    # Process the data
    with open(test_data_path, "r") as f:
        raw_data = yaml.safe_load(f)
    hierarchy = create_hierarchy_from_data(raw_data)

    # Test visualization
    config = HierarchyVisualizerConfig(
        figure_size=(30, 30),
        dpi=300,
        font_size=8,
        save_plots=True,
        output_dir="hierarchy_plots",
    )
    visualizer = HierarchyVisualizer(config=config, plot_results=True)
    visualizer.visualize(hierarchy)

    # Verify visualization was created
    assert os.path.exists(
        "hierarchy_plots/peptide_hierarchy_radial.png"
    ), "Hierarchy visualization not created"
    assert os.path.exists(
        "hierarchy_plots/peptide_hierarchy_radial.svg"
    ), "Hierarchy SVG not created"

    # Run the pipeline
    input_data = PeptideHierarchyInput(hierarchy=hierarchy)
    result = pipeline.run(input_data)

    # Verify pipeline output files exist
    assert os.path.exists(
        "hierarchy_plots/peptide_hierarchy_radial.png"
    ), "Hierarchy plot not created"
    assert (
        os.path.getsize("hierarchy_plots/peptide_hierarchy_radial.png") > 0
    ), "Hierarchy plot is empty"

    # Check chromatogram plots
    chromatogram_plots = os.listdir("chromatogram_plots")
    assert len(chromatogram_plots) > 0, "No chromatogram plots created"

    # Verify expected number of nodes were processed
    assert len(hierarchy.get_nodes_at_depth(1)) > 0, "No depth 1 nodes in hierarchy"
    assert len(hierarchy.get_nodes_at_depth(2)) > 0, "No depth 2 nodes in hierarchy"
    assert len(hierarchy.get_nodes_at_depth(3)) > 0, "No depth 3 nodes in hierarchy"


def test_hierarchical_pipeline_invalid_input() -> None:
    """Test the hierarchical pipeline with invalid input."""
    with pytest.raises(FileNotFoundError):
        HierarchicalPipe(input_file_path="nonexistent.yaml")


def test_hierarchical_pipeline_empty_input(tmp_path: Path) -> None:
    """Test the hierarchical pipeline with empty input."""
    # Create empty YAML file with minimal structure
    empty_file: Path = tmp_path / "empty.yaml"
    empty_file.write_text(
        """
building_blocks: {}
peptides: []
"""
    )

    pipeline = HierarchicalPipe(input_file_path=str(empty_file))
    with pytest.warns(UserWarning, match="No peptides found in input data"):
        with open(empty_file, "r") as f:
            raw_data = yaml.safe_load(f)
        hierarchy = create_hierarchy_from_data(raw_data)
        input_data = PeptideHierarchyInput(hierarchy=hierarchy)
        result = pipeline.run(input_data)
