"""
Detector de padrões arquiteturais. Lógica pura.
(todos os dados estão em patterns_config.py)
"""

from typing import Any

from tools.base_tool import Tool

from .classifiers import assess_complexity, classify_architecture_type
from .models import ArchitectureReport, DetectedPattern, PatternConfig
from .patterns_config import (
    BACKEND_STANDARD,
    BASIC_LAYERED,
    CLEAN_ARCHITECTURE,
    DDD,
    EVENT_DRIVEN,
    FEATURE_BASED,
    FRAMEWORK_INDICATORS,
    FRONTEND_STANDARD,
    HEXAGONAL,
    MICROSERVICES,
    MONOREPO,
    MVC,
    PATTERN_RECOMMENDATIONS,
    REPOSITORY_PATTERN,
    SIMPLE_MODULAR,
)

MIN_CONFIDENCE = 0.3

# Padrões que usam a lógica genérica (dir_weights + file_keywords)
_GENERIC_PATTERNS: list[PatternConfig] = [
    SIMPLE_MODULAR,
    FEATURE_BASED,
    BASIC_LAYERED,
    FRONTEND_STANDARD,
    BACKEND_STANDARD,
    MVC,
    CLEAN_ARCHITECTURE,
    DDD,
    HEXAGONAL,
    MONOREPO,
]


