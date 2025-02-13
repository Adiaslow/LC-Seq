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

    def _propagate_failure_status(self, G: nx.DiGraph) -> None:
        """Propagate failure status up the graph.

        If all terminal nodes connected to a node have failed, mark that node as failed.
        This propagates from higher depths to lower depths.

        Args:
            G: NetworkX directed graph representing the hierarchy
        """
        # Process nodes from highest layer to lowest (excluding root)
        for layer in [3, 2, 1]:
            nodes_in_layer = [n for n in G.nodes() if G.nodes[n]["layer"] == layer]

            for node in nodes_in_layer:
                # Get all successors (nodes that use this as precursor)
                successors = list(G.successors(node))

                # If node has no successors (terminal node) and is already marked, skip
                if not successors and G.nodes[node]["status"] in ["SUCCESS", "FAILURE"]:
                    continue

                # If all successors failed, mark this node as failed
                if successors and all(
                    G.nodes[succ]["status"] == "FAILURE" for succ in successors
                ):
                    G.nodes[node]["status"] = "FAILURE"

    def _create_hierarchy_graph(self, hierarchy) -> nx.DiGraph:
        """Create a graph representing abstract peptides and their relationships."""
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
            status="UNKNOWN",
        )

        # Add nodes for each abstract peptide
        for layer in [1, 2, 3]:
            nodes_in_layer = hierarchy.get_nodes_at_depth(layer)
            for node in nodes_in_layer:
                # Create node ID from the effective sequence in reverse order
                effective_sequence = [
                    b for b in node.peptide.blocks if b.identifier != "AgxNull"
                ]
                # Reverse the sequence before joining
                node_id = "-".join(b.identifier for b in effective_sequence[::-1])

                # Add number of equivalent encodings to label
                encoding_count = len(node.peptide.encodings)
                label = f"{node_id}\n({encoding_count} encodings)"

                # Get retention time from the peptide properties
                rt = node.peptide.properties.get("retention_time")

                G.add_node(
                    node_id,
                    layer=layer,
                    sequence=node_id,
                    retention_time=rt,
                    size=self.config.node_sizes[layer],
                    label=label,
                    status=node.peptide.properties.get(
                        "synthesis_status", "UNKNOWN"
                    ).name,
                )

                # Add edges based on precursor relationships
                for precursor in hierarchy.get_precursors(node):
                    if precursor == hierarchy.root:
                        G.add_edge(node_id, root_id)
                    else:
                        precursor_seq = [
                            b
                            for b in precursor.peptide.blocks
                            if b.identifier != "AgxNull"
                        ]
                        # Reverse the precursor sequence before joining
                        precursor_id = "-".join(
                            b.identifier for b in precursor_seq[::-1]
                        )
                        G.add_edge(node_id, precursor_id)

        # Propagate failure status up the graph
        self._propagate_failure_status(G)

        return G

    def _create_layout(self, G: nx.DiGraph) -> Dict:
        """Create a radial hierarchical layout with peptides arranged by layer in concentric circles.

        Args:
            G: NetworkX directed graph representing the hierarchy

        Returns:
            Dict: Mapping of nodes to their positions in the layout
        """
        pos = {}
        layers = defaultdict(list)

        # Group nodes by layer
        for node in G.nodes():
            layer = G.nodes[node]["layer"]
            layers[layer].append(node)

        # Set radius for each layer (center to outside)
        layer_radii = {
            0: 0.0,  # Root at center
            1: 0.3,  # Single blocks
            2: 0.6,  # Double blocks
            3: 1.0,  # Triple blocks
        }

        # Position nodes in each layer
        for layer in sorted(layers.keys()):
            nodes = layers[layer]
            radius = layer_radii[layer]

            if layer == 0:
                # Place root node at center
                pos[nodes[0]] = np.array([0.0, 0.0])
                continue

            # Distribute nodes evenly around the circle
            angle_step = 2 * np.pi / len(nodes)

            for i, node in enumerate(nodes):
                angle = i * angle_step
                # Convert polar coordinates to Cartesian
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                pos[node] = np.array([x, y])

        return pos

    def visualize(self, hierarchy) -> None:
        """Create the hierarchy visualization."""
        if not self.plot_results:
            return

        # Create graph and propagate failure status
        G = self._create_hierarchy_graph(hierarchy)
        pos = self._create_layout(G)

        plt.figure(figsize=self.config.figure_size, dpi=self.config.dpi)

        # Draw edges first so they appear behind nodes
        nx.draw_networkx_edges(
            G,
            pos,
            edge_color="gray",
            arrows=True,
            arrowsize=15,
            width=0.5,
            alpha=0.4,
            arrowstyle="->",
        )

        # Draw nodes with colors based on synthesis status
        status_colors = {
            "UNKNOWN": "lightgray",
            "SUCCESS": "#2ecc71",  # Green
            "FAILURE": "#e74c3c",  # Red
        }

        # Draw nodes in order: FAILURE first, then SUCCESS, then UNKNOWN
        for status in ["FAILURE", "SUCCESS", "UNKNOWN"]:
            nodes = [n for n in G.nodes() if G.nodes[n]["status"] == status]
            if nodes:
                nx.draw_networkx_nodes(
                    G,
                    pos,
                    nodelist=nodes,
                    node_color=status_colors[status],
                    node_size=[G.nodes[n]["size"] for n in nodes],
                    alpha=0.7,
                )

        # Add labels with retention times
        labels = {}
        for node in G.nodes():
            base_label = G.nodes[node]["label"]
            rt = G.nodes[node]["retention_time"]
            rt_text = f"\nRT: {rt:.2f}" if rt is not None else ""
            labels[node] = f"{base_label}{rt_text}"

        # Adjust label positions to prevent overlap
        nx.draw_networkx_labels(
            G,
            pos,
            labels,
            font_size=self.config.font_size,
            horizontalalignment="center",
            verticalalignment="center",
        )

        plt.title("Peptide Library Hierarchy (Radial Layout)")
        plt.axis("equal")  # Equal aspect ratio for circular layout
        plt.axis("off")

        # Save plots with the same logic as before
        if self.config.save_plots:
            os.makedirs(self.config.output_dir, exist_ok=True)

            # Save SVG version
            svg_filename = os.path.join(
                self.config.output_dir, "peptide_hierarchy_radial.svg"
            )
            plt.savefig(svg_filename, format="svg", bbox_inches="tight")
            self.logger.info(f"Saved hierarchy plot to {svg_filename}")

            # Save PNG version
            png_filename = os.path.join(
                self.config.output_dir, "peptide_hierarchy_radial.png"
            )
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
