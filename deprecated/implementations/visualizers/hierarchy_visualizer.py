# src/chromatographicpeakpicking/implementations/visualizers/hierarchy_visualizer.py
"""
Module: hierarchy_visualizer

This module implements the HierarchyVisualizer class which provides visualization
capabilities for Hierarchy instances using NetworkX with hierarchical layout.
"""

from typing import Any, Dict, Optional, List, Set, Tuple
from collections import defaultdict
import math
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
from ...core.protocols.visualizable import Visualizable
from ...core.prototypes.hierarchy import Hierarchy
from ...core.prototypes.peptide import Peptide

class HierarchyVisualizer(Visualizable):
    """Visualizer for Hierarchy instances using NetworkX with hierarchical layout."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the HierarchyVisualizer."""
        self._current_graph = None
        self._current_figure = None

        # Default configuration
        default_config = {
            'level_colors': {
                3: '#2874a6',  # Dark blue
                2: '#5499c7',  # Medium blue
                1: '#85c1e9',  # Light blue
                0: '#d4e6f1'   # Very light blue
            },
            'node_size': 3000,
            'edge_color': '#2c3e50',
            'font_size': 10,
            'figure_size': (12, 8),
            'vertical_spacing': 1.0,
            'horizontal_spacing': 0.8
        }

        # Merge custom config with defaults
        if config is not None:
            default_config.update(config)

        self.config = default_config

    def _group_similar_nodes(self, nodes: List[str]) -> List[List[str]]:
        """
        Group nodes that represent the same truncation pattern.
        Nodes are considered equivalent if they have the same non-null building blocks
        in the same relative order, regardless of AgxNull positions.
        """
        def get_normalized_key(node: str) -> str:
            # Split into components
            components = node.split('-')
            # Get only non-null components while preserving their relative order
            real_components = [c for c in components if c != 'AgxNull']
            # Count AgxNulls to ensure we group nodes of the same level
            agx_count = components.count('AgxNull')
            # Create a key that captures the ordered real components and level
            return f"{'-'.join(real_components)}_{agx_count}"

        groups = {}
        for node in nodes:
            key = get_normalized_key(node)
            if key not in groups:
                groups[key] = []
            groups[key].append(node)

        return list(groups.values())

    def _create_networkx_graph(self, hierarchy: Hierarchy) -> nx.DiGraph:
        """Create a NetworkX graph from the hierarchy."""
        G = nx.DiGraph()

        # Get peptides organized by level
        levels = defaultdict(set)
        for level in range(4):  # 0 to 3
            peptides = hierarchy.get_peptides_by_level(level)
            if peptides:  # Only add non-empty levels
                levels[level] = peptides

        # Add nodes with level information
        for level, peptides in levels.items():
            for peptide in peptides:
                sequence_str = "-".join(bb.name for bb in reversed(peptide.sequence))
                G.add_node(
                    sequence_str,
                    label=sequence_str,
                    level=level,
                    color=self.config['level_colors'][level],
                    peptide=peptide
                )

        # Add edges based on hierarchy relationships
        for peptide, descendants in hierarchy.descendants.items():
            parent_seq = "-".join(bb.name for bb in reversed(peptide.sequence))
            for child in descendants:
                child_seq = "-".join(bb.name for bb in reversed(child.sequence))
                if parent_seq in G and child_seq in G:
                    G.add_edge(parent_seq, child_seq)

        return G

    def _hierarchical_layout(self, G: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
        """Create a hierarchical layout for the graph with permutation grouping."""
        if not G.nodes:
            return {}

        # Group nodes by level
        nodes_by_level = defaultdict(list)
        for node, data in G.nodes(data=True):
            level = data.get('level', 0)
            nodes_by_level[level].append(node)

        # Calculate positions
        pos = {}
        max_level = max(nodes_by_level.keys())

        for level in sorted(nodes_by_level.keys(), reverse=True):
            nodes = nodes_by_level[level]

            # Group similar nodes
            node_groups = self._group_similar_nodes(nodes)
            n_groups = len(node_groups)

            # Calculate y-coordinate (vertical position)
            base_y = self.config['vertical_spacing'] * (max_level - level)

            # Position each group
            total_width = (n_groups - 1) * self.config['horizontal_spacing']
            start_x = -total_width / 2

            for group_idx, group in enumerate(node_groups):
                # Calculate base position for the group
                group_x = start_x + (group_idx * self.config['horizontal_spacing'])

                # For each group, arrange nodes in a tight triangular pattern
                if len(group) == 1:
                    pos[group[0]] = (group_x, base_y)
                else:
                    # Calculate triangle dimensions
                    triangle_height = 0.3 * self.config['vertical_spacing']
                    triangle_width = 0.3 * self.config['horizontal_spacing']

                    if len(group) == 2:
                        # For 2 nodes, stack vertically
                        pos[group[0]] = (group_x, base_y + triangle_height/2)
                        pos[group[1]] = (group_x, base_y - triangle_height/2)
                    else:
                        # For 3 nodes, arrange in a triangle
                        pos[group[0]] = (group_x, base_y + triangle_height)  # Top
                        pos[group[1]] = (group_x - triangle_width/2, base_y - triangle_height/2)  # Bottom left
                        pos[group[2]] = (group_x + triangle_width/2, base_y - triangle_height/2)  # Bottom right

        return pos

    def visualize(self, data: Any) -> nx.DiGraph:
        """Create NetworkX visualization of a hierarchy."""
        if not isinstance(data, Hierarchy):
            raise TypeError("Data must be a Hierarchy instance")

        # Create graph and compute layout
        G = self._create_networkx_graph(data)
        pos = self._hierarchical_layout(G)

        # Create figure
        plt.figure(figsize=self.config['figure_size'])

        if G.nodes:
            # Draw nodes
            nx.draw_networkx_nodes(
                G, pos,
                node_color=[data['color'] for _, data in G.nodes(data=True)],
                node_size=self.config['node_size']
            )

            # Draw edges with improved visibility
            if G.edges:
                nx.draw_networkx_edges(
                    G, pos,
                    edge_color=self.config['edge_color'],
                    arrows=True,
                    arrowsize=20,
                    arrowstyle='->'
                )

            # Draw labels
            nx.draw_networkx_labels(
                G, pos,
                labels=nx.get_node_attributes(G, 'label'),
                font_size=self.config['font_size']
            )

        plt.title("Peptide Hierarchy")
        plt.axis('off')
        plt.show()

        self._current_graph = G
        self._current_figure = plt.gcf()

        return G

    def save(self, path: Path) -> None:
        """Save current visualization to file."""
        if self._current_figure is None:
            raise ValueError("No visualization has been generated. Call visualize() first.")

        path.parent.mkdir(parents=True, exist_ok=True)
        self._current_figure.savefig(path, bbox_inches='tight', dpi=300)
        plt.close(self._current_figure)

    def display(self) -> None:
        """Display the current visualization."""
        if self._current_figure is None:
            raise ValueError("No visualization has been generated. Call visualize() first.")
        plt.show()
