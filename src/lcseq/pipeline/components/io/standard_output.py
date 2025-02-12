# src/lcseq/pipeline/components/standard_output.py
"""
This module provides a pipeline component for handling standard output data.
It includes a class for formatting output data and a method for saving results to a YAML file.

Classes:
    StandardOutput: Pipeline component for handling standard output data.
"""
# Standard library imports
import logging
import os
from typing import Dict, Any, Optional
import yaml

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    SinglePeptideInput,
    PeptideSetInput,
    PeptideHierarchyInput
)

logger = logging.getLogger(__name__)

class StandardOutput(PipelineComponent):
    """StandardOutput class for handling standard output data.

    Attributes:
        logger: Logger for logging messages.
        input_file_path: Path to the input file.
        original_data: Original data loaded from the input file.

    Methods:
        __init__: Initialize the StandardOutput.
        _add_retention_time: Add retention time to the peptide properties.
        _format_output: Format the output data structure.
        _format_new_output: Format output for new data without original structure.
        _save_results: Save results to a YAML file with '_results' appended to the original filename.
        process_peptide: Process a single peptide output.
        process_peptide_set: Process a set of peptides output.
        process_hierarchy: Process a hierarchy of peptides output.
    """
    def __init__(self, input_file_path: Optional[str] = None):
        """Initialize the StandardOutput.

        Args:
            input_file_path (Optional[str], optional): Path to the input file.
                Default is None.
        """
        self.logger = logging.getLogger(__name__)
        self.input_file_path = input_file_path
        self.original_data = None
        if input_file_path:
            try:
                with open(input_file_path, 'r') as f:
                    self.original_data = yaml.safe_load(f)
            except Exception as e:
                self.logger.error(f"Failed to load original input file: {str(e)}")

    def _add_retention_time(self, peptide):
        """Add retention time from selected peak to peptide properties.

        Args:
            peptide (Peptide): The peptide to add retention time to.

        Returns:
            Peptide: The peptide with retention time added.
        """
        for encoding in peptide.encodings:
            if encoding.chromatogram and encoding.chromatogram.peaks:
                if encoding.chromatogram.peaks:
                    peak = encoding.chromatogram.peaks[0]
                    peptide.properties['retention_time'] = peak.apex_time

                    # Add analysis results to properties
                    if hasattr(encoding.chromatogram, 'properties'):
                        peptide.properties['chromatogram_metrics'] = {
                            'noise_level': encoding.chromatogram.properties.get('noise_level'),
                            'signal_to_noise': encoding.chromatogram.properties.get('signal_to_noise'),
                            'baseline_mean': encoding.chromatogram.properties.get('baseline_mean'),
                            'total_area': encoding.chromatogram.properties.get('total_area'),
                            'dynamic_range': encoding.chromatogram.properties.get('dynamic_range')
                        }

                    # Add peak metrics to properties
                    if encoding.chromatogram.peaks:
                        peak = encoding.chromatogram.peaks[0]
                        peptide.properties['picked_peak_metrics'] = {
                            'apex_time': float(peak.apex_time),
                            'end_time': float(peak.end_time),
                            'apex_intensity': float(peak.apex_intensity),
                            'width': float(peak.properties.get('width', 0.0)),
                            'area': float(peak.properties.get('area', 0.0)),
                            'symmetry': float(peak.properties.get('symmetry', 0.0)),
                            'gaussian_residuals':
                                float(peak.properties.get(
                                    'gaussian_residuals', 0.0
                                )),
                            'gaussian_fit_amplitude':
                                float(peak.properties.get(
                                    'gaussian_fit_params', {}
                                ).get('amplitude', 0.0)),
                            'gaussian_fit_mean':
                                float(peak.properties.get(
                                    'gaussian_fit_params', {}
                                ).get('mean', 0.0)),
                            'gaussian_fit_sigma':
                                float(peak.properties.get(
                                    'gaussian_fit_params', {}
                                ).get('sigma', 0.0))
                        }
                    break
        return peptide

    def _format_output(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the output data structure while preserving original format.

        Args:
            input_data (Dict[str, Any]): The input data to format.

        Returns:
            Dict[str, Any]: The formatted output data.
        """
        if not self.original_data:
            return self._format_new_output(input_data)

        # Create a deep copy of original data
        output_data = dict(self.original_data)

        # Update peptide information while preserving structure
        for peptide in input_data['peptides']:
            # Find matching peptide in original data
            for orig_peptide in output_data['peptides']:
                if orig_peptide['identifier'] == peptide.sequence_str:
                    # Preserve original properties and add new ones
                    orig_peptide['properties'].update(peptide.properties)

                    # Update chromatogram data if it exists
                    if hasattr(peptide, 'encodings'):
                        for encoding in peptide.encodings:
                            if encoding.chromatogram:
                                chrom_data = {
                                    'times': encoding.chromatogram.times.tolist(),
                                    'intensities':
                                        encoding.chromatogram.intensities.tolist()
                                }
                                if encoding.chromatogram.peaks:
                                    chrom_data['peaks'] = [{
                                        'apex_time': float(peak.apex_time),
                                        'end_time': float(peak.end_time),
                                        'apex_intensity': float(peak.apex_intensity),
                                        'width':
                                            float(peak.properties.get('width', 0.0)),
                                        'area': float(peak.properties.get('area', 0.0)),
                                        'symmetry':
                                            float(peak.properties.get('symmetry', 0.0)),
                                        'gaussian_residuals':
                                            float(peak.properties.get(
                                                'gaussian_residuals', 0.0
                                            )),
                                        'gaussian_fit_amplitude':
                                            float(peak.properties.get(
                                                'gaussian_fit_params', {}
                                            ).get('amplitude', 0.0)),
                                        'gaussian_fit_mean':
                                            float(peak.properties.get(
                                                'gaussian_fit_params', {}
                                            ).get('mean', 0.0)),
                                        'gaussian_fit_sigma':
                                            float(peak.properties.get(
                                                'gaussian_fit_params', {}
                                            ).get('sigma', 0.0))
                                    } for peak in encoding.chromatogram.peaks]
                                orig_peptide['chromatogram'] = chrom_data
                    break

        return output_data

    def _format_new_output(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for new data without original structure.

        Args:
            input_data (Dict[str, Any]): The input data to format.

        Returns:
            Dict[str, Any]: The formatted output data.
        """
        return {
            'building_blocks': {},  # Empty building blocks section
            'peptides': [{
                'identifier': peptide.sequence_str,
                'sequence': [block.identifier for block in peptide.sequence],
                'properties': peptide.properties,
                'chromatogram': next(
                    (
                        {
                            'times': encoding.chromatogram.times.tolist(),
                            'intensities': encoding.chromatogram.intensities.tolist(),
                            'peaks': [{
                                'apex_time': float(peak.apex_time),
                                'end_time': float(peak.end_time),
                                'apex_intensity': float(peak.apex_intensity),
                                'width':
                                    float(peak.properties.get('width', 0.0)),
                                'area': float(peak.properties.get('area', 0.0)),
                                'symmetry':
                                    float(peak.properties.get('symmetry', 0.0)),
                                'gaussian_residuals':
                                    float(peak.properties.get(
                                        'gaussian_residuals', 0.0
                                    )),
                                'gaussian_fit_amplitude':
                                    float(peak.properties.get(
                                        'gaussian_fit_params', {}
                                    ).get('amplitude', 0.0)),
                                'gaussian_fit_mean':
                                    float(peak.properties.get(
                                        'gaussian_fit_params', {}
                                    ).get('mean', 0.0)),
                                'gaussian_fit_sigma':
                                    float(peak.properties.get(
                                        'gaussian_fit_params', {}
                                    ).get('sigma', 0.0))
                            } for peak in encoding.chromatogram.peaks]
                        }
                        for encoding in peptide.encodings
                        if encoding.chromatogram and encoding.chromatogram.peaks
                    ),
                    None
                )
            } for peptide in input_data['peptides']]
        }

    def _save_results(self, output_data: Dict[str, Any]) -> None:
        """Save results to a YAML file with '_results' appended to the original
        filename.

        Args:
            output_data (Dict[str, Any]): The output data to save.
        """
        if not self.input_file_path:
            self.logger.warning("No input file path provided. Cannot save results.")
            return

        base, ext = os.path.splitext(self.input_file_path)
        results_file = f"{base}_results{ext}"

        try:
            with open(results_file, 'w') as f:
                yaml.dump(output_data, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Results saved to {results_file}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
            raise

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide output.

        Args:
            input_data (SinglePeptideInput): The input data to process.

        Returns:
            SinglePeptideInput: The processed input data.
        """
        self.logger.info("Outputting results for peptide:" +
            f"{input_data.peptide.sequence_str}")
        input_data.peptide = self._add_retention_time(input_data.peptide)

        output_data = self._format_output({'peptides': [input_data.peptide]})
        self._save_results(output_data)

        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides output.

        Args:
            input_data (PeptideSetInput): The input data to process.

        Returns:
            PeptideSetInput: The processed input data.
        """
        self.logger.info("Outputting results for peptide set:" +
            f"{len(input_data.peptides)} peptides")
        processed_peptides = set()
        for peptide in input_data.peptides:
            processed_peptide = self._add_retention_time(peptide)
            processed_peptides.add(processed_peptide)
        input_data.peptides = processed_peptides

        # Format and save output
        output_data = self._format_output({'peptides': list(processed_peptides)})
        self._save_results(output_data)

        return input_data

    def process_hierarchy(
        self,
        input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides output.

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        def process_node(node):
            node.root = self._add_retention_time(node.root)
            for child in node.children:
                process_node(child)

        self.logger.info(f"Outputting results for peptide hierarchy")
        process_node(input_data.hierarchy)

        # Format and save output
        # Note: For hierarchy, we flatten the structure for output
        all_peptides = []
        def collect_peptides(node):
            all_peptides.append(node.root)
            for child in node.children:
                collect_peptides(child)

        collect_peptides(input_data.hierarchy)
        output_data = self._format_output({'peptides': all_peptides})
        self._save_results(output_data)

        return input_data
