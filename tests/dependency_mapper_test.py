"""
Testes do dependency mapper

use na pasta raiz o comando:
python -m tests.dependency_mapper_test
"""

from tools.dependency_mapper import DependencyMapperTool
import asyncio

async def test():
    tool = DependencyMapperTool()
    
    files = [
        {
            "path": "requirements.txt",
            "content": "fastapi>=0.100.0\npydantic>=2.0.0",
            "type": "text"
        },
        {
            "path": "src/main.py",
            "content": "import fastapi\nfrom src import models",
            "type": "python"
        },
        {
            "path": "src/models.py",
            "content": "from pydantic import BaseModel",
            "type": "python"
        }
    ]
    
    result = await tool.execute({
        "files": files,
        "language": "python"
    })
    
    print("External deps:", result['external_dependencies'])
    print("Internal deps:", result['internal_dependencies'])
    print("Circular:", result['circular_dependencies'])

asyncio.run(test())