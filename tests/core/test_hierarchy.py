import pytest
import yaml
from pathlib import Path
from typing import Dict, List, Any

from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.synthesis_status import SynthesisStatus
from src.lcseq.core.hierarchy import PeptideHierarchy, PeptideHierarchyNode
from src.lcseq.pipeline.components.visualizers.hierarchy_visualizer import (
    HierarchyVisualizer,
    HierarchyVisualizerConfig,
)


def initialize_building_blocks(
    building_blocks_data: Dict[str, Dict[str, Dict[str, Any]]]
) -> None:
    """Initialize the BuildingBlockRegistry with building blocks from the input data."""
    try:
        BuildingBlockRegistry.clear()
    except ValueError:
        pass

    # Register all building blocks
    for position, blocks in building_blocks_data.items():
        for identifier, properties in blocks.items():
            block = BuildingBlock(identifier=identifier, properties=properties)
            BuildingBlockRegistry.register(block)


def create_peptide_library(peptides_data: List[Dict[str, Any]]) -> List[Peptide]:
    """Create Peptide objects from input data."""
    peptides = []

    for peptide_data in peptides_data:
        sequence = peptide_data["sequence"]
        properties = peptide_data.get("properties", {})

        # Create building block objects for sequence
        bb_sequence = [BuildingBlockRegistry.get(bb) for bb in sequence]

        # Create encoding using the actual sequence data
        encodings = []
        if "chromatogram" in peptide_data:
            chromatogram_data = peptide_data["chromatogram"]
            encoding_props = {}

            if chromatogram_data["times"] and chromatogram_data["intensities"]:
                # Find the time at maximum intensity
                max_intensity_idx = max(
                    range(len(chromatogram_data["intensities"])),
                    key=lambda i: chromatogram_data["intensities"][i],
                )
                rt = chromatogram_data["times"][max_intensity_idx]

                # Store retention time in both encoding properties and peptide properties
                encoding_props["retention_time"] = rt
                properties["retention_time"] = rt

            encoding = PeptideEncoding(blocks=bb_sequence, properties=encoding_props)
            encodings.append(encoding)

        peptide = Peptide(
            blocks=bb_sequence, properties=properties, encodings=encodings
        )
        peptides.append(peptide)

    return peptides


