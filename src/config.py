"""
Carrega e valida as variáveis de ambiente usadas pelo projeto.

Centralizar isso aqui evita espalhar os.getenv() pelo código
e garante que, se faltar alguma credencial, o erro aparece
de forma clara logo no início da execução.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Erro de configuração: variável de ambiente ausente ou inválida."""


@dataclass(frozen=True)
class Settings:
    supabase_url: str
    supabase_key: str
    zapi_instance_id: str
    zapi_token: str
    zapi_client_token: str
    max_contacts: int


def _require(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value or not value.strip():
        raise ConfigError(
            f"Variável de ambiente obrigatória '{var_name}' não foi definida. "
            f"Verifique se o arquivo .env existe e está preenchido "
            f"(veja .env.example como referência)."
        )
    return value.strip()


def load_settings() -> Settings:
    """Lê e valida todas as variáveis necessárias. Lança ConfigError se algo faltar."""
    max_contacts_raw = os.getenv("MAX_CONTACTS", "3")
    try:
        max_contacts = int(max_contacts_raw)
    except ValueError as exc:
        raise ConfigError(
            f"MAX_CONTACTS deve ser um número inteiro, recebido: '{max_contacts_raw}'"
        ) from exc

    return Settings(
        supabase_url=_require("SUPABASE_URL"),
        supabase_key=_require("SUPABASE_KEY"),
        zapi_instance_id=_require("ZAPI_INSTANCE_ID"),
        zapi_token=_require("ZAPI_TOKEN"),
        zapi_client_token=_require("ZAPI_CLIENT_TOKEN"),
        max_contacts=max_contacts,
    )
