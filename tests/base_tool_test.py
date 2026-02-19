from tools.base_tool import Tool

# Testando erro
try:
    tool = Tool()
except TypeError as e:
    print(f"\nErro esperado: {e}")

# Tool para testar
class TestTool(Tool):
    @property
    def name(self): return "test"
    
    @property
    def description(self): return "Test tool"
    
    @property
    def input_schema(self): 
        return {"type": "object", "properties": {}}
    
    async def execute(self, input_data):
        return {"result": "test"}

# Testando acerto
tool = TestTool()
print(f"\nQuando validado: {tool.to_anthropic_format()}")