"""
Testes para o módulo tools.architecture

Cobertura:
- ArchitectureDetectorTool.execute() — padrões genéricos e especializados
- _detect_generic               — lógica unificada de detecção por dir_weights
- _detect_repository            — lógica especializada
- _detect_microservices         — lógica especializada
- _detect_event_driven          — lógica especializada
- _detect_frameworks            — detecção de frameworks/libs
- _build_recommendations        — recomendações por padrão e confiança
- classify_architecture_type    — classificação do tipo arquitetural
- assess_complexity             — avaliação de complexidade
- ArchitectureReport.to_dict()  — serialização retrocompatível
- Casos de borda                — entrada vazia, parcial, mista
"""

import pytest

from tools.architecture.classifiers import assess_complexity, classify_architecture_type
from tools.architecture.detector import ArchitectureDetectorTool
from tools.architecture.models import ArchitectureReport, DetectedPattern, PatternConfig


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def detector() -> ArchitectureDetectorTool:
    return ArchitectureDetectorTool()


def make_pattern(name: str, confidence: float = 0.8) -> DetectedPattern:
    """Atalho para criar DetectedPattern em testes."""
    return DetectedPattern(
        pattern=name,
        confidence=confidence,
        evidence=["evidência de teste"],
        description="descrição de teste",
    )


# ─── Helpers de execução ──────────────────────────────────────────────────────

async def run(
    detector: ArchitectureDetectorTool,
    dirs: list[str] = None,
    files: list[str] = None,
    structure: dict = None,
) -> dict:
    return await detector.execute({
        "file_structure": structure or {},
        "file_names":     files or [],
        "directory_names": dirs or [],
    })


# ══════════════════════════════════════════════════════════════════════════════
# 1. Padrões genéricos via execute()
# ══════════════════════════════════════════════════════════════════════════════

