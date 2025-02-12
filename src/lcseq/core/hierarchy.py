# src/lcseq/core/hierarchy.py
"""
This module defines the PeptideHierarchy and PeptideHierarchyNode classes,
which represent the hierarchical structure of peptides and their relationships.

Classes:
    PeptideHierarchyNode: Represents a node in the peptide hierarchy.
    PeptideHierarchy: Represents the complete hierarchy of peptides.
"""

# Standard library imports
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional

# Local application imports
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.synthesis_status import SynthesisStatus

@dataclass
class PeptideHierarchyNode:
    """Represents a node in the peptide hierarchy.
    
    Attributes:
        peptide (Peptide): The peptide represented by the node.
        layer (int): The layer of the node in the hierarchy.
        truncation_edges (Set['PeptideHierarchyNode']): The nodes that are truncations of the current node.
        extension_edges (Set['PeptideHierarchyNode']): The nodes that are extensions of the current node.
        equivalent_encodings (Set[PeptideEncoding]): The encodings that are equivalent to the current node.
        synthesis_status (SynthesisStatus): The synthesis status of the node.
        retention_time (Optional[float]): The retention time of the node.
    
    Methods:
        validate_retention_times: Validate that this node's retention time is greater than all its truncations.
        update_synthesis_status: Update the synthesis status of the node based on retention time validation and truncations.
    """
    peptide: Peptide
    layer: int  # 1 for single-block, 2 for two-block, etc.
    truncation_edges: Set['PeptideHierarchyNode'] = field(default_factory=set)
    extension_edges: Set['PeptideHierarchyNode'] = field(default_factory=set)
    equivalent_encodings: Set[PeptideEncoding] = field(default_factory=set)
    synthesis_status: SynthesisStatus = SynthesisStatus.UNKNOWN
    retention_time: Optional[float] = None

    def validate_retention_times(self) -> bool:
        """Validate that this node's retention time is greater than all its truncations.

        Returns:
            bool: True if validation passes, False otherwise.
        """
        if self.retention_time is None:
            return False

        for truncation in self.truncation_edges:
            if truncation.retention_time is None:
                return False
            if self.retention_time <= truncation.retention_time:
                return False

        return True

    def update_synthesis_status(self) -> None:
        """Update synthesis status based on retention time validation and truncations.

        Returns:
            None
        """
        if not self.validate_retention_times():
            self.synthesis_status = SynthesisStatus.FAILURE
            return

        # Check if any truncations failed
        for truncation in self.truncation_edges:
            if truncation.synthesis_status == SynthesisStatus.FAILURE:
                self.synthesis_status = SynthesisStatus.FAILURE
                return

        self.synthesis_status = SynthesisStatus.SUCCESS

@dataclass
class PeptideHierarchy:
    """Represents the complete hierarchy of peptides.
    
    Attributes:
        nodes (Dict[str, PeptideHierarchyNode]): A dictionary of nodes in the hierarchy.
        layers (Dict[int, Set[PeptideHierarchyNode]]): A dictionary of layers in the hierarchy.
    
    Methods:
        add_node: Add a new node to the hierarchy and establish all relationships.
        _establish_truncation_relationships: Establish all truncation relationships for a node.
    """
    nodes: Dict[str, PeptideHierarchyNode] = field(default_factory=dict)
    layers: Dict[int, Set[PeptideHierarchyNode]] = field(default_factory=lambda: {1: set(), 2: set(), 3: set()})

    def add_node(self, peptide: Peptide) -> PeptideHierarchyNode:
        """Add a new node to the hierarchy and establish all relationships.

        Args:
            peptide (Peptide): The peptide to add to the hierarchy.

        Returns:
            PeptideHierarchyNode: The newly added node.
        """
        if peptide.sequence_str in self.nodes:
            return self.nodes[peptide.sequence_str]

        layer = len(peptide.sequence)
        node = PeptideHierarchyNode(peptide=peptide, layer=layer)

        # Add to both lookups
        self.nodes[peptide.sequence_str] = node
        self.layers[layer].add(node)

        # Establish truncation relationships
        self._establish_truncation_relationships(node)

        return node

    def _establish_truncation_relationships(self, node: PeptideHierarchyNode) -> None:
        """Establish all truncation relationships for a node.

        Args:
            node (PeptideHierarchyNode): The node to establish truncation relationships for.
        """
        sequence = node.peptide.sequence
        n = len(sequence)

        # Generate all possible truncations
        for length in range(1, n):
            for i in range(n - length + 1):
                truncation_seq = sequence[i:i+length]
                truncation_str = '-'.join([block.identifier for block in truncation_seq][::-1])

                if truncation_str in self.nodes:
                    truncation_node = self.nodes[truncation_str]
                    node.truncation_edges.add(truncation_node)
                    truncation_node.extension_edges.add(node)
