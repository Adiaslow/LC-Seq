# src/chromatographicpeakpicking/core/factories/hierarchy_factory.py
"""
Module: hierarchy_factory

This module defines the HierarchyFactory class for creating Hierarchy instances.
"""

from typing import Dict, Any, List
from ..prototypes.hierarchy import Hierarchy
from ..prototypes.peptide import Peptide
from ..types.config import GlobalConfig
from ...implementations.caches.hierarchy_cache import HierarchyCache

class HierarchyFactory:
    """
    Responsible for creating Hierarchy instances.

    This class encapsulates the logic for creating new Hierarchy instances,
    including the creation of hierarchies with specific configurations and peptides.
    """

    def __init__(self):
        """Initialize the HierarchyFactory with a singleton cache."""
        self.cache = HierarchyCache()

    def register_prototype(self, name: str, hierarchy: Hierarchy) -> None:
        """Register a prototype hierarchy in the cache."""
        if self.cache is None:
            raise AttributeError("Cache has not been initialized")
        self.cache.set(name, hierarchy)

    def create_hierarchy(self, prototype_name: str, **kwargs: Any) -> Hierarchy:
        """Create a new Hierarchy instance based on a registered prototype."""
        if self.cache is None:
            raise AttributeError("Cache has not been initialized")
        prototype = self.cache.get(prototype_name)
        if prototype is None:
            raise ValueError(f"Prototype '{prototype_name}' is not registered.")
        return prototype.clone(**kwargs)

    def create_hierarchy_from_config(
            self,
            global_config: GlobalConfig,
            peptides: List[Peptide] = None,
            **kwargs: Any
        ) -> Hierarchy:
        """
        Create a new Hierarchy instance with proper handling of equivalent forms.

        Args:
            global_config (GlobalConfig): The configuration settings.
            peptides (List[Peptide], optional): Initial peptides to add.
            kwargs (Any): Additional attributes for the hierarchy.

        Returns:
            Hierarchy: A new Hierarchy instance.
        """
        hierarchy = Hierarchy(global_config=global_config, **kwargs)

        if peptides:
            # Sort peptides by number of non-null blocks to ensure proper relationship building
            sorted_peptides = sorted(
                peptides,
                key=lambda p: hierarchy.count_non_null_blocks(p),
                reverse=True
            )

            # Add peptides in order from most complete to most truncated
            for peptide in sorted_peptides:
                # Before adding, check if we already have a functionally equivalent form
                level = hierarchy.count_non_null_blocks(peptide)
                existing_equiv = next(
                    (existing for existing in hierarchy.levels[level]
                        if hierarchy.are_functionally_equivalent(existing, peptide)),
                    None
                )

                if not existing_equiv:
                    hierarchy.add_peptide(peptide)

        return hierarchy

    def list_prototypes(self) -> Dict[str, Hierarchy]:
        """List all registered prototype hierarchies."""
        return self.cache.cache

    def unregister_prototype(self, name: str) -> None:
        """Unregister a prototype hierarchy from the cache."""
        if self.cache.get(name) is None:
            raise ValueError(f"Prototype '{name}' is not registered.")
        self.cache.remove(name)
