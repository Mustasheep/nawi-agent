"""
Classificadores de tipo e complexidade arquitetural.
"""

from .models import DetectedPattern


# Mapeamento padrão → tipo de arquitetura
_ARCHITECTURE_TYPES: list[tuple[str, str]] = [
    ("Microservices",       "Distributed Architecture"),
    ("Monorepo",            "Monorepo Multi-Project"),
    ("Event-Driven",        "Event-Driven / Reactive Architecture"),
    ("MVC",                 "Traditional MVC Architecture"),
    ("Feature-Based",       "Feature-Based Modular Architecture"),
    ("Frontend Standard",   "Frontend Application Structure"),
    ("Backend Standard",    "Backend API Structure"),
    ("Simple Modular",      "Simple Modular Structure"),
]

_DOMAIN_CENTRIC = {"Clean Architecture", "Hexagonal Architecture", "Domain-Driven Design"}

_COMPLEX_PATTERNS = {"Clean Architecture", "DDD", "Hexagonal", "Microservices", "Event-Driven"}
_SIMPLE_PATTERNS  = {"Simple Modular", "Basic Layered", "Frontend Standard", "Backend Standard"}


def classify_architecture_type(patterns: list[DetectedPattern]) -> str:
    if not patterns:
        return "Arquitetura não identificada"

    # Domain-centric patterns têm prioridade especial
    if any(dc in p.pattern for p in patterns for dc in _DOMAIN_CENTRIC):
        return "Domain-Centric Architecture"

    primary = patterns[0].pattern
    for keyword, label in _ARCHITECTURE_TYPES:
        if keyword in primary:
            return label

    # Detecta layered em qualquer posição
    if any("Layered" in p.pattern for p in patterns):
        return "Layered Architecture"

    return "Custom/Mixed Architecture"


def assess_complexity(patterns: list[DetectedPattern]) -> str:
    if not patterns:
        return "Unknown"

    primary = patterns[0]
    has_complex = any(cp in p.pattern for p in patterns for cp in _COMPLEX_PATTERNS)
    is_simple   = any(sp in primary.pattern for sp in _SIMPLE_PATTERNS)

    if has_complex and primary.confidence > 0.7:
        return "High (Enterprise-level)"
    if has_complex or len(patterns) >= 4:
        return "Medium-High (Structured)"
    if len(patterns) >= 2 and primary.confidence > 0.6:
        return "Medium (Organized)"
    if is_simple:
        return "Low-Medium (Simple & Pragmatic)"
    return "Low (Basic)"
