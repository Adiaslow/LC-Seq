"""
This module defines the PeptideHierarchy and PeptideHierarchyNode classes,
which represent the hierarchical structure of peptides and their relationships.

Classes:
    PeptideHierarchyNode: Represents a node in the peptide hierarchy.
    PeptideHierarchy: Represents the complete hierarchy of peptides.
"""

# Standard library imports
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

# Third party imports
import networkx as nx
import matplotlib.pyplot as plt
import os

# Local application imports
from src.lcseq.core.building_block import BuildingBlock
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.synthesis_status import SynthesisStatus


@dataclass
class PeptideHierarchyNode:
    """Represents a node in the peptide hierarchy.

    Attributes:
        peptide (Peptide): The peptide represented by the node.
        layer (int): The layer of the node in the hierarchy (1 for single-block, 2 for two-block, etc.).
        truncation_edges (Set['PeptideHierarchyNode']): The nodes that are truncations of the current node.
        extension_edges (Set['PeptideHierarchyNode']): The nodes that are extensions of the current node.
        equivalent_encodings (Set[PeptideEncoding]): The encodings that are equivalent to the current node.
        synthesis_status (SynthesisStatus): The synthesis status of the node.
        retention_time (Optional[float]): The retention time of the node.
    """

    peptide: Peptide
    layer: int
    truncation_edges: Set["PeptideHierarchyNode"] = field(default_factory=set)
    extension_edges: Set["PeptideHierarchyNode"] = field(default_factory=set)
    equivalent_encodings: Set[PeptideEncoding] = field(default_factory=set)
    synthesis_status: SynthesisStatus = SynthesisStatus.UNKNOWN
    retention_time: Optional[float] = None

    @property
    def encodings(self) -> List[PeptideEncoding]:
        """Get the encodings from the peptide."""
        return self.peptide.encodings

    def validate_retention_times(self) -> bool:
        """Validate that this node's retention time is greater than all its truncations."""
        if self.retention_time is None:
            return False

        for truncation in self.truncation_edges:
            if truncation.retention_time is None:
                return False
            if self.retention_time <= truncation.retention_time:
                return False

        return True

    def update_synthesis_status(self) -> None:
        """Update synthesis status based on retention time validation and truncations."""
        if not self.validate_retention_times():
            self.synthesis_status = SynthesisStatus.FAILURE
            return

        # Check if any truncations failed
        for truncation in self.truncation_edges:
            if truncation.synthesis_status == SynthesisStatus.FAILURE:
                self.synthesis_status = SynthesisStatus.FAILURE
                return

        self.synthesis_status = SynthesisStatus.SUCCESS

    def __str__(self) -> str:
        """Return a string representation of the node."""
        return f"PeptideHierarchyNode(peptide={self.peptide}, layer={self.layer})"

    def __repr__(self) -> str:
        """Return a string representation of the node."""
        return self.__str__()

    def __eq__(self, other: Any) -> bool:
        """Check if two nodes are equal."""
        if not isinstance(other, PeptideHierarchyNode):
            return False
        return self.peptide == other.peptide

    def __hash__(self) -> int:
        """Return the hash of the node."""
        return hash(self.peptide)


