"""
Ponto de entrada do projeto.

Fluxo:
  1. Carrega e valida as variáveis de ambiente.
  2. Busca até MAX_CONTACTS contatos no Supabase.
  3. Para cada contato, monta a mensagem personalizada e envia via Z-API.

Erros em um contato específico (telefone inválido, falha da Z-API)
são logados e não interrompem o envio para os demais contatos.
"""
import logging
import sys

from src.config import ConfigError, load_settings
from src.logging_setup import setup_logging
from src.supabase_client import SupabaseFetchError, build_client, fetch_contacts
from src.zapi_client import InvalidPhoneError, ZapiSendError, build_message, send_message

logger = logging.getLogger(__name__)


def run() -> int:
    """Executa o fluxo completo. Retorna o exit code do processo."""
    setup_logging()

    try:
        settings = load_settings()
    except ConfigError as exc:
        logger.error("Erro de configuração: %s", exc)
        return 1

    try:
        client = build_client(settings.supabase_url, settings.supabase_key)
        contacts = fetch_contacts(client, limit=settings.max_contacts)
    except SupabaseFetchError as exc:
        logger.error("Erro ao buscar contatos: %s", exc)
        return 1

    if not contacts:
        logger.warning("Nenhum contato válido para enviar mensagem. Encerrando.")
        return 0

    logger.info("%d contato(s) encontrado(s). Iniciando envios...", len(contacts))

    sucesso = 0
    falha = 0

    for contact in contacts:
        mensagem = build_message(contact.nome)
        try:
            send_message(
                instance_id=settings.zapi_instance_id,
                token=settings.zapi_token,
                client_token=settings.zapi_client_token,
                telefone=contact.telefone,
                mensagem=mensagem,
            )
            sucesso += 1
        except (InvalidPhoneError, ZapiSendError) as exc:
            logger.error(
                "Falha ao enviar mensagem para '%s' (%s): %s",
                contact.nome,
                contact.telefone,
                exc,
            )
            falha += 1

    logger.info("Concluído. Sucesso: %d | Falhas: %d", sucesso, falha)
    return 0 if falha == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
