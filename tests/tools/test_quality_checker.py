"""
Testes para a QualityCheckerTool.
"""

import pytest

from tools.quality_checker import QualityCheckerTool


@pytest.fixture
def checker() -> QualityCheckerTool:
    return QualityCheckerTool()


def _make_file(path: str, content: str, language: str = "python") -> dict:
    return {"path": path, "content": content, "language": language}


@pytest.mark.asyncio
async def test_quality_checker_basic_structure(checker: QualityCheckerTool):
    files = [_make_file("src/module.py", "def foo():\n    return 1\n")]

    result = await checker.execute({"files": files})

    assert "overall_quality_score" in result
    assert "quality_grade" in result
    assert "detailed_scores" in result
    assert "recommendations" in result
    assert "summary" in result


@pytest.mark.asyncio
async def test_quality_checker_detects_tests_and_documentation(checker: QualityCheckerTool):
    module_content = '''
"""Módulo de exemplo."""


class BadClass:
    """Classe documentada."""
    pass


def badFunction(x, y):
    """Função documentada."""
    if x > y:
        return x
    return y
'''
    test_content = '''
import pytest

from src.module import badFunction


def test_bad_function():
    assert badFunction(1, 2) == 2
'''

    files = [
        _make_file("src/module.py", module_content, "python"),
        _make_file("tests/test_module.py", test_content, "python"),
    ]

    result = await checker.execute({"files": files})

    detailed = result["detailed_scores"]

    # Documentação deve ter algum nível de cobertura
    doc_score = detailed["documentation"]
    assert doc_score["total_items"] > 0
    assert doc_score["score"] > 0

    # Testes devem ser detectados
    test_score = detailed["testing"]
    assert test_score["has_tests"] is True
    assert test_score["test_files"] >= 1


@pytest.mark.asyncio
async def test_quality_checker_detects_naming_and_complexity_issues(
    checker: QualityCheckerTool,
):
    complex_content = '''
def BadFunction(x, y, z):
    if x > y:
        if y > z:
            if x > z:
                for i in range(10):
                    if i % 2 == 0:
                        while False:
                            pass
    return x + y + z
'''

    files = [_make_file("src/complex.py", complex_content, "python")]

    result = await checker.execute({"files": files})
    detailed = result["detailed_scores"]

    naming = detailed["naming_conventions"]
    assert naming["total_violations"] >= 1

    complexity = detailed["code_complexity"]
    assert complexity["total_functions"] >= 1
    assert complexity["total_complex"] >= 1
    assert complexity["score"] < 100


@pytest.mark.asyncio
async def test_quality_checker_summary_mentions_score(checker: QualityCheckerTool):
    files = [_make_file("src/module.py", "def foo():\n    return 1\n")]

    result = await checker.execute({"files": files})

    summary = result["summary"]
    assert "Score Geral" in summary