@dataclass
class PeptideHierarchy:
    """Represents the complete hierarchy of peptides."""

    NULL_IDENTIFIER: str = "AgxNull"
    nodes: Dict[str, PeptideHierarchyNode] = field(default_factory=dict)
    layers: Dict[int, Set[PeptideHierarchyNode]] = field(
        default_factory=lambda: {1: set(), 2: set(), 3: set()}
    )
    root: Optional[PeptideHierarchyNode] = None

    def __post_init__(self) -> None:
        """Initialize the root node during hierarchy creation."""
        # Create a peptide with all null blocks for the root
        root_sequence = [
            BuildingBlock(identifier=self.NULL_IDENTIFIER, properties={})
            for _ in range(3)  # Assuming max depth of 3
        ]
        root_peptide = Peptide(sequence=root_sequence)
        self.root = PeptideHierarchyNode(peptide=root_peptide, layer=0)

    @property
    def children(self) -> List[PeptideHierarchyNode]:
        """Get all nodes in the hierarchy."""
        return list(self.nodes.values())

    @property
    def peptides(self) -> List[Peptide]:
        """Get all peptides in the hierarchy."""
        return [node.peptide for node in self.children]

    def get_layer(self, layer: int) -> Set[PeptideHierarchyNode]:
        """Get all nodes in a specific layer."""
        return self.layers.get(layer, set())

    def add_node(self, peptide: Peptide) -> PeptideHierarchyNode:
        """Add a new node to the hierarchy and establish all relationships."""
        # Get effective sequence (non-null blocks)
        effective_sequence = [
            b for b in peptide.sequence if b.identifier != self.NULL_IDENTIFIER
        ]

        # Handle root node case (all nulls)
        if not effective_sequence:
            return self.root

        # Generate canonical key for this abstract peptide
        canonical_key = "-".join(b.identifier for b in effective_sequence)

        # If we already have this abstract peptide, add this as another encoding
        if canonical_key in self.nodes:
            node = self.nodes[canonical_key]
            node.equivalent_encodings.add(peptide.encodings[0])  # Add this encoding
            return node

        # Create new node for this abstract peptide
        node = PeptideHierarchyNode(peptide=peptide, layer=len(effective_sequence))

        # Add initial encoding
        if peptide.encodings:
            node.equivalent_encodings.add(peptide.encodings[0])

        # Add to lookups
        self.nodes[canonical_key] = node
        self.layers[len(effective_sequence)].add(node)

        # Establish relationships
        self._establish_relationships(node)

        return node

    def _establish_relationships(self, node: PeptideHierarchyNode) -> None:
        """Establish parent-child relationships for this node.

        For a node at depth N, connect it to appropriate nodes at depth N-1
        based on the valid cartesian products of building blocks.
        """
        effective_sequence = [
            b for b in node.peptide.sequence if b.identifier != self.NULL_IDENTIFIER
        ]
        depth = len(effective_sequence)

        if depth == 1:
            # Connect to root
            node.extension_edges.add(self.root)
            self.root.truncation_edges.add(node)
        else:
            # Find parent nodes at depth-1 that this node extends
            parent_sequence = effective_sequence[:-1]
            parent_key = "-".join(b.identifier for b in parent_sequence)

            if parent_key in self.nodes:
                parent_node = self.nodes[parent_key]
                node.extension_edges.add(parent_node)
                parent_node.truncation_edges.add(node)

    def get_hierarchy_structure(self) -> Dict[str, Any]:
        """
        Generate a structured representation of the hierarchy for visualization/debugging.

        Returns:
            Dict with the following structure:
            {
                'layers': {
                    1: ['A', 'B', 'C'],  # nodes in layer 1
                    2: ['A-B', 'B-C'],   # nodes in layer 2
                    3: ['A-B-C']         # nodes in layer 3
                },
                'relationships': {
                    'A-B': {
                        'truncations': ['A', 'B'],
                        'extensions': ['A-B-C'],
                        'synthesis_status': 'SUCCESS',
                        'retention_time': 5.6
                    },
                    # ... other nodes
                }
            }
        """
        structure = {"layers": {}, "relationships": {}}

        # Populate layers
        for layer_num, nodes in self.layers.items():
            structure["layers"][layer_num] = [
                node.peptide.sequence_str for node in nodes
            ]

        # Populate relationships
        for seq_str, node in self.nodes.items():
            structure["relationships"][seq_str] = {
                "truncations": [n.peptide.sequence_str for n in node.truncation_edges],
                "extensions": [n.peptide.sequence_str for n in node.extension_edges],
                "synthesis_status": node.synthesis_status.name,
                "retention_time": node.retention_time,
            }

        return structure

    def visualize_hierarchy(self) -> None:
        """
        Visualize the peptide hierarchy using NetworkX. Integrates with HierarchyVisualizer class structure.
        """
        # Create graph with unique node instances
        G = nx.DiGraph()

        # Add nodes with attributes for each layer
        layer_colors = ["lightgray", "#3498db", "#2ecc71", "#e74c3c"]
        node_sizes = {
            0: 1200,  # Root node
            1: 900,  # Single building blocks
            2: 600,  # Two building blocks
            3: 400,  # Three building blocks
        }

        # Add root node
        root_id = "ROOT"
        G.add_node(
            root_id,
            layer=0,
            sequence=root_id,
            size=node_sizes[0],
            label="ROOT",
            retention_time=None,
        )

        # Add peptide nodes by layer
        for layer in [1, 2, 3]:
            nodes_in_layer = self.get_layer(layer)
            for node in nodes_in_layer:
                G.add_node(
                    node.peptide.sequence_str,
                    layer=layer,
                    sequence=node.peptide.sequence_str,
                    retention_time=node.retention_time,
                    size=node_sizes[layer],
                    label=node.peptide.sequence_str,
                    status=node.synthesis_status.name,
                )

        # Add edges for truncation relationships
        for seq_str, node in self.nodes.items():
            for truncation in node.truncation_edges:
                G.add_edge(seq_str, truncation.peptide.sequence_str)

        # Create hierarchical layout
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Set up the plot
        plt.figure(figsize=(40, 40), dpi=300)

        # Draw nodes by layer
        for layer in range(4):  # Including root layer
            nodes_in_layer = [n for n in G.nodes() if G.nodes[n]["layer"] == layer]
            if not nodes_in_layer:
                continue

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

        # Add labels with retention times
        labels = {}
        for node in G.nodes():
            rt = G.nodes[node]["retention_time"]
            layer = G.nodes[node]["layer"]
            rt_text = f"\nRT: {rt:.2f}" if rt is not None else ""
            labels[node] = f"{G.nodes[node]['label']}\nLayer {layer}{rt_text}"

        nx.draw_networkx_labels(G, pos, labels, font_size=10)

        plt.title("Peptide Library Hierarchy")
        plt.axis("off")

        # Create output directory if it doesn't exist
        os.makedirs("hierarchy_plots", exist_ok=True)

        # Save both SVG and PNG versions
        svg_filename = os.path.join("hierarchy_plots", "peptide_hierarchy.svg")
        plt.savefig(svg_filename, format="svg", bbox_inches="tight")

        png_filename = os.path.join("hierarchy_plots", "peptide_hierarchy.png")
        plt.savefig(png_filename, format="png", bbox_inches="tight", dpi=300)

        plt.close()