def test_peptide_hierarchy():
    """Test the peptide hierarchy functionality."""
    # Load test data from YAML
    data_path = Path("tests/data/prepared_data.yaml")
    with open(data_path, "r") as f:
        data = yaml.safe_load(f)

    building_blocks_data = data["building_blocks"]
    peptides_data = data["peptides"]

    # Initialize building blocks
    initialize_building_blocks(building_blocks_data)

    # Create peptide library and organize by sequence
    peptides = {}
    for peptide in create_peptide_library(peptides_data):
        # Use the effective sequence string as the key
        sequence = peptide.effective_sequence_str
        peptides[sequence] = peptide

    # Create hierarchy
    hierarchy = PeptideHierarchy()
    nodes = {}

    # Add peptides to hierarchy in order of increasing depth
    # First add depth 1 nodes
    depth_1_sequences = [seq for seq in peptides.keys() if len(seq.split("-")) == 1]
    for sequence in depth_1_sequences:
        nodes[sequence] = hierarchy.add_peptide(peptides[sequence])

    # Then add depth 2 nodes
    depth_2_sequences = [seq for seq in peptides.keys() if len(seq.split("-")) == 2]
    for sequence in depth_2_sequences:
        nodes[sequence] = hierarchy.add_peptide(peptides[sequence])

    # Finally add depth 3 nodes
    depth_3_sequences = [seq for seq in peptides.keys() if len(seq.split("-")) == 3]
    for sequence in depth_3_sequences:
        nodes[sequence] = hierarchy.add_peptide(peptides[sequence])

    # Create visualizer with custom config
    config = HierarchyVisualizerConfig(
        figure_size=(30, 30),
        dpi=300,
        font_size=8,
        save_plots=True,
        output_dir="hierarchy_plots",
    )
    visualizer = HierarchyVisualizer(config=config, plot_results=True)

    # Print all sequences for debugging
    print("\nAvailable sequences in nodes:")
    for node in nodes.values():
        print(
            f"Node depth: {node.depth}, sequence: {node.peptide.effective_sequence_str}"
        )

    # Test node depths
    for node in nodes.values():
        assert node.depth == len(
            node.peptide.effective_sequence
        ), f"Node sequence {node.peptide.effective_sequence_str} has incorrect depth: {node.depth} != {len(node.peptide.effective_sequence)}"

    # Test precursor relationships for Val_Nvl_Leu
    val_nvl_leu = next(
        (
            node
            for node in nodes.values()
            if node.peptide.effective_sequence_str == "Val-Nvl-Leu"
        ),
        None,
    )

    if val_nvl_leu:
        precursors = hierarchy.get_precursors(val_nvl_leu)
        precursor_sequences = {p.peptide.effective_sequence_str for p in precursors}
        expected_precursors = {"Nvl-Leu", "Val-Nvl", "Val-Leu"}

        assert (
            precursor_sequences == expected_precursors
        ), f"Expected precursors {expected_precursors}, got {precursor_sequences}"

        # Verify depth
        assert (
            val_nvl_leu.depth == 3
        ), f"Expected depth 3 for Val-Nvl-Leu, got {val_nvl_leu.depth}"

        # Verify precursor depths
        for precursor in precursors:
            assert (
                precursor.depth == 2
            ), f"Expected depth 2 for precursor {precursor.peptide.effective_sequence_str}, got {precursor.depth}"

    # Test depth relationships
    depth_1_nodes = hierarchy.get_nodes_at_depth(1)
    depth_2_nodes = hierarchy.get_nodes_at_depth(2)
    depth_3_nodes = hierarchy.get_nodes_at_depth(3)

    # Verify that each depth 2 node has two depth 1 precursors
    for node in depth_2_nodes:
        precursors = hierarchy.get_precursors(node)
        assert (
            len(precursors) == 2
        ), f"Node {node.peptide.effective_sequence_str} has {len(precursors)} precursors, expected 2"
        assert all(
            p.depth == 1 for p in precursors
        ), f"Not all precursors of {node.peptide.effective_sequence_str} are depth 1"

    # Verify that each depth 3 node has three depth 2 precursors
    for node in depth_3_nodes:
        precursors = hierarchy.get_precursors(node)
        assert (
            len(precursors) == 3
        ), f"Node {node.peptide.effective_sequence_str} has {len(precursors)} precursors, expected 3"
        assert all(
            p.depth == 2 for p in precursors
        ), f"Not all precursors of {node.peptide.effective_sequence_str} are depth 2"

    # Test root connections
    root_children = hierarchy.get_products(hierarchy.root)
    assert all(
        child.depth == 1 for child in root_children
    ), "Not all root children are depth 1 nodes"

    # Test synthesis status update for all depth 3 nodes
    for node in depth_3_nodes:
        precursors = hierarchy.get_precursors(node)
        node.update_synthesis_status(precursors)
        status = node.peptide.properties.get("synthesis_status")
        assert status in [
            SynthesisStatus.SUCCESS,
            SynthesisStatus.FAILURE,
        ], f"Expected SUCCESS or FAILURE status for {node.peptide.effective_sequence_str}, got {status}"

    # Generate visualization using HierarchyVisualizer
    visualizer.visualize(hierarchy)