class ArchitectureDetectorTool(Tool):
    """
    Detecta padrões arquiteturais no projeto.

    Analisa estrutura de diretórios, nomes de arquivos e organização
    do código para identificar padrões desde estruturas simples até
    arquiteturas enterprise. Retorna confiança e evidências da detecção.
    """

    @property
    def name(self) -> str:
        return "architecture_detector"

    @property
    def description(self) -> str:
        return (
            "Detecta padrões arquiteturais no projeto, desde estruturas simples "
            "até padrões complexos. Identifica: estruturas modulares, MVC, Clean "
            "Architecture, Microservices, Repository Pattern, DDD, Event-Driven, "
            "feature-based e padrões específicos de frameworks. "
            "Retorna confiança da detecção e evidências encontradas."
        )

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_structure": {
                    "type": "object",
                    "description": "Estrutura de arquivos do projeto {tipo: [paths]}",
                },
                "file_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de nomes de arquivos no projeto",
                },
                "directory_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de nomes de diretórios",
                },
            },
            "required": ["file_structure"],
        }

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        file_structure: dict = input_data["file_structure"]
        file_names: list[str] = input_data.get("file_names", [])
        dir_names: list[str] = input_data.get("directory_names", [])

        # Strings de busca pré-computadas
        dirs_lower  = [d.lower() for d in dir_names]
        files_lower = [f.lower() for f in file_names]
        struct_str  = " ".join(str(k).lower() for k in file_structure)

        patterns: list[DetectedPattern] = []

        # ── Padrões com lógica genérica ──────────────────────────────────────
        for cfg in _GENERIC_PATTERNS:
            result = self._detect_generic(cfg, dirs_lower, files_lower)
            if result:
                patterns.append(result)

        # ── Padrões com lógica especializada ─────────────────────────────────
        for detect_fn in [
            lambda: self._detect_repository(files_lower, struct_str),
            lambda: self._detect_microservices(dirs_lower, struct_str),
            lambda: self._detect_event_driven(files_lower, struct_str),
        ]:
            result = detect_fn()
            if result:
                patterns.append(result)

        patterns.sort(key=lambda p: p.confidence, reverse=True)

        report = ArchitectureReport(
            detected_patterns=patterns,
            primary_pattern=patterns[0] if patterns else None,
            secondary_patterns=patterns[1:4] if len(patterns) > 1 else [],
            architecture_type=classify_architecture_type(patterns),
            complexity_level=assess_complexity(patterns),
            framework_hints=self._detect_frameworks(files_lower, struct_str),
            recommendations=self._build_recommendations(patterns),
        )

        return report.to_dict()

    # ── Detector genérico ────────────────────────────────────────────────────

    def _detect_generic(
        self,
        cfg: PatternConfig,
        dirs_lower: list[str],
        files_lower: list[str],
    ) -> DetectedPattern | None:
        """
        Lógica unificada para padrões baseados em dir_weights + file_keywords.
        Substitui ~10 métodos quase idênticos.
        """
        evidence: list[str] = []
        confidence = 0.0

        # Pontuação por diretórios
        matched_dirs = [
            key for key, weight in cfg.dir_weights.items()
            if any(key in d for d in dirs_lower)
        ]
        if len(matched_dirs) < cfg.min_dir_matches:
            return None

        confidence = sum(cfg.dir_weights[k] for k in matched_dirs)
        evidence.append(f"Diretórios: {', '.join(matched_dirs)}")

        # Bônus por arquivos com keywords
        if cfg.file_keywords:
            matched_files = sum(
                1 for f in files_lower
                if any(kw in f for kw in cfg.file_keywords)
            )
            if matched_files:
                confidence += min(matched_files * 0.05, 0.2)
                evidence.append(f"Arquivos correspondentes: {matched_files}")

        if confidence < cfg.threshold:
            return None

        return DetectedPattern(
            pattern=cfg.name,
            confidence=min(confidence, 1.0),
            evidence=evidence,
            description=cfg.description,
        )

    # ── Detectores especializados ────────────────────────────────────────────

    def _detect_repository(
        self, files_lower: list[str], struct_str: str
    ) -> DetectedPattern | None:
        evidence: list[str] = []
        confidence = 0.0

        repo_files = [f for f in files_lower if "repository" in f]
        if not repo_files:
            return None

        confidence += 0.4 + (0.2 if len(repo_files) >= 3 else 0.0)
        evidence.append(f"{len(repo_files)} repositor{'ies' if len(repo_files) > 1 else 'y'} encontrado(s)")

        interface_files = [
            f for f in files_lower
            if any(p in f for p in ["irepository", "repository_interface", "repositoryinterface", "base_repository"])
        ]
        if interface_files:
            confidence += 0.3
            evidence.append("Interfaces/abstrações de repository encontradas")

        if "repositor" in struct_str:
            confidence += 0.1
            evidence.append("Diretório repositories organizado")

        return DetectedPattern(
            pattern=REPOSITORY_PATTERN.name,
            confidence=min(confidence, 1.0),
            evidence=evidence,
            description=REPOSITORY_PATTERN.description,
        ) if confidence >= MIN_CONFIDENCE else None

    def _detect_microservices(
        self, dirs_lower: list[str], struct_str: str
    ) -> DetectedPattern | None:
        evidence: list[str] = []
        confidence = 0.0

        service_dirs = [d for d in dirs_lower if "service" in d]
        count = len(service_dirs)
        if count >= 2:
            confidence += 0.3 + (0.2 if count >= 3 else 0.0)
            evidence.append(f"{count} serviços identificados")

        container_tools = ["docker-compose", "dockerfile", "kubernetes", "k8s", ".dockerignore"]
        if any(tool in struct_str for tool in container_tools):
            confidence += 0.3
            evidence.append("Configurações de containerização encontradas")

        if any(kw in d for d in dirs_lower for kw in ("gateway", "proxy")):
            confidence += 0.2
            evidence.append("API Gateway/Proxy detectado")

        return DetectedPattern(
            pattern=MICROSERVICES.name,
            confidence=min(confidence, 1.0),
            evidence=evidence,
            description=MICROSERVICES.description,
        ) if confidence >= MIN_CONFIDENCE else None

    def _detect_event_driven(
        self, files_lower: list[str], struct_str: str
    ) -> DetectedPattern | None:
        evidence: list[str] = []
        confidence = 0.0

        event_files = [
            f for f in files_lower
            if any(kw in f for kw in EVENT_DRIVEN.file_keywords)
        ]
        if not event_files:
            return None

        confidence += 0.3 + (0.2 if len(event_files) >= 3 else 0.0)
        evidence.append(f"{len(event_files)} componente(s) de eventos encontrados")

        brokers = ["kafka", "rabbitmq", "redis", "pubsub", "queue", "eventbus", "messagebus"]
        found_brokers = [b for b in brokers if b in struct_str]
        if found_brokers:
            confidence += 0.3
            evidence.append(f"Message brokers: {', '.join(found_brokers)}")

        if "event" in struct_str:
            confidence += 0.2
            evidence.append("Estrutura organizada por eventos")

        return DetectedPattern(
            pattern=EVENT_DRIVEN.name,
            confidence=min(confidence, 1.0),
            evidence=evidence,
            description=EVENT_DRIVEN.description,
        ) if confidence >= MIN_CONFIDENCE else None

    # ── Detecção de frameworks ───────────────────────────────────────────────

    def _detect_frameworks(
        self, files_lower: list[str], struct_str: str
    ) -> dict[str, list[str]]:
        combined = struct_str + " " + " ".join(files_lower)

        result: dict[str, list[str]] = {}
        for category, frameworks in FRAMEWORK_INDICATORS.items():
            detected = [
                name
                for name, indicators in frameworks.items()
                if any(ind in combined for ind in indicators)
            ]
            if detected:
                result[category] = detected

        return result

    # ── Recomendações ────────────────────────────────────────────────────────

    def _build_recommendations(self, patterns: list[DetectedPattern]) -> list[str]:
        if not patterns:
            return [
                "✓ Considere adotar um padrão arquitetural claro para facilitar manutenção",
                "✓ Organize o código em diretórios como src/, utils/, config/",
            ]

        recommendations: list[str] = []
        primary = patterns[0]

        # Confiança do padrão primário
        if primary.confidence < 0.5:
            recommendations.append(
                f"⚠ Padrão '{primary.pattern}' com confiança moderada "
                f"({primary.confidence:.0%}). Considere reforçar a estrutura."
            )
        elif primary.confidence >= 0.8:
            recommendations.append(f"✓ Arquitetura bem definida ({primary.pattern})")

        if len(patterns) > 4:
            recommendations.append(
                "⚠ Múltiplos padrões detectados. Considere consolidar para evitar complexidade."
            )

        # Recomendações específicas por padrão
        for keyword, recs in PATTERN_RECOMMENDATIONS.items():
            if any(keyword in p.pattern for p in patterns):
                recommendations.extend(recs)

        if not any("test" in p.pattern.lower() for p in patterns):
            recommendations.append("⚠ Considere adicionar diretório de testes (tests/, __tests__/)")

        # Deduplicar mantendo ordem
        return list(dict.fromkeys(recommendations)) or ["✓ Arquitetura bem estruturada"]
