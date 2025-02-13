# lcseq/core/hierarchy.py
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
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.synthesis_status import SynthesisStatus


@dataclass
class PeptideHierarchyNode:
    """Represents a node in the peptide hierarchy graph.

    The node focuses purely on graph structure, with all peptide-specific
    information stored in the peptide object and its encodings.

    Attributes:
        peptide (Peptide): The abstract peptide represented by this node
        depth (int): Depth in synthesis graph (number of non-null building blocks)
        rt_threshold (float): Minimum retention time difference required for successful synthesis
    """

    peptide: Peptide
    depth: int
    rt_threshold: float = 0.5  # Default threshold of 0.5

    def validate_retention_times(
        self, precursors: List["PeptideHierarchyNode"]
    ) -> bool:
        """Validate retention times of this peptide's encodings against precursors.

        For each encoding of this peptide, its retention time should be greater
        than all retention times of corresponding precursor encodings.

        Args:
            precursors: List of precursor nodes in the synthesis graph

        Returns:
            bool: True if retention time validation passes
        """
        # Check if this peptide has any encodings with retention times
        peptide_rts = [
            enc.properties.get("retention_time")
            for enc in self.peptide.encodings
            if enc.properties.get("retention_time") is not None
        ]
        if not peptide_rts:
            return False

        # Check each precursor
        for precursor in precursors:
            precursor_rts = [
                enc.properties.get("retention_time")
                for enc in precursor.peptide.encodings
                if enc.properties.get("retention_time") is not None
            ]
            if not precursor_rts:
                return False

            # Each encoding's RT should be greater than all precursor RTs
            for rt in peptide_rts:
                if any(rt <= p_rt for p_rt in precursor_rts):
                    return False

        return True

    def update_synthesis_status(
        self, precursors: Optional[List["PeptideHierarchyNode"]] = None
    ) -> None:
        """Update synthesis status based on retention time relationships with precursors.

        A synthesis is considered successful if:
        1. For depth 1: Always successful (base building blocks)
        2. For depth > 1: RT must be greater than all precursor RTs by at least rt_threshold

        Args:
            precursors: Optional list of precursor nodes. If None, will be determined from hierarchy.
        """
        if self.depth == 0:  # Root node
            self.peptide.properties["synthesis_status"] = SynthesisStatus.UNKNOWN
            return

        if self.depth == 1:  # Base building blocks
            self.peptide.properties["synthesis_status"] = SynthesisStatus.SUCCESS
            return

        # Get retention time of this peptide
        current_rt = None
        for encoding in self.peptide.encodings:
            if "retention_time" in encoding.properties:
                current_rt = encoding.properties["retention_time"]
                break

        if current_rt is None:
            self.peptide.properties["synthesis_status"] = SynthesisStatus.FAILURE
            return

        # Get precursor retention times
        if precursors is None:
            precursors = []  # Should be populated from hierarchy

        precursor_rts = []
        for precursor in precursors:
            for encoding in precursor.peptide.encodings:
                if "retention_time" in encoding.properties:
                    precursor_rts.append(encoding.properties["retention_time"])
                    break

        if not precursor_rts:
            self.peptide.properties["synthesis_status"] = SynthesisStatus.FAILURE
            return

        # Check if any precursor has failed synthesis
        any_precursor_failed = any(
            precursor.peptide.properties.get("synthesis_status")
            == SynthesisStatus.FAILURE
            for precursor in precursors
        )

        if any_precursor_failed:
            self.peptide.properties["synthesis_status"] = SynthesisStatus.FAILURE
            return

        # Check if current RT is greater than all precursor RTs by at least rt_threshold
        max_precursor_rt = max(precursor_rts)
        if current_rt > (max_precursor_rt + self.rt_threshold):
            self.peptide.properties["synthesis_status"] = SynthesisStatus.SUCCESS
        else:
            self.peptide.properties["synthesis_status"] = SynthesisStatus.FAILURE

    def __hash__(self) -> int:
        """Hash based on peptide's effective sequence."""
        return hash(self.peptide)

    def __eq__(self, other: Any) -> bool:
        """Equality based on peptide's effective sequence."""
        if not isinstance(other, PeptideHierarchyNode):
            return False
        return self.peptide == other.peptide

    def __str__(self) -> str:
        """String representation of the node."""
        return f"PeptideHierarchyNode(peptide={self.peptide}, depth={self.depth})"

    def __repr__(self) -> str:
        """Detailed string representation of the node."""
        return self.__str__()


