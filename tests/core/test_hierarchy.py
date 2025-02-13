# tests/core/test_hierarchy.py
"""Tests for the PeptideHierarchy class."""

# Standard library imports
import os
from pathlib import Path
from typing import Dict, List, Set

import pytest
import yaml

# Local application imports
from src.lcseq.core.building_block import BuildingBlock
from src.lcseq.core.hierarchy import PeptideHierarchy, PeptideHierarchyNode
from src.lcseq.core.peptide import Peptide
from src.lcseq.core.synthesis_status import SynthesisStatus
from src.lcseq.pipeline.components.visualizers.hierarchy_visualizer import (
    HierarchyVisualizer,
    HierarchyVisualizerConfig,
)
from src.lcseq.pipeline.input_types import PeptideHierarchyInput


@pytest.fixture
def simple_peptides() -> List[Peptide]:
    """Create simple test peptides for relationship testing.

    Returns:
        List of test peptides with known relationships.
    """
    blocks = [
        BuildingBlock("BB1", properties={"name": "Block1"}),
        BuildingBlock("BB2", properties={"name": "Block2"}),
        BuildingBlock("BB3", properties={"name": "Block3"}),
    ]

    return [
        Peptide([blocks[0]]),  # Single block
        Peptide([blocks[0], blocks[1]]),  # Two blocks
        Peptide([blocks[0], blocks[1], blocks[2]]),  # Three blocks
    ]


def test_hierarchy_initialization() -> None:
    """Test initialization of PeptideHierarchy."""
    hierarchy = PeptideHierarchy()
    assert isinstance(hierarchy.nodes, dict)
    assert isinstance(hierarchy.layers, dict)
    assert set(hierarchy.layers.keys()) == {1, 2, 3}
    assert all(isinstance(layer, set) for layer in hierarchy.layers.values())


def test_add_node(simple_peptides: List[Peptide]) -> None:
    """Test adding nodes to hierarchy.

    Args:
        simple_peptides: List of simple test peptides.
    """
    hierarchy = PeptideHierarchy()

    # Add peptides to hierarchy
    for peptide in simple_peptides:
        node = hierarchy.add_node(peptide)
        assert node.peptide == peptide
        assert node.layer == len(peptide.sequence)
        assert node in hierarchy.layers[node.layer]
        assert peptide.sequence_str in hierarchy.nodes


def test_truncation_relationships(simple_peptides: List[Peptide]) -> None:
    """Test establishment of truncation relationships.

    Args:
        simple_peptides: List of simple test peptides.
    """
    hierarchy = PeptideHierarchy()

    # Add all peptides
    nodes = [hierarchy.add_node(peptide) for peptide in simple_peptides]

    # Check relationships
    # Three-block peptide should have both two-block and one-block as truncations
    assert (
        nodes[0] in nodes[2].truncation_edges
    )  # One-block is truncation of three-block
    assert (
        nodes[1] in nodes[2].truncation_edges
    )  # Two-block is truncation of three-block

    # Two-block peptide should have one-block as truncation
    assert nodes[0] in nodes[1].truncation_edges  # One-block is truncation of two-block

    # One-block peptide should have no truncations
    assert not nodes[0].truncation_edges


def test_extension_relationships(simple_peptides: List[Peptide]) -> None:
    """Test establishment of extension relationships.

    Args:
        simple_peptides: List of simple test peptides.
    """
    hierarchy = PeptideHierarchy()

    # Add all peptides
    nodes = [hierarchy.add_node(peptide) for peptide in simple_peptides]

    # Check relationships
    # One-block peptide should have both two-block and three-block as extensions
    assert nodes[1] in nodes[0].extension_edges  # Two-block is extension of one-block
    assert nodes[2] in nodes[0].extension_edges  # Three-block is extension of one-block

    # Two-block peptide should have three-block as extension
    assert nodes[2] in nodes[1].extension_edges  # Three-block is extension of two-block

    # Three-block peptide should have no extensions
    assert not nodes[2].extension_edges


def test_node_validation(simple_peptides: List[Peptide]) -> None:
    """Test retention time validation.

    Args:
        simple_peptides: List of simple test peptides.
    """
    hierarchy = PeptideHierarchy()

    # Add peptides with retention times
    for i, peptide in enumerate(simple_peptides):
        peptide.properties["retention_time"] = float(i + 1)  # 1.0, 2.0, 3.0

    nodes = [hierarchy.add_node(peptide) for peptide in simple_peptides]

    # Set retention times on nodes
    for node in nodes:
        node.retention_time = node.peptide.properties["retention_time"]

    # Check validation
    assert nodes[0].validate_retention_times()  # Single block always valid
    assert nodes[1].validate_retention_times()  # Two-block > one-block
    assert nodes[2].validate_retention_times()  # Three-block > two-block and one-block


def test_synthesis_status_update(simple_peptides: List[Peptide]) -> None:
    """Test synthesis status updates.

    Args:
        simple_peptides: List of simple test peptides.
    """
    hierarchy = PeptideHierarchy()

    # Add peptides with retention times
    nodes = []
    for i, peptide in enumerate(simple_peptides):
        node = hierarchy.add_node(peptide)
        node.retention_time = float(i + 1)  # 1.0, 2.0, 3.0
        nodes.append(node)

    # Update synthesis status
    for node in nodes:
        node.update_synthesis_status()

    # Check status
    assert all(node.synthesis_status == SynthesisStatus.SUCCESS for node in nodes)

    # Make one fail by setting invalid retention time
    nodes[1].retention_time = 0.5  # Less than its truncation
    nodes[1].update_synthesis_status()
    assert nodes[1].synthesis_status == SynthesisStatus.FAILURE

    # Update three-block status - should fail due to failed truncation
    nodes[2].update_synthesis_status()
    assert nodes[2].synthesis_status == SynthesisStatus.FAILURE


def test_duplicate_node_addition(simple_peptides: List[Peptide]) -> None:
    """Test adding duplicate nodes.

    Args:
        simple_peptides: List of simple test peptides.
    """
    hierarchy = PeptideHierarchy()

    # Add same peptide twice
    node1 = hierarchy.add_node(simple_peptides[0])
    node2 = hierarchy.add_node(simple_peptides[0])

    # Should return same node
    assert node1 is node2
    assert len(hierarchy.nodes) == 1
    assert len(hierarchy.layers[1]) == 1


def test_hierarchy_visualization(
    simple_peptides: List[Peptide], tmp_path: Path
) -> None:
    """Test visualization of the hierarchy.

    Args:
        simple_peptides: List of simple test peptides.
        tmp_path: Temporary directory path.
    """
    # Create hierarchy
    hierarchy = PeptideHierarchy()
    for peptide in simple_peptides:
        node = hierarchy.add_node(peptide)
        # Add retention times for visualization
        node.retention_time = float(len(peptide.sequence))

    # Set up visualizer with test output directory
    output_dir = str(tmp_path / "hierarchy_plots")
    config = HierarchyVisualizerConfig(
        save_plots=True,
        output_dir=output_dir,
    )
    visualizer = HierarchyVisualizer(config=config, plot_results=True)

    # Create input and process
    input_data = PeptideHierarchyInput(hierarchy=hierarchy)
    visualizer.process_hierarchy(input_data)

    # Check that plot was created
    expected_plot = os.path.join(output_dir, "peptide_hierarchy.png")
    assert os.path.exists(expected_plot), f"Plot not found at {expected_plot}"
    assert os.path.getsize(expected_plot) > 0, "Plot file is empty"
