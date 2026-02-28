"""
Testes para a DependencyMapperTool.
"""

import pytest

from tools.dependency_mapper import DependencyMapperTool


@pytest.fixture
def mapper() -> DependencyMapperTool:
    return DependencyMapperTool()


def _make_file(path: str, content: str, type_: str = "code") -> dict:
    return {"path": path, "content": content, "type": type_}


@pytest.mark.asyncio
async def test_external_dependencies_from_requirements(mapper: DependencyMapperTool):
    content = "requests==2.31.0\npydantic>=2.0\n# comment\n"
    files = [_make_file("requirements.txt", content, "text")]

    result = await mapper.execute({"files": files, "language": "python"})

    external = result["external_dependencies"]
    assert set(external["production"]) >= {"requests", "pydantic"}
    assert external["total_count"] >= 2


@pytest.mark.asyncio
async def test_internal_dependencies_and_graph_python(mapper: DependencyMapperTool):
    files = [
        _make_file(
            "app/main.py",
            "import app.utils\nfrom app import models\n",
        ),
        _make_file(
            "app/utils.py",
            "from app import models\n",
        ),
        _make_file("app/models.py", "# models\n"),
    ]

    result = await mapper.execute({"files": files, "language": "python"})

    internal = result["internal_dependencies"]
    assert "app/main.py" in internal
    assert any("app.utils" in dep or "app" in dep for dep in internal["app/main.py"])

    metrics = result["metrics"]
    assert metrics["total_internal_dependencies"] >= 1
    assert metrics["most_dependent_module"]["path"] in internal

    graph = result["dependency_graph"]
    assert "main.py" in graph


@pytest.mark.asyncio
async def test_circular_dependencies_detected(mapper: DependencyMapperTool):
    files = [
        _make_file("module_a", "import module_b\n"),
        _make_file("module_b", "import module_a\n"),
    ]

    result = await mapper.execute({"files": files, "language": "python"})

    circular = result["circular_dependencies"]
    assert circular
    cycle = circular[0]
    assert "module_a" in cycle and "module_b" in cycle
    assert len(cycle) >= 3  # ida e volta


@pytest.mark.asyncio
async def test_recommendations_healthy_when_no_issues(mapper: DependencyMapperTool):
    files = [_make_file("app/main.py", "print('hello')\n")]

    result = await mapper.execute({"files": files, "language": "python"})

    recs = result["recommendations"]
    assert any("Estrutura de dependências saudável" in r for r in recs)

