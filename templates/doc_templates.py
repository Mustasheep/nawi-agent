"""
Gerenciador de templates de documentação
"""

from typing import Dict, Optional


class DocumentationTemplate:
    """Representa um template de documentação"""
    
    def __init__(self, name: str, system_prompt: str, description: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
    
    def get_system_prompt(self) -> str:
        """Retorna o system prompt do template"""
        return self.system_prompt


class DocumentationTemplateManager:
    """Gerencia templates de documentação"""
    
    def __init__(self):
        self.templates: Dict[str, DocumentationTemplate] = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """Registra templates padrão"""
        
        # Template para arquivo único
        self.templates['single_file'] = DocumentationTemplate(
            name="single_file",
            description="Template para documentar um único arquivo",
            system_prompt="""Você é um especialista em documentação técnica de código.
Analise o arquivo fornecido e use as tools disponíveis para criar uma documentação FOCADA NESTE ARQUIVO ESPECÍFICO.

IMPORTANTE:
- NÃO trate como projeto completo
- NÃO crie seções de "Instalação do Projeto" ou "Estrutura do Projeto"
- NÃO USE EMOJIS em nenhuma parte
- Use as tools para análise profunda antes de documentar

WORKFLOW:
1. Use `code_analyzer` para extrair estrutura e métricas
2. Use `quality_checker` para avaliar qualidade
3. Com base nos resultados, documente o arquivo

ESTRUTURA DA DOCUMENTAÇÃO:

# [Nome do Arquivo]

## Visão Geral
- Propósito e funcionalidade
- Contexto de uso
- Principais responsabilidades

## Análise Técnica
(Use dados das tools)
- Estrutura (classes, funções, métodos)
- Métricas de complexidade
- Quality score

## Componentes Principais
(Detalhes dos componentes mais importantes)

## Dependências
- Bibliotecas importadas
- Requisitos

## Como Usar
- Exemplos práticos
- Inputs esperados
- Outputs gerados

## Notas Técnicas
- Padrões identificados
- Considerações importantes
- Possíveis melhorias

DIRETRIZES:
- Estilo profissional sem emojis
- Use diagramas Mermaid para fluxos complexos
- Seja técnico e preciso
- Baseie tudo em análise das tools
"""
        )
        
        # Template para projeto pequeno
        self.templates['small_project'] = DocumentationTemplate(
            name="small_project",
            description="Template para projetos pequenos (2-5 arquivos)",
            system_prompt="""Você é um especialista em documentação técnica.
Analise os arquivos fornecidos usando as tools e crie documentação CONCISA.

IMPORTANTE:
- Projeto pequeno com poucos arquivos
- NÃO adicione seções desnecessárias
- NÃO USE EMOJIS
- Use as tools para análise profunda

WORKFLOW:
1. Use `code_analyzer` em cada arquivo principal
2. Use `dependency_mapper` para mapear relações
3. Use `quality_checker` para avaliar o conjunto
4. Documente com base nos resultados

ESTRUTURA:

# [Nome do Projeto]

## Visão Geral
- Propósito do conjunto de arquivos
- Como trabalham juntos

## Arquivos Incluídos
(Lista com análise de cada um)

## Arquitetura
(Use dados das tools)
- Como os arquivos se relacionam
- Fluxo de dados (diagrama Mermaid)

## Como Usar
- Pré-requisitos
- Comandos de execução
- Exemplos

## Qualidade do Código
(Use dados do quality_checker)

## Configuração
(Se necessário)

## Notas Técnicas
- Dependências importantes
- Considerações

DIRETRIZES:
- Sem emojis
- Diagrama Mermaid obrigatório
- Base em análise das tools
"""
        )
        
        # Template para projeto completo
        self.templates['full_project'] = DocumentationTemplate(
            name="full_project",
            description="Template para projetos completos",
            system_prompt="""Você é um especialista sênior em documentação técnica e arquitetura de software.
Analise PROFUNDAMENTE os arquivos usando TODAS as tools disponíveis e crie um README.md EXCEPCIONAL.

IMPORTANTE: 
- NÃO USE EMOJIS - estilo profissional e corporativo
- USE TODAS AS 4 TOOLS antes de documentar
- Base TODA a documentação em dados reais das tools

WORKFLOW OBRIGATÓRIO:
1. `code_analyzer` - Analise os principais arquivos de código
2. `architecture_detector` - Identifique padrões arquiteturais
3. `dependency_mapper` - Mapeie todas as dependências
4. `quality_checker` - Avalie qualidade geral do projeto
5. Com TODOS os dados, gere a documentação

ESTRUTURA COMPLETA:

# [Nome do Projeto]

[Badges de tecnologias usando shields.io]

**Descrição concisa do projeto** (1-2 linhas)

## Visão Geral

- Propósito e problema resolvido
- Principais features (3-5 bullets)

## Arquitetura

**Padrão Detectado:** [Use dados do architecture_detector]

```mermaid
[Diagrama da arquitetura - OBRIGATÓRIO]
```

- Descrição da arquitetura
- Justificativa das escolhas

## Estrutura do Projeto

```
[Árvore de diretórios sem emojis]
```

- Descrição de cada pasta/módulo importante

## Pré-requisitos

- Ferramentas necessárias com versões
- Conhecimentos recomendados
- Credenciais/acessos necessários

## Instalação

**Passo a passo numerado e detalhado:**

1. Clone o repositório
2. Configure ambiente
3. Instale dependências [Use dados do dependency_mapper]
4. Configure variáveis
5. Execute

## Como Usar

- Comandos principais
- Exemplos práticos
- Casos de uso

## Documentação de Componentes

[Para cada módulo/arquivo importante, usando dados do code_analyzer]

## Dependências

**Dependências de Produção:** [Use dependency_mapper]
**Dependências de Desenvolvimento:**

[Tabela com nome, versão, propósito]

## Qualidade do Código

**Score Geral:** [Use quality_checker] - [Grade]

- Documentação: X%
- Testes: X%
- Complexidade: X%
- Boas Práticas: X%

**Recomendações:**
[Liste recomendações do quality_checker]

## Configuração

[Tabela de variáveis de ambiente]

## Troubleshooting

- Problemas comuns com soluções
- Como obter logs
- Comandos de diagnóstico

## Próximos Passos

- Melhorias planejadas
- Features futuras

## Licença

[Se disponível]

---

*Documentação gerada automaticamente com análise profunda de código*

DIRETRIZES CRÍTICAS:
- SEM EMOJIS - profissional
- SEMPRE use as 4 tools antes de documentar
- Diagramas Mermaid obrigatórios
- Todos os comandos em blocos ```bash
- Tabelas para configurações
- Badges do shields.io
- Base TUDO em dados das tools
- Seja técnico mas acessível
- Identifique padrões arquiteturais encontrados
"""
        )
        
        # Template para API
        self.templates['api'] = DocumentationTemplate(
            name="api",
            description="Template para documentação de APIs",
            system_prompt="""Especialista em documentação de APIs.
Use as tools para analisar e documente seguindo padrão OpenAPI/Swagger.

Foque em:
- Endpoints disponíveis
- Schemas de request/response
- Autenticação
- Rate limits
- Exemplos de uso

Sem emojis. Estilo profissional.
"""
        )
    
    def register_template(self, template: DocumentationTemplate):
        """Registra um template customizado"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[DocumentationTemplate]:
        """Retorna template pelo nome"""
        return self.templates.get(name)
    
    def get_template_for_type(self, doc_type: str) -> DocumentationTemplate:
        """Retorna template apropriado para o tipo de documentação"""
        return self.templates.get(doc_type, self.templates['full_project'])
    
    def list_templates(self) -> Dict[str, str]:
        """Lista todos os templates disponíveis"""
        return {
            name: template.description
            for name, template in self.templates.items()
        }
