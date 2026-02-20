"""
Testes do code analyzer

use na pasta raiz o comando:
python -m tests.code_analyzer_test
"""

from tools.code_analyzer import CodeAnalyzerTool
import asyncio

async def test():
    tool = CodeAnalyzerTool()
    
    code = """
def hello(name):
    '''Diz olá'''
    return f"Hello {name}"

class Greeter:
    def greet(self):
        pass
"""
    
    result = await tool.execute({
        "code": code,
        "language": "python"
    })
    
    print("Funções:", result['structure']['functions'])
    print("Classes:", result['structure']['classes'])
    print("Métricas:", result['metrics'])

asyncio.run(test())