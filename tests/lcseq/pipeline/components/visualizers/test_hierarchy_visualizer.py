"""Tests for the HierarchyVisualizer component."""

# Standard library imports
import os
from pathlib import Path
from typing import Generator, Set

import pytest
from matplotlib.pyplot import close

# Local application imports
from src.lcseq.core.building_block import BuildingBlock
from src.lcseq.core.hierarchy import PeptideHierarchy, PeptideHierarchyNode
from src.lcseq.core.peptide import Peptide
from src.lcseq.core.synthesis_status import SynthesisStatus
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    PeptideSetInput,
    SinglePeptideInput,
)
from src.lcseq.pipeline.components.visualizers.hierarchy_visualizer import (
    HierarchyVisualizer,
    HierarchyVisualizerConfig,
)


@pytest.fixture
def test_hierarchy() -> Generator[PeptideHierarchy, None, None]:
    """Create a test peptide hierarchy.

    Returns:
        A simple peptide hierarchy for testing.
    """
    hierarchy = PeptideHierarchy()

    # Create some building blocks
    block1 = BuildingBlock("A1", properties={"name": "Block1"})
    block2 = BuildingBlock("A2", properties={"name": "Block2"})
    block3 = BuildingBlock("A3", properties={"name": "Block3"})

    # Create peptides of different lengths
    peptide1 = Peptide([block1])
    peptide2 = Peptide([block1, block2])
    peptide3 = Peptide([block1, block2, block3])

    # Add retention times
    peptide1.properties["retention_time"] = 1.0
    peptide2.properties["retention_time"] = 2.0
    peptide3.properties["retention_time"] = 3.0

    # Add to hierarchy
    node1: PeptideHierarchyNode = hierarchy.add_node(peptide1)
    node2: PeptideHierarchyNode = hierarchy.add_node(peptide2)
    node3: PeptideHierarchyNode = hierarchy.add_node(peptide3)

    # Set synthesis status
    node1.synthesis_status = SynthesisStatus.SUCCESS
    node2.synthesis_status = SynthesisStatus.FAILURE
    node3.synthesis_status = SynthesisStatus.UNKNOWN

    yield hierarchy


@pytest.fixture
def test_output_dir(tmp_path: Path) -> Generator[str, None, None]:
    """Create a temporary output directory.

    Returns:
        Path to temporary output directory.
    """
    output_dir = str(tmp_path / "test_hierarchy_plots")
    yield output_dir


@pytest.fixture
def visualizer(test_output_dir: str) -> Generator[HierarchyVisualizer, None, None]:
    """Create a HierarchyVisualizer instance.

    Args:
        test_output_dir: Path to test output directory.

    Returns:
        Configured HierarchyVisualizer instance.
    """
    config = HierarchyVisualizerConfig(
        save_plots=True,
        output_dir=test_output_dir,
    )
    visualizer = HierarchyVisualizer(config=config, plot_results=True)
    yield visualizer
    close("all")  # Clean up any open matplotlib figures


def test_process_hierarchy(
    visualizer: HierarchyVisualizer,
    test_hierarchy: PeptideHierarchy,
    test_output_dir: str,
) -> None:
    """Test processing a hierarchy input.

    Args:
        visualizer: The visualizer instance.
        test_hierarchy: Test hierarchy fixture.
        test_output_dir: Test output directory.
    """
    # Create input data
    input_data = PeptideHierarchyInput(hierarchy=test_hierarchy)

    # Process the hierarchy
    result: PeptideHierarchyInput = visualizer.process_hierarchy(input_data)

    # Check that input data is returned unchanged
    assert result == input_data

    # Check that plot file was created
    expected_file: str = os.path.join(test_output_dir, "peptide_hierarchy.png")
    assert os.path.exists(expected_file)


def test_process_hierarchy_no_plot(
    test_hierarchy: PeptideHierarchy,
    test_output_dir: str,
) -> None:
    """Test processing without plotting.

    Args:
        test_hierarchy: Test hierarchy fixture.
        test_output_dir: Test output directory.
    """
    # Create visualizer with plotting disabled
    config = HierarchyVisualizerConfig(
        save_plots=True,
        output_dir=test_output_dir,
    )
    visualizer = HierarchyVisualizer(config=config, plot_results=False)

    # Create input data
    input_data = PeptideHierarchyInput(hierarchy=test_hierarchy)

    # Process the hierarchy
    result: PeptideHierarchyInput = visualizer.process_hierarchy(input_data)

    # Check that input data is returned unchanged
    assert result == input_data

    # Check that no plot file was created
    expected_file: str = os.path.join(test_output_dir, "peptide_hierarchy.png")
    assert not os.path.exists(expected_file)


def test_process_single_peptide(visualizer: HierarchyVisualizer) -> None:
    """Test processing a single peptide (should warn and return unchanged).

    Args:
        visualizer: The visualizer instance.
    """
    # Create a test peptide
    peptide = Peptide([BuildingBlock("A1", properties={"name": "Block1"})])
    input_data = SinglePeptideInput(peptide=peptide)

    # Process the peptide
    with pytest.warns(UserWarning, match="Single peptide visualization not supported"):
        result: SinglePeptideInput = visualizer.process_peptide(input_data)

    # Check that input data is returned unchanged
    assert result == input_data


def test_process_peptide_set(visualizer: HierarchyVisualizer) -> None:
    """Test processing a peptide set (should warn and return unchanged).

    Args:
        visualizer: The visualizer instance.
    """
    # Create a test peptide set
    peptides: Set[Peptide] = {
        Peptide([BuildingBlock("A1", properties={"name": "Block1"})])
    }
    input_data: PeptideSetInput = PeptideSetInput(peptides=peptides)

    # Process the peptide set
    with pytest.warns(UserWarning, match="Peptide set visualization not supported"):
        result: PeptideSetInput = visualizer.process_peptide_set(input_data)

    # Check that input data is returned unchanged
    assert result == input_data


def test_visualizer_config_defaults() -> None:
    """Test default configuration values."""
    config = HierarchyVisualizerConfig()

    assert config.figure_size == (12, 8)
    assert config.dpi == 100
    assert config.node_size == 1000
    assert config.font_size == 8
    assert config.save_plots is True
    assert config.output_dir == "hierarchy_plots"
