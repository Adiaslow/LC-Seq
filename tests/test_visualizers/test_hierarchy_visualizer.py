# tests/test_implementations/test_visualizers/test_hierarchy_visualizer.py

import pytest
import networkx as nx
from pathlib import Path
import matplotlib.pyplot as plt
from src.chromatographicpeakpicking.core.prototypes.hierarchy import Hierarchy
from src.chromatographicpeakpicking.core.prototypes.peptide import Peptide
from src.chromatographicpeakpicking.core.prototypes.building_block import BuildingBlock
from src.chromatographicpeakpicking.core.types.config import GlobalConfig
from src.chromatographicpeakpicking.implementations.visualizers.hierarchy_visualizer import HierarchyVisualizer

@pytest.fixture
def test_hierarchy():
    """Create a test hierarchy with a simple peptide structure."""
    # Create configuration with AgxNull as null building block
    config = GlobalConfig(null_building_block=BuildingBlock("AgxNull"))
    hierarchy = Hierarchy(global_config=config)

    # Create test peptide with three building blocks
    sequence = [BuildingBlock("Leu"), BuildingBlock("Phe"), BuildingBlock("Val")]
    peptide = Peptide(sequence=sequence)

    # Add to hierarchy - this will automatically generate descendants
    hierarchy.add_peptide(peptide)

    # Generate all descendants
    descendants = hierarchy.generate_all_descendants(peptide)
    for desc in descendants:
        hierarchy.add_peptide(desc)

    return hierarchy

@pytest.fixture
def visualizer():
    """Create a HierarchyVisualizer instance."""
    return HierarchyVisualizer()

def test_graph_creation(visualizer, test_hierarchy):
    """Test that NetworkX graph is created correctly."""
    G = visualizer.visualize(test_hierarchy)

    # Basic graph validation
    assert isinstance(G, nx.DiGraph)
    assert len(G.nodes) > 0

    # Verify we have nodes at different levels
    levels = set(data['level'] for _, data in G.nodes(data=True))
    assert len(levels) > 1  # Should have multiple levels

    # Verify edges exist (should have parent-child relationships)
    assert len(G.edges) > 0

    # Check specific node attributes
    for node, attrs in G.nodes(data=True):
        assert 'label' in attrs
        assert 'level' in attrs
        assert 'color' in attrs
        assert isinstance(attrs['level'], int)
        assert 0 <= attrs['level'] <= 3

def test_node_levels(visualizer, test_hierarchy):
    """Test that nodes are assigned to correct levels."""
    G = visualizer.visualize(test_hierarchy)

    # Count nodes at each level
    level_counts = {}
    for _, data in G.nodes(data=True):
        level = data['level']
        level_counts[level] = level_counts.get(level, 0) + 1

    # Level 3: 1 node (original peptide)
    assert level_counts[3] == 1, "Should have 1 node at level 3 (original peptide)"

    # Level 2: 9 nodes (one null substitution, all possible positions and permutations)
    assert level_counts[2] == 9, "Should have 9 nodes at level 2 (one AgxNull substitution)"

    # Level 1: 9 nodes (two null substitutions, all possible positions and permutations)
    assert level_counts[1] == 9, "Should have 9 nodes at level 1 (two AgxNull substitutions)"

    # Level 0: 1 node (all null)
    assert level_counts[0] == 1, "Should have 1 node at level 0 (all AgxNull)"

    # Total should be 20 nodes
    assert sum(level_counts.values()) == 20, "Should have 20 total nodes"

    # Verify specific sequences are present
    node_labels = nx.get_node_attributes(G, 'label')
    expected_sequences = {
        # Level 3
        "Leu-Phe-Val",
        # Level 2 (sample of the 9)
        "Leu-Phe-AgxNull",
        "Leu-AgxNull-Phe",
        "AgxNull-Leu-Phe",
        # Level 1 (sample of the 9)
        "Leu-AgxNull-AgxNull",
        "AgxNull-Leu-AgxNull",
        "AgxNull-AgxNull-Leu",
        # Level 0
        "AgxNull-AgxNull-AgxNull"
    }

    # Check that at least these sequences exist
    actual_sequences = set(node_labels.values())
    assert expected_sequences.issubset(actual_sequences), \
           f"Missing expected sequences. Should have {expected_sequences}"

def test_edge_structure(visualizer, test_hierarchy):
    """Test that edges correctly represent parent-child relationships."""
    G = visualizer.visualize(test_hierarchy)

    # Each non-zero level node should have edges to lower levels
    for node, data in G.nodes(data=True):
        level = data['level']
        if level > 0:
            # Should have at least one outgoing edge
            assert len(list(G.edges(node))) > 0

def test_custom_configuration(visualizer, test_hierarchy):
    """Test visualization with custom configuration."""
    custom_config = {
        'level_colors': {
            3: '#ff0000',
            2: '#ff5555',
            1: '#ffaaaa',
            0: '#ffe0e0'
        },
        'node_size': 4000,
        'edge_color': '#000000',
        'font_size': 12,
        'figure_size': (15, 10)
    }

    visualizer = HierarchyVisualizer(config=custom_config)
    G = visualizer.visualize(test_hierarchy)

    # Verify custom colors are used
    colors = set(data['color'] for _, data in G.nodes(data=True))
    assert '#ff0000' in colors

def test_save_visualization(visualizer, test_hierarchy, tmp_path):
    """Test saving visualization to file."""
    visualizer.visualize(test_hierarchy)
    save_path = tmp_path / "hierarchy.png"
    visualizer.save(save_path)
    assert save_path.exists()
    assert save_path.stat().st_size > 0

def test_invalid_data(visualizer):
    """Test handling of invalid data."""
    with pytest.raises(TypeError):
        visualizer.visualize("not a hierarchy")

def test_save_without_visualization(visualizer, tmp_path):
    """Test attempting to save without creating visualization first."""
    save_path = tmp_path / "hierarchy.png"
    with pytest.raises(ValueError):
        visualizer.save(save_path)
