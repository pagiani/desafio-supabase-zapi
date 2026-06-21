"""
Responsável por toda a comunicação com o Supabase.

Mantém a lógica de "como buscar contatos" isolada do resto do
programa, para que main.py não precise saber detalhes da API
do Supabase.
"""
import logging
from dataclasses import dataclass

from supabase import Client, create_client

logger = logging.getLogger(__name__)

TABLE_NAME = "contatos"


class SupabaseFetchError(Exception):
    """Erro ao buscar dados no Supabase."""


@dataclass(frozen=True)
class Contact:
    nome: str
    telefone: str


def build_client(url: str, key: str) -> Client:
    return create_client(url, key)


def fetch_contacts(client: Client, limit: int) -> list[Contact]:
    """
    Busca até `limit` contatos na tabela `contatos`.

    Contatos sem nome ou telefone preenchidos são ignorados
    (com um aviso no log), pois não é possível personalizar
    nem enviar mensagem para eles.
    """
    try:
        response = (
            client.table(TABLE_NAME)
            .select("nome, telefone")
            .limit(limit)
            .execute()
        )
    except Exception as exc:
        raise SupabaseFetchError(
            f"Falha ao consultar a tabela '{TABLE_NAME}' no Supabase: {exc}"
        ) from exc

    rows = response.data or []
    if not rows:
        logger.warning("Nenhum contato encontrado na tabela '%s'.", TABLE_NAME)
        return []

    contacts: list[Contact] = []
    for row in rows:
        nome = (row.get("nome") or "").strip()
        telefone = (row.get("telefone") or "").strip()

        if not nome or not telefone:
            logger.warning(
                "Contato ignorado por dados incompletos: %s", row
            )
            continue

        contacts.append(Contact(nome=nome, telefone=telefone))

    return contacts
