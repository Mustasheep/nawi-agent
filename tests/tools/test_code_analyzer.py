"""
Testes para a CodeAnalyzerTool.
"""

import pytest

from tools.code_analyzer import CodeAnalyzerTool


@pytest.fixture
def analyzer() -> CodeAnalyzerTool:
    return CodeAnalyzerTool()


@pytest.mark.asyncio
async def test_python_basic_structure(analyzer: CodeAnalyzerTool):
    code = """import os

CONSTANT = 1

def foo(x, y):
    \"\"\"Soma dois números.\"\"\"
    return x + y


class Bar:
    \"\"\"Classe de exemplo.\"\"\"

    def method(self, z):
        return z
"""

    result = await analyzer.execute(
        {"code": code, "language": "python", "file_path": "module.py"}
    )

    assert result["language"] == "python"
    assert result["file_path"] == "module.py"

    stats = result["stats"]
    assert stats["total_lines"] == len(code.splitlines())

    structure = result["structure"]
    func_names = [f["name"] for f in structure["functions"]]
    class_names = [c["name"] for c in structure["classes"]]

    assert "foo" in func_names
    assert "Bar" in class_names
    assert any(imp["module"] == "os" for imp in structure["imports"])

    metrics = result["metrics"]
    assert metrics["total_functions"] >= 1
    assert metrics["total_classes"] >= 1
    assert metrics["total_imports"] >= 1


@pytest.mark.asyncio
async def test_python_syntax_error_returns_error_and_stats(analyzer: CodeAnalyzerTool):
    code = "def bad(:\n    pass"

    result = await analyzer.execute({"code": code, "language": "python"})

    assert result["language"] == "python"
    assert "error" in result
    assert "stats" in result
    assert result["stats"]["total_lines"] == len(code.splitlines())


@pytest.mark.asyncio
async def test_javascript_basic_analysis(analyzer: CodeAnalyzerTool):
    code = """import x from 'mod';

class Foo extends Bar {}

function baz() {
  return 42;
}
"""

    result = await analyzer.execute(
        {"code": code, "language": "javascript", "file_path": "index.js"}
    )

    assert result["language"] == "javascript"
    structure = result["structure"]

    assert any(fn["name"] == "baz" for fn in structure["functions"])
    assert any(cls["name"] == "Foo" for cls in structure["classes"])
    assert any(imp["module"] == "mod" for imp in structure["imports"])


@pytest.mark.asyncio
async def test_unsupported_language_returns_error_with_basic_stats(
    analyzer: CodeAnalyzerTool,
):
    code = "print('hello')"

    result = await analyzer.execute({"code": code, "language": "java"})

    assert "error" in result
    assert "basic_stats" in result
    assert result["basic_stats"]["total_lines"] == len(code.splitlines())

