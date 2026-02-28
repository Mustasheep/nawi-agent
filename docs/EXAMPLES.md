# Guia de Exemplos Práticos

Este guia mostra exemplos reais de uso do Agente Documentador.

## Exemplo 1: Documentar Script Python Simples

### Cenário
Você tem um script Python que processa CSVs.

### Comando
```bash
python main.py process_data.py -n "Processador de Dados"
```

### O que acontece
1. FileScanner identifica 1 arquivo Python
2. Modo detectado: `single_file`
3. Tools executadas:
   - `code_analyzer` - Extrai funções e estrutura
   - `quality_checker` - Avalia qualidade
4. Documentação gerada focada no arquivo

### Output
```markdown
# Processador de Dados

## Visão Geral
Script para processar arquivos CSV...

## Análise Técnica
- 5 funções encontradas
- Complexidade média: 4.2
- Quality Score: 78/100

## Componentes Principais
### Função: process_csv()
...
```

---

## Exemplo 2: API Flask

### Cenário
Projeto Flask com múltiplos endpoints.

### Comando
```bash
python main.py ./app -n "User Management API" -t api -o docs/API.md -v
```

### Estrutura do Projeto
```
app/
├── __init__.py
├── routes.py
├── models.py
└── utils.py
```

### O que acontece
1. Escaneia diretório `./app`
2. Template API selecionado
3. Tools executadas:
   - `code_analyzer` - Analisa cada arquivo
   - `architecture_detector` - Detecta padrão MVC
   - `dependency_mapper` - Mapeia Flask e extensions
   - `quality_checker` - Avalia API
4. Modo verbose mostra execução de cada tool

### Output
Documentação completa de API com:
- Endpoints documentados
- Schemas de request/response
- Exemplos de uso com curl
- Autenticação
- Rate limiting

---

## Exemplo 3: Projeto Terraform

### Cenário
Infraestrutura como código para AWS.

### Comando
```bash
python main.py ./terraform -n "AWS Infrastructure" -o docs/INFRA.md
```

### Estrutura
```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
└── modules/
    ├── vpc/
    └── ec2/
```

### O que acontece
1. FileScanner categoriza arquivos .tf
2. `architecture_detector` identifica organização modular
3. `dependency_mapper` mapeia recursos e módulos
4. Documentação com:
   - Recursos criados
   - Variáveis necessárias
   - Outputs importantes
   - Diagrama de arquitetura AWS

---

## Exemplo 4: Projeto React

### Cenário
Frontend React com múltiplos componentes.

### Comando
```bash
python main.py ./src/components -n "UI Components Library"
```

### O que acontece
1. Detecta arquivos .jsx/.tsx
2. `code_analyzer` extrai componentes e props
3. `dependency_mapper` mapeia imports entre componentes
4. Documentação com:
   - Catálogo de componentes
   - Props de cada componente
   - Exemplos de uso
   - Hierarquia de componentes (Mermaid)

---

## Exemplo 5: Análise de Qualidade de Projeto Grande

### Cenário
Projeto Python com 50+ arquivos. Você quer saber a qualidade.

### Comando
```bash
python main.py ./src ./tests -v -n "Data Pipeline"
```

### O que acontece
1. Escaneia até 20 arquivos por tipo
2. **Todas as 4 tools são executadas:**
   - `code_analyzer` - Análise de cada módulo
   - `architecture_detector` - Detecta Clean Architecture
   - `dependency_mapper` - Grafo completo de deps
   - `quality_checker` - Score detalhado
3. Logs verbose mostram:
   ```
   [INFO] Executando tool: code_analyzer
   [INFO] Executando tool: architecture_detector
   [INFO] Padrão detectado: Clean Architecture (85% confiança)
   [INFO] Executando tool: dependency_mapper
   [INFO] 42 dependências externas, 18 circulares
   [INFO] Executando tool: quality_checker
   [INFO] Quality Score: 82/100 - B (Bom)
   ```

### Output
README completo com:
- Arquitetura Clean identificada
- Score de qualidade: 82/100
- Recomendações específicas
- Grafo de dependências
- Plano de melhorias

---

## Exemplo 6: Múltiplos Diretórios

### Cenário
Monorepo com API e Workers.

### Comando
```bash
python main.py ./api ./workers ./shared -n "Monorepo Project"
```

