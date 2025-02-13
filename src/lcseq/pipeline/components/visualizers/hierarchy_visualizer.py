"""
This module provides a pipeline component for visualizing peptide hierarchies as dendrograms/graphs.
"""

import logging
import os
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Set
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from collections import defaultdict

from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    PeptideSetInput,
    SinglePeptideInput,
)


@dataclass
class HierarchyVisualizerConfig:
    """Configuration for hierarchy visualization."""

    figure_size: Tuple[int, int] = (40, 40)
    dpi: int = 300
    node_sizes: dict[int, int] = field(
        default_factory=lambda: {
            0: 1200,  # Root node
            1: 900,  # Single building blocks
            2: 600,  # Two building blocks
            3: 400,  # Three building blocks
        }
    )
    font_size: int = 10
    save_plots: bool = True
    output_dir: str = "hierarchy_plots"
    rt_diff_threshold: float = 10.0


class HierarchyVisualizer(PipelineComponent):
    """Visualizes a peptide hierarchy as a graph with unique node instances per path."""

    def __init__(
        self,
        config: Optional[HierarchyVisualizerConfig] = None,
        plot_results: bool = False,
    ) -> None:
        super().__init__()
        self.config = config or HierarchyVisualizerConfig()
        self.plot_results = plot_results
        # Override save_plots based on plot_results
        self.config.save_plots = self.config.save_plots and plot_results
        self.logger = logging.getLogger(__name__)

    def _create_unique_node_id(
        self, sequence: str, parent_id: Optional[str] = None
    ) -> str:
        """Create a unique node ID that includes its path in the hierarchy."""
        if parent_id is None:
            return sequence
        return f"{parent_id}>{sequence}"

    def _get_sequence_from_id(self, node_id: str) -> str:
        """Extract the actual sequence from a node ID."""
        return node_id.split(">")[-1]

    def _create_hierarchy_graph(self, hierarchy) -> nx.DiGraph:
        """Create a graph with unique node instances for each path in the hierarchy."""
        G = nx.DiGraph()

        # Add root node
        root_id = "ROOT"
        G.add_node(
            root_id,
            layer=0,
            sequence=root_id,
            size=self.config.node_sizes[0],
            label="ROOT",
            retention_time=None,
        )

        # Dictionary to track nodes by layer and parent
        nodes_by_parent = defaultdict(list)
        nodes_by_layer = defaultdict(set)

        # First layer: Add single building blocks
        layer1_nodes = hierarchy.get_layer(1)
        for node in layer1_nodes:
            sequence = node.peptide.sequence_str
            node_id = self._create_unique_node_id(sequence)

            G.add_node(
                node_id,
                layer=1,
                sequence=sequence,
                retention_time=node.retention_time,
                size=self.config.node_sizes[1],
                label=sequence,
            )

            G.add_edge(root_id, node_id)
            nodes_by_parent[root_id].append(node_id)
            nodes_by_layer[1].add(node_id)

        # Second layer: Create unique instances for each parent
        layer2_nodes = hierarchy.get_layer(2)
        for l1_node_id in nodes_by_layer[1]:
            for node in layer2_nodes:
                sequence = node.peptide.sequence_str
                node_id = self._create_unique_node_id(sequence, l1_node_id)

                G.add_node(
                    node_id,
                    layer=2,
                    sequence=sequence,
                    retention_time=node.retention_time,
                    size=self.config.node_sizes[2],
                    label=sequence,
                )

                G.add_edge(l1_node_id, node_id)
                nodes_by_parent[l1_node_id].append(node_id)
                nodes_by_layer[2].add(node_id)

        # Third layer: Create unique instances for each parent
        layer3_nodes = hierarchy.get_layer(3)
        for l2_node_id in nodes_by_layer[2]:
            for node in layer3_nodes:
                sequence = node.peptide.sequence_str
                node_id = self._create_unique_node_id(sequence, l2_node_id)

                G.add_node(
                    node_id,
                    layer=3,
                    sequence=sequence,
                    retention_time=node.retention_time,
                    size=self.config.node_sizes[3],
                    label=sequence,
                )

                G.add_edge(l2_node_id, node_id)
                nodes_by_parent[l2_node_id].append(node_id)
                nodes_by_layer[3].add(node_id)

        return G

    def _create_layout(self, G: nx.DiGraph) -> Dict:
        """Create a hierarchical layout with layers arranged radially."""
        pos = {}
        layers = defaultdict(list)

        # Group nodes by layer
        for node in G.nodes():
            layer = G.nodes[node]["layer"]
            layers[layer].append(node)

        # Calculate the total number of nodes in each layer
        nodes_per_layer = {layer: len(nodes) for layer, nodes in layers.items()}
        max_nodes = max(nodes_per_layer.values())

        # Position nodes in a radial layout
        radius_step = 1.0 / len(layers)
        for layer in sorted(layers.keys()):
            nodes = layers[layer]
            radius = 1.0 - (layer * radius_step)  # Outer layers have smaller radius

            # Calculate angular spacing
            angle_step = 2 * np.pi / len(nodes)

            # Position each node
            for i, node in enumerate(nodes):
                angle = i * angle_step
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                pos[node] = np.array([x, y])

        return pos

    def visualize(self, hierarchy) -> None:
        """Create the hierarchy visualization.

        Only creates visualization if plotting is enabled via self.plot_results.
        Does not create output directory if plotting is disabled.
        """
        if not self.plot_results:
            # Clean up any existing output directory if plotting is disabled
            if os.path.exists(self.config.output_dir):
                try:
                    for file in os.listdir(self.config.output_dir):
                        file_path = os.path.join(self.config.output_dir, file)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    os.rmdir(self.config.output_dir)
                except Exception as e:
                    self.logger.warning(f"Failed to clean up output directory: {e}")
            return

        # Create graph with unique node instances
        G = self._create_hierarchy_graph(hierarchy)

        # Create the layout
        pos = self._create_layout(G)

        # Create figure
        plt.figure(figsize=self.config.figure_size, dpi=self.config.dpi)

        # Draw nodes by layer
        layer_colors = [
            "lightgray",
            "#3498db",
            "#2ecc71",
            "#e74c3c",
        ]  # Colors for each layer
        for layer in range(4):
            nodes_in_layer = [n for n in G.nodes() if G.nodes[n]["layer"] == layer]
            if not nodes_in_layer:
                continue

            # Draw nodes
            nx.draw_networkx_nodes(
                G,
                pos,
                nodelist=nodes_in_layer,
                node_color=layer_colors[layer],
                node_size=[G.nodes[n]["size"] for n in nodes_in_layer],
                alpha=0.7,
            )

        # Draw edges
        nx.draw_networkx_edges(
            G, pos, edge_color="gray", arrows=True, arrowsize=15, width=0.5, alpha=0.4
        )

        # Add labels
        labels = {node: G.nodes[node]["label"] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=self.config.font_size)

        plt.title("Peptide Library Hierarchy")
        plt.axis("off")

        # Save or show the plot
        if self.config.save_plots:
            os.makedirs(self.config.output_dir, exist_ok=True)
            svg_filename = os.path.join(self.config.output_dir, "peptide_hierarchy.svg")
            plt.savefig(svg_filename, format="svg", bbox_inches="tight")
            self.logger.info(f"Saved hierarchy plot to {svg_filename}")

            png_filename = os.path.join(self.config.output_dir, "peptide_hierarchy.png")
            plt.savefig(
                png_filename, format="png", bbox_inches="tight", dpi=self.config.dpi
            )
            self.logger.info(f"Saved hierarchy plot to {png_filename}")

            plt.close()
        else:
            plt.show()
            plt.close()

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process and visualize the peptide hierarchy."""
        if not input_data.hierarchy or not input_data.hierarchy.peptides:
            warnings.warn("No peptides found in input data", UserWarning)
            return input_data

        self.visualize(input_data.hierarchy)
        return input_data

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide (not supported)."""
        warnings.warn("Single peptide visualization not supported", UserWarning)
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides (not supported)."""
        warnings.warn("Peptide set visualization not supported", UserWarning)
        return input_data
