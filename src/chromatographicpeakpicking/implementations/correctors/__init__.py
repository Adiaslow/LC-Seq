# src/chromatographicpeakpicking/implementations/correctors/__init__.py

"""
Initialization module for baseline correctors.
"""
from .aals import AALSCorrector
from .swm import SWMCorrector

__all__ = [
    "AALSCorrector",
    "SWMCorrector",
]
