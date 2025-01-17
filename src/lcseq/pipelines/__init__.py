# src/lcseq/pipelines/__init__.py
# from src.lcseq.pipelines.CC import CC
# from src.lcseq.pipelines.gpp import GPP
from src.lcseq.pipelines.tpipe import TPipe
from src.lcseq.pipelines.standard import StandardPipe

__all__ = [
    # "CC",
    # "GPP",
    "TPipe",
    "StandardPipe"
]
