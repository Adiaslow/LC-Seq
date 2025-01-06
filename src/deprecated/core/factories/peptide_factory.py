# src/chromatographicpeakpicking/core/factories/peptide_factory.py
"""
Module: peptide_factory

This module defines the PeptideFactory class, which is responsible for creating Peptide
instances. The PeptideFactory class follows the Factory Pattern and the Prototype Pattern to
allow for efficient creation and cloning of Peptide instances with optional modifications.
"""

from typing import Dict, Any, List
from ..prototypes.peptide import Peptide
from ..prototypes.building_block import BuildingBlock
from ...implementations.caches.peptide_cache import PeptideCache

class PeptideFactory:
    """
    Responsible for creating Peptide instances.

    This class encapsulates the logic for creating new Peptide instances,
    including the creation of peptides with specific sequences and properties.

    Attributes:
        cache (PeptideCache): The singleton cache for storing and retrieving peptide prototypes.
    """

    def __init__(self):
        """Initialize the PeptideFactory with a singleton cache."""
        self.cache = PeptideCache()

    def register_prototype(self, name: str, peptide: Peptide) -> None:
        """
        Register a prototype peptide in the cache.

        Args:
            name (str): The name to register the prototype under.
            peptide (Peptide): The Peptide instance to register as a prototype.

        Raises:
            AttributeError: If self.cache is None
        """
        if self.cache is None:
            raise AttributeError("Cache has not been initialized")
        self.cache.set(name, peptide)

    def create_peptide(self, prototype_name: str, **kwargs: Any) -> Peptide:
        """
        Create a new Peptide instance based on a registered prototype.

        Args:
            prototype_name (str): The name of the prototype to use.
            kwargs (Any): Attributes to override in the new instance.

        Returns:
            Peptide: A new Peptide instance based on the prototype.

        Raises:
            ValueError: If the prototype_name is not registered.
        """
        if self.cache is None:
            raise AttributeError("Cache has not been initialized")
        prototype = self.cache.get(prototype_name)
        if prototype is None:
            raise ValueError(f"Prototype '{prototype_name}' is not registered.")
        return prototype.clone(**kwargs)

    def create_peptide_from_sequence(self, sequence: List[BuildingBlock], **kwargs: Any) -> Peptide:
        """
        Create a new Peptide instance directly from a sequence.

        Args:
            sequence (List[BuildingBlock]): The sequence of building blocks.
            kwargs (Any): Additional attributes for the peptide.

        Returns:
            Peptide: A new Peptide instance.
        """
        return Peptide(sequence=sequence, **kwargs)

    def list_prototypes(self) -> Dict[str, Peptide]:
        """List all registered prototype peptides."""
        return self.cache.cache

    def unregister_prototype(self, name: str) -> None:
        """Unregister a prototype peptide from the cache."""
        if self.cache.get(name) is None:
            raise ValueError(f"Prototype '{name}' is not registered.")
        self.cache.remove(name)
