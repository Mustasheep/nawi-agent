# Documentação: settings.py

**Tipo:** Python Configuration Module  
**Linguagem:** Python  
**Propósito:** Configuração centralizada para sistema de documentação automática de código usando modelo Claude

## Visão Geral

Este arquivo define uma classe de configuração que centraliza todos os parâmetros operacionais de um agente de documentação de código. Implementa o padrão de configuração através de dataclass, fornecendo valores padrão para limites de tokens, processamento de arquivos, e integração com a API da Anthropic.

O arquivo estabelece três principais categorias de configuração: parâmetros do modelo de IA, limites de processamento baseados no tipo de documentação, e regras de filtragem de arquivos por extensão e diretório.

## Componentes Principais

### Classe Settings
```python
@dataclass
class Settings:
```

**Configuração do Modelo:**
- `MODEL`: Especifica o modelo Claude ("claude-sonnet-4-20250514")
- `API_URL`: Endpoint da API Anthropic para mensagens
- `ANTHROPIC_VERSION`: Versão da API utilizada

**Limites de Tokens por Contexto:**
- `MAX_TOKENS_SINGLE_FILE`: 6000 tokens para arquivos únicos
- `MAX_TOKENS_SMALL_PROJECT`: 6000 tokens para projetos pequenos  
- `MAX_TOKENS_FULL_PROJECT`: 8000 tokens para projetos completos

**Controle de Processamento:**
- `MAX_FILE_SIZE_BYTES`: Limite de 100KB por arquivo
- `MAX_FILES_PER_TYPE`: Máximo 20 arquivos por categoria
- `MAX_CONTENT_CHARS_PER_FILE`: Truncamento em 2000 caracteres
- Thresholds para classificação automática de projeto (1 arquivo = single, ≤5 = small)

**Filtragem de Conteúdo:**
- `EXCLUDE_DIRS`: Set com diretórios comuns ignorados (.git, __pycache__, node_modules, etc.)
- `EXTENSIONS`: Mapeamento de categorias para extensões suportadas
- `MARKDOWN_IGNORE`: Arquivos markdown específicos excluídos (readme.md)

## Dependências

```python
from dataclasses import dataclass, field
from typing import Dict, Set
```

**Bibliotecas Padrão:**
- `dataclasses`: Para criação de classe de configuração estruturada
- `typing`: Para anotações de tipo (Dict, Set)

## Como Usar

**Importação e Instanciação:**
```python
from config.settings import Settings

# Instância com valores padrão
config = Settings()

# Acesso às configurações
max_tokens = config.MAX_TOKENS_SINGLE_FILE
excluded_dirs = config.EXCLUDE_DIRS
python_extensions = config.EXTENSIONS['python']
```

**Customização de Valores:**
```python
# Override de configurações específicas
custom_settings = Settings(
    MODEL="claude-3-haiku",
    MAX_TOKENS_SINGLE_FILE=4000,
    MAX_FILE_SIZE_BYTES=50_000
)
```

**Verificação de Extensões:**
```python
settings = Settings()
if '.py' in settings.EXTENSIONS['python']:
    # Processar arquivo Python
```

## Notas Técnicas

**Padrão de Design:** Implementa o padrão Configuration Object usando dataclass, proporcionando imutabilidade relativa e valores padrão bem definidos.

**Factory Functions:** Utiliza `field(default_factory=lambda: {...})` para inicializar coleções mutáveis, evitando o problema de objetos mutáveis compartilhados entre instâncias.

**Categorização Inteligente:** O sistema de thresholds (SINGLE_FILE_THRESHOLD, SMALL_PROJECT_THRESHOLD) permite classificação automática do contexto de documentação baseado na quantidade de arquivos.

**Considerações de Performance:** Os limites de tamanho de arquivo e caracteres por arquivo previnem sobrecarga de memória e custos excessivos de API, implementando truncamento preventivo.

**Extensibilidade:** A estrutura de dicionário para extensões permite fácil adição de novas categorias de arquivos sem modificar a lógica core do sistema.