### Estrutura
```
project/
├── api/          # REST API
├── workers/      # Background jobs
└── shared/       # Código compartilhado
```

### O que acontece
1. Escaneia os 3 diretórios
2. `architecture_detector` identifica Microservices
3. `dependency_mapper` mostra relações entre módulos
4. Documentação com:
   - Visão geral do monorepo
   - Documentação de cada serviço
   - Como os serviços se comunicam
   - Código compartilhado

---

## Exemplo 7: Notebook Jupyter

### Cenário
Análise de dados em Jupyter Notebook.

### Comando
```bash
python main.py analysis.ipynb -n "Sales Analysis"
```

### O que acontece
1. FileScanner detecta .ipynb
2. `code_analyzer` extrai células e funções
3. Documentação com:
   - Objetivo da análise
   - Principais funções
   - Bibliotecas usadas
   - Como executar

---

## Exemplo 8: Projeto sem Testes

### Cenário
Projeto legado sem testes. Você quer documentar e ver o score.

### Comando
```bash
python main.py ./legacy_app -v
```

### Output do quality_checker
```
Quality Score: 45/100 - F (Inadequado)

Problemas identificados:
- Testes: 0% - Nenhum teste encontrado
- Documentação: 35% - Poucas docstrings
- Complexidade: 62% - 12 funções muito complexas
- Boas Práticas: 58% - Secrets hardcoded detectados

Recomendações:
1. 🧪 Implemente testes unitários urgente
2. 📝 Adicione docstrings nas funções principais
3. 🔀 Refatore funções com complexidade > 10
4. 🔒 Mova secrets para variáveis de ambiente
```

---

## Exemplo 9: Comparando Versões

### Cenário
Você quer comparar documentação antes e depois de refatorar.

### Comando Antes
```bash
python main.py ./src -o docs/README_v1.md
```

### Refatoração
(Você melhora o código baseado nas recomendações)

### Comando Depois
```bash
python main.py ./src -o docs/README_v2.md
```

### Comparação
```
Antes:  Quality Score: 45/100 - F
Depois: Quality Score: 82/100 - B

Melhorias:
+ Testes: 0% → 75%
+ Documentação: 35% → 85%
+ Complexidade: 62% → 88%
```

---

## Exemplo 10: CI/CD Integration

### Cenário
Gerar documentação automaticamente no CI.

### GitHub Actions
```yaml
name: Generate Docs

on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install deps
        run: pip install -r requirements.txt
      
      - name: Generate Documentation
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python main.py ./src -n "${{ github.repository }}"
      
      - name: Commit docs
        run: |
          git config user.name "Bot"
          git config user.email "bot@example.com"
          git add README.md
          git commit -m "docs: update documentation" || exit 0
          git push
```

---

## Tips e Boas Práticas

### 1. Use Modo Verbose para Debugging
```bash
python main.py ./src -v
```
Mostra exatamente o que cada tool está fazendo.

### 2. Comece com Arquivo Único
Antes de documentar o projeto inteiro, teste com um arquivo:
```bash
python main.py main.py -v
```

### 3. Organize Output em Pastas
```bash
python main.py ./src -o docs/technical/README.md
python main.py ./api -o docs/api/API.md
```

### 4. Use Templates Apropriados
```bash
# API
python main.py ./api -t api

# Projeto completo
python main.py . -t full_project
```

### 5. Combine com Git Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash
python main.py . -o README.md
git add README.md
```

---

## Troubleshooting por Exemplo

### Problema: "Arquivo muito grande"
**Solução:** Ajuste max_file_size no FileScanner
```python
scanner = FileScanner(max_file_size=200000)  # 200KB
```

### Problema: "Muitos arquivos ignorados"
**Solução:** Ajuste max_files_per_type
```python
scanner = FileScanner(max_files_per_type=50)
```

### Problema: "Tool não executada"
**Solução:** Verifique logs verbose
```bash
python main.py ./src -v
```
Se tool não aparece, pode ser que Claude não a considerou necessária.

---

## Próximos Passos

Após documentar seu projeto:

1. **Revise a documentação gerada**
2. **Ajuste baseado nas recomendações**
3. **Execute novamente** para ver melhorias
4. **Integre no CI/CD** para manter atualizado
5. **Customize templates** se necessário
