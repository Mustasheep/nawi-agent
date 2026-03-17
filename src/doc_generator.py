from datetime import datetime

from config import Settings
from prompts import get_system_prompt
from scanner import FileScanner
from src import ClaudeClient

from utils import Logger

logger = Logger()

class DocGenerator:
    """
    Orquestra a geração de documentação.
    Recebe FileScanner e ClaudeClient via injeção de dependência,
    detecta o tipo de documentação necessário e despacha para o método correto.
    """

    def __init__(self, scanner: FileScanner, client: ClaudeClient, settings: Settings = None, log: Logger = None):
        self._scanner = scanner
        self._client = client
        self._cfg = settings or Settings()
        self._log = log or logger

    async def generate(self, project_name: str = "Projeto") -> str:
        """
        Ponto de entrada principal. Detecta o tipo e gera a documentação.

        Returns:
            String com o conteúdo Markdown da documentação gerada.
        """
        self._log.section("Gerando documentação com Claude AI")
        doc_type = self._scanner.detect_documentation_type()

        labels = {
            'single_file':   'Arquivo Único',
            'small_project': 'Projeto Pequeno',
            'full_project':  'Projeto Completo',
        }
        self._log.info(f"Modo: {labels.get(doc_type, doc_type)}")

        handlers = {
            'single_file':   self._generate_single_file_doc,
            'small_project': self._generate_small_project_doc,
            'full_project':  self._generate_full_project_doc,
        }
        return await handlers[doc_type](project_name)

    # ------------------
    # Geradores por tipo
    # ------------------

    async def _generate_single_file_doc(self, file_name: str) -> str:
        file_data = self._scanner.get_single_file_info()
        if not file_data:
            return self._fallback()

        info = file_data['info']
        context = (
            f"# Documentação: {info['name']}\n\n"
            f"**Tipo:** {file_data['type']}\n"
            f"**Caminho:** {info['path']}\n"
            f"**Linhas:** {info['lines']}\n\n"
            f"## Conteúdo do Arquivo\n\n```\n{info['content']}\n```\n\n"
            "Documente ESTE ARQUIVO ESPECÍFICO. NÃO trate como um projeto completo."
        )
        return await self._call(
            context=context,
            doc_type='single_file',
            max_tokens=self._cfg.MAX_TOKENS_SINGLE_FILE,
            label="arquivo único",
        )

    async def _generate_small_project_doc(self, project_name: str) -> str:
        context = (
            f"# Análise: {project_name}\n\n"
            "Estes arquivos trabalham juntos. Documente de forma concisa e direta:\n\n"
        )
        for file_type in self._cfg.EXTENSIONS:
            context += self._scanner.prepare_context(
                file_type, max_files=self._cfg.MAX_FILES_IN_CONTEXT_SMALL
            )
        return await self._call(
            context=context,
            doc_type='small_project',
            max_tokens=self._cfg.MAX_TOKENS_SMALL_PROJECT,
            label="projeto pequeno",
        )

    async def _generate_full_project_doc(self, project_name: str) -> str:
        context = (
            f"# Análise do Projeto: {project_name}\n\n"
            "Analise os seguintes arquivos e gere uma documentação completa e profissional:\n\n"
        )
        for file_type in self._cfg.EXTENSIONS:
            context += self._scanner.prepare_context(
                file_type, max_files=self._cfg.MAX_FILES_IN_CONTEXT_FULL
            )
        return await self._call(
            context=context,
            doc_type='full_project',
            max_tokens=self._cfg.MAX_TOKENS_FULL_PROJECT,
            label="projeto completo",
        )

    # ------------------
    # Helpers internos
    # ------------------

    async def _call(self, context: str, doc_type: str, max_tokens: int, label: str) -> str:
        try:
            self._log.info(f"Analisando {label}...")
            result = await self._client.call(
                messages=[{"role": "user", "content": context}],
                system_prompt=get_system_prompt(doc_type),
                max_tokens=max_tokens,
            )
            self._log.success("Documentação gerada com sucesso!\n")
            return result
        except Exception as e:
            self._log.error(f"Erro ao gerar documentação: {e}")
            return self._fallback()

    def _fallback(self) -> str:
        """Documentação básica utilizada quando a chamada à API falha."""
        lines = [
            "# Documentação do Projeto\n",
            f"*Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}*\n",
            "## Arquivos Encontrados\n",
        ]
        for file_type, files in self._scanner.files_data.items():
            if files:
                lines.append(f"### {file_type.upper()}: {len(files)} arquivos\n")
                for f in files[:5]:
                    lines.append(f"- `{f['path']}` ({f['lines']} linhas)")
                lines.append("")
        return "\n".join(lines)