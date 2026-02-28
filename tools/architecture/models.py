"""
Modelos de dados para o detector de arquitetura
"""

from dataclasses import dataclass, field
from typing import TypedDict


@dataclass
class PatternConfig:
    """Configuração de um padrão arquitetural"""
    name: str
    description: str
    dir_weights: dict[str, float] = field(default_factory=dict)
    file_keywords: list[str] = field(default_factory=list)
    min_dir_matches: int = 1
    threshold: float = 0.3


@dataclass
class DetectedPattern:
    """Resultado de um padrão detectado"""
    pattern: str
    confidence: float
    evidence: list[str]
    description: str


@dataclass
class ArchitectureReport:
    """Relatório completo de arquitetura"""
    detected_patterns: list[DetectedPattern]
    primary_pattern: DetectedPattern | None
    secondary_patterns: list[DetectedPattern]
    architecture_type: str
    complexity_level: str
    framework_hints: dict[str, list[str]]
    recommendations: list[str]

    def to_dict(self) -> dict:
        """Serializa para dict (compatibilidade com retorno anterior)"""
        def pattern_to_dict(p: DetectedPattern) -> dict:
            return {
                "pattern": p.pattern,
                "confidence": p.confidence,
                "evidence": p.evidence,
                "description": p.description,
            }

        return {
            "detected_patterns": [pattern_to_dict(p) for p in self.detected_patterns],
            "primary_pattern": pattern_to_dict(self.primary_pattern) if self.primary_pattern else None,
            "secondary_patterns": [pattern_to_dict(p) for p in self.secondary_patterns],
            "architecture_type": self.architecture_type,
            "complexity_level": self.complexity_level,
            "framework_hints": self.framework_hints,
            "recommendations": self.recommendations,
        }


class FrameworkHints(TypedDict, total=False):
    frontend: list[str]
    backend: list[str]
    database: list[str]
    testing: list[str]
    deployment: list[str]