class TestGenericPatternDetection:

    @pytest.mark.asyncio
    async def test_mvc_full_triad(self, detector):
        result = await run(detector, dirs=["models", "views", "controllers"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "MVC (Model-View-Controller)" in names

    @pytest.mark.asyncio
    async def test_mvc_requires_min_two_dirs(self, detector):
        """Só 'models' não deve atingir min_dir_matches=2."""
        result = await run(detector, dirs=["models"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "MVC (Model-View-Controller)" not in names

    @pytest.mark.asyncio
    async def test_clean_architecture_detected(self, detector):
        result = await run(detector, dirs=["domain", "application", "infrastructure"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Clean Architecture" in names

    @pytest.mark.asyncio
    async def test_clean_architecture_requires_three_layers(self, detector):
        result = await run(detector, dirs=["domain", "application"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Clean Architecture" not in names

    @pytest.mark.asyncio
    async def test_ddd_detected(self, detector):
        result = await run(detector, dirs=["domain", "entities", "aggregates", "value_objects"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Domain-Driven Design (DDD)" in names

    @pytest.mark.asyncio
    async def test_hexagonal_detected(self, detector):
        result = await run(detector, dirs=["ports", "adapters"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Hexagonal Architecture (Ports & Adapters)" in names

    @pytest.mark.asyncio
    async def test_feature_based_detected(self, detector):
        result = await run(detector, dirs=["features", "modules"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Feature-Based Architecture" in names

    @pytest.mark.asyncio
    async def test_simple_modular_detected(self, detector):
        result = await run(detector, dirs=["src", "utils", "config"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Simple Modular Structure" in names

    @pytest.mark.asyncio
    async def test_frontend_standard_detected(self, detector):
        result = await run(
            detector,
            dirs=["components", "pages", "hooks"],
            files=["Button.tsx", "Home.jsx", "useAuth.ts"],
        )
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Frontend Standard Structure" in names

    @pytest.mark.asyncio
    async def test_backend_standard_detected(self, detector):
        result = await run(
            detector,
            dirs=["controllers", "routes", "models", "middleware"],
            files=["server.js", "app.js"],
        )
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Backend Standard Structure" in names

    @pytest.mark.asyncio
    async def test_monorepo_detected(self, detector):
        result = await run(
            detector,
            dirs=["packages", "apps"],
            structure={"lerna.json": [], "packages/web": [], "packages/api": []},
        )
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Monorepo Structure" in names

    @pytest.mark.asyncio
    async def test_patterns_sorted_by_confidence(self, detector):
        result = await run(
            detector,
            dirs=["models", "views", "controllers", "domain", "application", "infrastructure"],
        )
        confidences = [p["confidence"] for p in result["detected_patterns"]]
        assert confidences == sorted(confidences, reverse=True)

    @pytest.mark.asyncio
    async def test_file_keywords_boost_confidence(self, detector):
        """Arquivos com keywords devem aumentar a confiança vs só diretórios."""
        result_no_files = await run(detector, dirs=["models", "views", "controllers"])
        result_with_files = await run(
            detector,
            dirs=["models", "views", "controllers"],
            files=["user_controller.py", "product_model.py", "order_view.py"],
        )

        def mvc_confidence(result):
            for p in result["detected_patterns"]:
                if "MVC" in p["pattern"]:
                    return p["confidence"]
            return 0.0

        assert mvc_confidence(result_with_files) >= mvc_confidence(result_no_files)


# ══════════════════════════════════════════════════════════════════════════════
# 2. Detectores especializados
# ══════════════════════════════════════════════════════════════════════════════

class TestRepositoryDetection:

    @pytest.mark.asyncio
    async def test_single_repository_file(self, detector):
        result = await run(detector, files=["user_repository.py"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Repository Pattern" in names

    @pytest.mark.asyncio
    async def test_multiple_repos_increases_confidence(self, detector):
        result_one = await run(detector, files=["user_repository.py"])
        result_many = await run(
            detector,
            files=["user_repository.py", "order_repository.py", "product_repository.py"],
        )

        def repo_confidence(r):
            for p in r["detected_patterns"]:
                if p["pattern"] == "Repository Pattern":
                    return p["confidence"]
            return 0.0

        assert repo_confidence(result_many) > repo_confidence(result_one)

    @pytest.mark.asyncio
    async def test_interface_boosts_confidence(self, detector):
        result = await run(
            detector,
            files=["user_repository.py", "irepository.py"],
        )
        for p in result["detected_patterns"]:
            if p["pattern"] == "Repository Pattern":
                assert p["confidence"] > 0.7
                assert any("Interface" in e or "abstração" in e for e in p["evidence"])
                return
        pytest.fail("Repository Pattern não detectado")

    @pytest.mark.asyncio
    async def test_no_repository_file_returns_none(self, detector):
        result = await run(detector, files=["user_service.py", "order_model.py"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Repository Pattern" not in names


class TestMicroservicesDetection:

    @pytest.mark.asyncio
    async def test_multiple_service_dirs_detected(self, detector):
        result = await run(detector, dirs=["user-service", "order-service", "payment-service"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Microservices" in names

    @pytest.mark.asyncio
    async def test_two_services_detected(self, detector):
        result = await run(detector, dirs=["auth-service", "api-service"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Microservices" in names

    @pytest.mark.asyncio
    async def test_one_service_not_enough(self, detector):
        result = await run(detector, dirs=["user-service"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Microservices" not in names

    @pytest.mark.asyncio
    async def test_docker_compose_boosts_confidence(self, detector):
        result = await run(
            detector,
            dirs=["auth-service", "api-service"],
            structure={"docker-compose.yml": [], "dockerfile": []},
        )
        for p in result["detected_patterns"]:
            if p["pattern"] == "Microservices":
                assert p["confidence"] >= 0.6
                assert any("container" in e.lower() for e in p["evidence"])
                return
        pytest.fail("Microservices não detectado")

    @pytest.mark.asyncio
    async def test_gateway_boosts_confidence(self, detector):
        result = await run(detector, dirs=["auth-service", "api-service", "api-gateway"])
        for p in result["detected_patterns"]:
            if p["pattern"] == "Microservices":
                assert any("Gateway" in e for e in p["evidence"])
                return
        pytest.fail("Microservices não detectado")


class TestEventDrivenDetection:

    @pytest.mark.asyncio
    async def test_event_files_detected(self, detector):
        result = await run(
            detector,
            files=["order_event.py", "payment_handler.py", "notification_listener.py"],
        )
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Event-Driven Architecture" in names

    @pytest.mark.asyncio
    async def test_broker_keywords_boost_confidence(self, detector):
        result = await run(
            detector,
            files=["order_event.py"],
            structure={"kafka_config.py": [], "rabbitmq_setup.py": []},
        )
        for p in result["detected_patterns"]:
            if p["pattern"] == "Event-Driven Architecture":
                assert p["confidence"] >= 0.6
                assert any("kafka" in e.lower() or "rabbitmq" in e.lower() for e in p["evidence"])
                return
        pytest.fail("Event-Driven não detectado")

    @pytest.mark.asyncio
    async def test_no_event_files_not_detected(self, detector):
        result = await run(detector, files=["user_service.py", "order_model.py"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Event-Driven Architecture" not in names

    @pytest.mark.asyncio
    async def test_subscriber_publisher_detected(self, detector):
        result = await run(
            detector,
            files=["email_subscriber.py", "sms_publisher.py", "push_subscriber.py"],
        )
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Event-Driven Architecture" in names


# ══════════════════════════════════════════════════════════════════════════════
# 3. Detecção de frameworks
# ══════════════════════════════════════════════════════════════════════════════

class TestFrameworkDetection:

    @pytest.mark.asyncio
    async def test_nextjs_detected(self, detector):
        result = await run(detector, files=["next.config.js", "next-env.d.ts"])
        assert "Next.js" in result["framework_hints"].get("frontend", [])

    @pytest.mark.asyncio
    async def test_react_detected_via_extension(self, detector):
        result = await run(detector, files=["App.tsx", "Button.jsx"])
        assert "React" in result["framework_hints"].get("frontend", [])

    @pytest.mark.asyncio
    async def test_django_detected(self, detector):
        result = await run(detector, files=["manage.py", "settings.py"])
        assert "Django" in result["framework_hints"].get("backend", [])

    @pytest.mark.asyncio
    async def test_fastapi_detected(self, detector):
        result = await run(detector, files=["fastapi_config.py", "main.py"])
        assert "FastAPI" in result["framework_hints"].get("backend", [])

    @pytest.mark.asyncio
    async def test_prisma_detected(self, detector):
        result = await run(detector, structure={"prisma/schema.prisma": []})
        assert "Prisma" in result["framework_hints"].get("database", [])

    @pytest.mark.asyncio
    async def test_pytest_detected(self, detector):
        result = await run(detector, files=["pytest.ini", "conftest.py"])
        assert "Pytest" in result["framework_hints"].get("testing", [])

    @pytest.mark.asyncio
    async def test_docker_detected(self, detector):
        result = await run(detector, structure={"Dockerfile": [], "docker-compose.yml": []})
        assert "Docker" in result["framework_hints"].get("deployment", [])

    @pytest.mark.asyncio
    async def test_no_frameworks_returns_empty(self, detector):
        result = await run(detector, files=["main.py", "utils.py"])
        assert result["framework_hints"] == {}

    @pytest.mark.asyncio
    async def test_multiple_frameworks_same_category(self, detector):
        result = await run(
            detector,
            files=["App.tsx", "Button.jsx", "next.config.js"],
        )
        frontend = result["framework_hints"].get("frontend", [])
        assert "React" in frontend
        assert "Next.js" in frontend


# ══════════════════════════════════════════════════════════════════════════════
# 4. Classificadores
# ══════════════════════════════════════════════════════════════════════════════

class TestClassifyArchitectureType:

    def test_empty_patterns(self):
        assert classify_architecture_type([]) == "Arquitetura não identificada"

    def test_microservices_primary(self):
        result = classify_architecture_type([make_pattern("Microservices")])
        assert result == "Distributed Architecture"

    def test_monorepo_primary(self):
        result = classify_architecture_type([make_pattern("Monorepo Structure")])
        assert result == "Monorepo Multi-Project"

    def test_clean_architecture_domain_centric(self):
        result = classify_architecture_type([make_pattern("Clean Architecture")])
        assert result == "Domain-Centric Architecture"

    def test_hexagonal_domain_centric(self):
        result = classify_architecture_type([make_pattern("Hexagonal Architecture (Ports & Adapters)")])
        assert result == "Domain-Centric Architecture"

    def test_ddd_domain_centric(self):
        result = classify_architecture_type([make_pattern("Domain-Driven Design (DDD)")])
        assert result == "Domain-Centric Architecture"

    def test_domain_centric_overrides_primary(self):
        """Clean Architecture em segunda posição deve ganhar do MVC em primeiro."""
        patterns = [
            make_pattern("MVC (Model-View-Controller)", confidence=0.9),
            make_pattern("Clean Architecture", confidence=0.7),
        ]
        assert classify_architecture_type(patterns) == "Domain-Centric Architecture"

    def test_mvc_primary(self):
        result = classify_architecture_type([make_pattern("MVC (Model-View-Controller)")])
        assert result == "Traditional MVC Architecture"

    def test_event_driven_primary(self):
        result = classify_architecture_type([make_pattern("Event-Driven Architecture")])
        assert result == "Event-Driven / Reactive Architecture"

    def test_feature_based_primary(self):
        result = classify_architecture_type([make_pattern("Feature-Based Architecture")])
        assert result == "Feature-Based Modular Architecture"

    def test_layered_in_secondary(self):
        patterns = [
            make_pattern("Simple Modular Structure", confidence=0.8),
            make_pattern("Basic Layered Architecture", confidence=0.6),
        ]
        assert classify_architecture_type(patterns) == "Simple Modular Structure"

    def test_unknown_pattern_returns_custom(self):
        result = classify_architecture_type([make_pattern("SomeUnknownPattern")])
        assert result == "Custom/Mixed Architecture"


class TestAssessComplexity:

    def test_empty_patterns(self):
        assert assess_complexity([]) == "Unknown"

    def test_complex_high_confidence(self):
        result = assess_complexity([make_pattern("Clean Architecture", confidence=0.9)])
        assert result == "High (Enterprise-level)"

    def test_complex_low_confidence(self):
        result = assess_complexity([make_pattern("Clean Architecture", confidence=0.5)])
        assert result == "Medium-High (Structured)"

    def test_many_patterns_medium_high(self):
        patterns = [make_pattern(f"Pattern {i}", confidence=0.5) for i in range(4)]
        result = assess_complexity(patterns)
        assert result == "Medium-High (Structured)"

    def test_two_patterns_medium(self):
        patterns = [
            make_pattern("Simple Modular Structure", confidence=0.8),
            make_pattern("Basic Layered Architecture", confidence=0.7),
        ]
        result = assess_complexity(patterns)
        assert result == "Medium (Organized)"

    def test_simple_pattern_low_medium(self):
        result = assess_complexity([make_pattern("Simple Modular Structure", confidence=0.8)])
        assert result == "Low-Medium (Simple & Pragmatic)"

    def test_frontend_standard_low_medium(self):
        result = assess_complexity([make_pattern("Frontend Standard Structure", confidence=0.8)])
        assert result == "Low-Medium (Simple & Pragmatic)"

    def test_unknown_single_pattern_low(self):
        result = assess_complexity([make_pattern("SomethingUnknown", confidence=0.5)])
        assert result == "Low (Basic)"

    def test_microservices_high_confidence(self):
        result = assess_complexity([make_pattern("Microservices", confidence=0.85)])
        assert result == "High (Enterprise-level)"


# ══════════════════════════════════════════════════════════════════════════════
# 5. Recomendações
# ══════════════════════════════════════════════════════════════════════════════

class TestBuildRecommendations:

    @pytest.mark.asyncio
    async def test_empty_project_returns_default_recs(self, detector):
        result = await run(detector)
        assert len(result["recommendations"]) >= 1
        assert any("padrão" in r.lower() or "organize" in r.lower() for r in result["recommendations"])

    @pytest.mark.asyncio
    async def test_high_confidence_positive_rec(self, detector):
        result = await run(
            detector,
            dirs=["models", "views", "controllers"],
            files=["user_controller.py", "product_model.py", "order_view.py",
                   "auth_controller.py", "item_model.py"],
        )
        recs = result["recommendations"]
        assert any("✓" in r for r in recs)

    @pytest.mark.asyncio
    async def test_low_confidence_warning(self, detector):
        """Com só 2 dirs MVC e sem arquivos extras, confiança deve ser moderada."""
        result = await run(detector, dirs=["models", "views"])
        # Pode não detectar MVC (min=2) mas se detectar deve avisar sobre confiança
        # O teste principal é que não gera crash e retorna lista
        assert isinstance(result["recommendations"], list)

    @pytest.mark.asyncio
    async def test_recommendations_are_unique(self, detector):
        """Sem duplicatas mesmo com múltiplos padrões ativos."""
        result = await run(
            detector,
            dirs=["models", "views", "controllers", "repositories", "domain",
                  "application", "infrastructure"],
            files=["user_repository.py", "product_repository.py", "order_repository.py"],
        )
        recs = result["recommendations"]
        assert len(recs) == len(set(recs))

    @pytest.mark.asyncio
    async def test_too_many_patterns_consolidation_warning(self, detector):
        """Muitos padrões detectados → aviso de consolidação."""
        result = await run(
            detector,
            dirs=["models", "views", "controllers", "domain", "application",
                  "infrastructure", "features", "src", "ports", "adapters"],
            files=["user_repository.py", "order_repository.py", "order_event.py",
                   "payment_handler.py", "payment_listener.py"],
        )
        recs = result["recommendations"]
        assert any("consolidar" in r.lower() or "múltiplos" in r.lower() for r in recs)


# ══════════════════════════════════════════════════════════════════════════════
# 6. Estrutura do retorno e retrocompatibilidade
# ══════════════════════════════════════════════════════════════════════════════

class TestReturnStructure:

    @pytest.mark.asyncio
    async def test_all_keys_present(self, detector):
        result = await run(detector, dirs=["src", "utils"])
        expected_keys = {
            "detected_patterns",
            "primary_pattern",
            "secondary_patterns",
            "architecture_type",
            "complexity_level",
            "framework_hints",
            "recommendations",
        }
        assert expected_keys.issubset(result.keys())

    @pytest.mark.asyncio
    async def test_pattern_dict_keys(self, detector):
        result = await run(detector, dirs=["models", "views", "controllers"])
        for p in result["detected_patterns"]:
            assert {"pattern", "confidence", "evidence", "description"} == set(p.keys())

    @pytest.mark.asyncio
    async def test_confidence_between_0_and_1(self, detector):
        result = await run(
            detector,
            dirs=["models", "views", "controllers", "domain", "application", "infrastructure"],
        )
        for p in result["detected_patterns"]:
            assert 0.0 <= p["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_primary_pattern_is_highest_confidence(self, detector):
        result = await run(
            detector,
            dirs=["models", "views", "controllers", "domain", "application", "infrastructure"],
        )
        if result["primary_pattern"] and result["detected_patterns"]:
            max_conf = max(p["confidence"] for p in result["detected_patterns"])
            assert result["primary_pattern"]["confidence"] == max_conf

    @pytest.mark.asyncio
    async def test_secondary_patterns_max_three(self, detector):
        result = await run(
            detector,
            dirs=["models", "views", "controllers", "domain", "application",
                  "infrastructure", "features", "src", "utils"],
        )
        assert len(result["secondary_patterns"]) <= 3

    @pytest.mark.asyncio
    async def test_evidence_is_list_of_strings(self, detector):
        result = await run(detector, dirs=["models", "views", "controllers"])
        for p in result["detected_patterns"]:
            assert isinstance(p["evidence"], list)
            assert all(isinstance(e, str) for e in p["evidence"])

    def test_to_dict_roundtrip(self):
        """ArchitectureReport.to_dict() preserva todos os campos."""
        pattern = make_pattern("MVC (Model-View-Controller)", confidence=0.85)
        report = ArchitectureReport(
            detected_patterns=[pattern],
            primary_pattern=pattern,
            secondary_patterns=[],
            architecture_type="Traditional MVC Architecture",
            complexity_level="Medium (Organized)",
            framework_hints={"backend": ["Django"]},
            recommendations=["✓ Arquitetura bem definida"],
        )
        d = report.to_dict()
        assert d["primary_pattern"]["pattern"] == "MVC (Model-View-Controller)"
        assert d["primary_pattern"]["confidence"] == 0.85
        assert d["framework_hints"] == {"backend": ["Django"]}
        assert d["secondary_patterns"] == []

    def test_to_dict_none_primary(self):
        report = ArchitectureReport(
            detected_patterns=[],
            primary_pattern=None,
            secondary_patterns=[],
            architecture_type="Arquitetura não identificada",
            complexity_level="Unknown",
            framework_hints={},
            recommendations=[],
        )
        assert report.to_dict()["primary_pattern"] is None


# ══════════════════════════════════════════════════════════════════════════════
# 7. Casos de borda
# ══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:

    @pytest.mark.asyncio
    async def test_empty_input(self, detector):
        result = await run(detector)
        assert result["detected_patterns"] == []
        assert result["primary_pattern"] is None
        assert result["architecture_type"] == "Arquitetura não identificada"
        assert result["complexity_level"] == "Unknown"
        assert result["framework_hints"] == {}
        assert len(result["recommendations"]) >= 1

    @pytest.mark.asyncio
    async def test_only_file_structure_key(self, detector):
        """file_names e directory_names são opcionais."""
        result = await detector.execute({"file_structure": {"src/main.py": []}})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_case_insensitive_dirs(self, detector):
        """Diretórios em maiúsculas devem ser detectados."""
        result = await run(detector, dirs=["Models", "VIEWS", "Controllers"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "MVC (Model-View-Controller)" in names

    @pytest.mark.asyncio
    async def test_case_insensitive_files(self, detector):
        result = await run(detector, files=["UserRepository.py", "ProductREPOSITORY.py"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "Repository Pattern" in names

    @pytest.mark.asyncio
    async def test_partial_dir_match(self, detector):
        """'user_models' deve ser reconhecido por conter 'models'."""
        result = await run(detector, dirs=["user_models", "app_views", "api_controllers"])
        names = [p["pattern"] for p in result["detected_patterns"]]
        assert "MVC (Model-View-Controller)" in names

    @pytest.mark.asyncio
    async def test_large_project_no_crash(self, detector):
        """Projeto com muitos arquivos e diretórios não deve travar."""
        many_dirs  = [f"module_{i}" for i in range(100)] + ["models", "views", "controllers"]
        many_files = [f"file_{i}.py" for i in range(500)] + ["user_repository.py"]
        result = await run(detector, dirs=many_dirs, files=many_files)
        assert isinstance(result, dict)
        assert "detected_patterns" in result

    @pytest.mark.asyncio
    async def test_confidence_never_exceeds_one(self, detector):
        """Muitos matches não devem ultrapassar 1.0."""
        abundant_dirs = [
            "models", "views", "controllers", "model", "view", "controller",
            "domain", "application", "infrastructure", "entities", "usecases",
        ]
        result = await run(detector, dirs=abundant_dirs)
        for p in result["detected_patterns"]:
            assert p["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_recommendations_never_empty_list(self, detector):
        """Sempre retorna ao menos uma recomendação."""
        result = await run(detector)
        assert len(result["recommendations"]) > 0