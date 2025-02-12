# src/lcseq/core/synthesis_status.py
"""
This module defines the SynthesisStatus enumeration, which represents the possible
states of a peptide synthesis.

Classes:
    SynthesisStatus: Enumeration of possible synthesis validation states.
"""

# Standard library imports
from enum import Enum


class SynthesisStatus(Enum):
    """Enumeration of possible synthesis validation states.

    Attributes:
        UNKNOWN: Initial state before validation
        SUCCESS: Synthesis confirmed successful
        FAILURE: Synthesis confirmed failed
        PENDING: Validation in progress
    """

    UNKNOWN = "unknown"
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
