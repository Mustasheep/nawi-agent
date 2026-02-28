"""
Testes do logger

use na pasta raiz o comando:
python -m tests.logger_test 
"""

from utils.logger import Logger

logger = Logger(verbose=True)
logger.info("Teste info")
logger.success("Teste sucesso")
logger.warning("Teste aviso")
logger.error("Teste erro")
logger.debug("Teste debug")
logger.section("TESTE DE SEÇÃO")