def test_synthesis_status_propagation():
    """Test that synthesis status is correctly determined based on truncation relationships."""
    # Create building blocks
    blocks = {
        "A": BuildingBlock(identifier="A", properties={"smiles": "C(C)C"}),
        "B": BuildingBlock(identifier="B", properties={"smiles": "C(C)C"}),
        "C": BuildingBlock(identifier="C", properties={"smiles": "C(C)C"}),
        "N": BuildingBlock(identifier="N", properties={"smiles": ""}),  # Null block
    }

    # Register blocks
    for block in blocks.values():
        BuildingBlockRegistry.register(block)

    # Create peptides with different retention times
    # Note: Each step should increase RT by more than the threshold (0.5)
    peptides = {
        # Single blocks (depth 1)
        "A": Peptide(
            blocks=[blocks["A"]],
            encodings=[
                PeptideEncoding(
                    blocks=[blocks["A"]], properties={"retention_time": 1.0}
                )
            ],
        ),
        "B": Peptide(
            blocks=[blocks["B"]],
            encodings=[
                PeptideEncoding(
                    blocks=[blocks["B"]], properties={"retention_time": 2.0}
                )
            ],
        ),
        "C": Peptide(
            blocks=[blocks["C"]],
            encodings=[
                PeptideEncoding(
                    blocks=[blocks["C"]], properties={"retention_time": 3.0}
                )
            ],
        ),
        # Double blocks (depth 2)
        "B_A": Peptide(
            blocks=[blocks["B"], blocks["A"]],
            encodings=[
                PeptideEncoding(
                    blocks=[blocks["B"], blocks["A"]],
                    properties={"retention_time": 4.0},  # > max(1.0, 2.0) + 0.5
                )
            ],
        ),
        "C_A": Peptide(
            blocks=[blocks["C"], blocks["A"]],
            encodings=[
                PeptideEncoding(
                    blocks=[blocks["C"], blocks["A"]],
                    properties={"retention_time": 5.0},  # > max(1.0, 3.0) + 0.5
                )
            ],
        ),
        "C_B": Peptide(
            blocks=[blocks["C"], blocks["B"]],
            encodings=[
                PeptideEncoding(
                    blocks=[blocks["C"], blocks["B"]],
                    properties={"retention_time": 3.5},  # Not > max(2.0, 3.0) + 0.5
                )
            ],
        ),
        # Triple block (depth 3)
        "C_B_A": Peptide(
            blocks=[blocks["C"], blocks["B"], blocks["A"]],
            encodings=[
                PeptideEncoding(
                    blocks=[blocks["C"], blocks["B"], blocks["A"]],
                    properties={
                        "retention_time": 7.0
                    },  # Would be success if C_B hadn't failed
                )
            ],
        ),
    }

    # Create hierarchy
    hierarchy = PeptideHierarchy()
    nodes = {}

    # Add peptides to hierarchy in order of increasing depth
    # First add depth 1 nodes
    for name in ["A", "B", "C"]:
        nodes[name] = hierarchy.add_peptide(peptides[name])

    # Then add depth 2 nodes
    for name in ["B_A", "C_A", "C_B"]:
        nodes[name] = hierarchy.add_peptide(peptides[name])

    # Finally add depth 3 node
    nodes["C_B_A"] = hierarchy.add_peptide(peptides["C_B_A"])

    # Verify depth 2 synthesis status
    assert (
        nodes["B_A"].peptide.properties["synthesis_status"] == SynthesisStatus.SUCCESS
    ), "B_A should be successful (RT 4.0 > max(A:1.0, B:2.0))"
    assert (
        nodes["C_A"].peptide.properties["synthesis_status"] == SynthesisStatus.SUCCESS
    ), "C_A should be successful (RT 5.0 > max(C:3.0, A:1.0))"
    assert (
        nodes["C_B"].peptide.properties["synthesis_status"] == SynthesisStatus.FAILURE
    ), "C_B should be failed (RT 3.5 not > max(C:3.0, B:2.0))"

    # Verify depth 3 synthesis status
    assert (
        nodes["C_B_A"].peptide.properties["synthesis_status"] == SynthesisStatus.FAILURE
    ), "C_B_A should be failed due to failed precursor C_B"

    # Create visualizer to see the results
    config = HierarchyVisualizerConfig(
        figure_size=(30, 30),
        dpi=300,
        font_size=8,
        save_plots=True,
        output_dir="hierarchy_test_plots",
    )
    visualizer = HierarchyVisualizer(config=config, plot_results=True)
    visualizer.visualize(hierarchy)


if __name__ == "__main__":
    test_peptide_hierarchy()
