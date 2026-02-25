"""
Detector de padrões arquiteturais
"""

from .detector import ArchitectureDetectorTool
from .models import ArchitectureReport, DetectedPattern, PatternConfig

__all__ = [
    "ArchitectureDetectorTool",
    "ArchitectureReport",
    "DetectedPattern",
    "PatternConfig",
]
