from tools.quality_checker import QualityCheckerTool
import asyncio

async def test():
    tool = QualityCheckerTool()
    
    files = [
        {
            "path": "test.py",
            "content": """
def func1():
    '''Documented'''
    pass

def func2():  # Not documented
    pass

class MyClass:
    '''Documented class'''
    pass
""",
            "language": "python"
        }
    ]
    
    result = await tool.execute({"files": files})
    
    print(f"Score: {result['overall_quality_score']}")
    print(f"Grade: {result['quality_grade']}")
    print("Recommendations:", result['recommendations'])

asyncio.run(test())