class PeptideHierarchy:
    """Graph-based representation of peptide synthesis relationships.

    The hierarchy is represented as a NetworkX DiGraph where:
    - Nodes are PeptideHierarchyNode objects
    - Edges represent synthesis relationships (precursor -> product)
    - Root node represents the starting point (depth 0)
    """

    def __init__(self, null_identifier: str = "AgxNull"):
        """Initialize empty hierarchy with root node.

        Args:
            null_identifier: Identifier for null building blocks
        """
        self.graph = nx.DiGraph()
        self.null_identifier = null_identifier

        # Initialize root node
        root_sequence = [BuildingBlockRegistry.get(null_identifier) for _ in range(3)]
        root_peptide = Peptide(blocks=root_sequence)
        root_peptide.properties["synthesis_status"] = (
            SynthesisStatus.SUCCESS
        )  # Root is always successful
        self.root = PeptideHierarchyNode(peptide=root_peptide, depth=0)
        self.graph.add_node(self.root)

    def add_peptide(self, peptide: Peptide) -> PeptideHierarchyNode:
        """Add a peptide to the hierarchy.

        Args:
            peptide: The peptide to add

        Returns:
            PeptideHierarchyNode: The created node
        """
        # Create node
        node = PeptideHierarchyNode(
            peptide=peptide, depth=len(peptide.effective_sequence)
        )
        self.graph.add_node(node)

        # Establish relationships
        self._establish_relationships(node)

        # Update synthesis status based on precursors
        precursors = self.get_precursors(node)
        node.update_synthesis_status(precursors)

        return node

    def _establish_relationships(self, node: PeptideHierarchyNode) -> None:
        """Establish synthesis relationships in the graph.

        Args:
            node: Node to establish relationships for
        """
        if node.depth == 0:
            return

        # Connect depth 1 nodes to root
        if node.depth == 1:
            self.graph.add_edge(self.root, node)
            return

        sequence = node.peptide.effective_sequence

        # For depth 2 nodes, find valid pairs of depth 1 precursors
        if node.depth == 2:
            for graph_node in self.graph.nodes:
                if not isinstance(graph_node, PeptideHierarchyNode):
                    continue
                if graph_node.depth == 1:
                    if graph_node.peptide.effective_sequence[0] in sequence:
                        self.graph.add_edge(graph_node, node)
            return

        # For depth 3 nodes, find valid depth 2 precursors
        if node.depth == 3:
            # Get all possible pairs from the sequence
            pairs = [
                (sequence[i], sequence[j])
                for i in range(len(sequence))
                for j in range(i + 1, len(sequence))
            ]

            for graph_node in self.graph.nodes:
                if not isinstance(graph_node, PeptideHierarchyNode):
                    continue
                if graph_node.depth == 2:
                    precursor_seq = graph_node.peptide.effective_sequence
                    # Check if precursor sequence matches any consecutive pair
                    if tuple(precursor_seq) in pairs:
                        self.graph.add_edge(graph_node, node)

    def get_precursors(self, node: PeptideHierarchyNode) -> List[PeptideHierarchyNode]:
        """Get immediate precursor nodes of a given node."""
        return list(self.graph.predecessors(node))

    def get_products(self, node: PeptideHierarchyNode) -> List[PeptideHierarchyNode]:
        """Get immediate product nodes of a given node."""
        return list(self.graph.successors(node))

    def get_nodes_at_depth(self, depth: int) -> List[PeptideHierarchyNode]:
        """Get all nodes at a specific depth in the hierarchy."""
        return [
            n
            for n in self.graph.nodes
            if isinstance(n, PeptideHierarchyNode) and n.depth == depth
        ]
