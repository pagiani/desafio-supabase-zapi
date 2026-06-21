"""
Responsável por toda a comunicação com a Z-API.

Isola os detalhes do endpoint HTTP (URL, headers, payload) do
resto do programa, e cuida da validação de telefone e tratamento
de erros de rede/HTTP.
"""
import logging
import re

import requests

logger = logging.getLogger(__name__)

ZAPI_BASE_URL = "https://api.z-api.io/instances"
REQUEST_TIMEOUT_SECONDS = 15

# Telefone no formato internacional: código do país + DDD + número.
# Ex: 5511999999999 (11 a 13 dígitos cobre a maioria dos países)
PHONE_REGEX = re.compile(r"^\d{11,13}$")


class InvalidPhoneError(Exception):
    """Telefone em formato inválido para envio."""


class ZapiSendError(Exception):
    """Erro ao enviar mensagem pela Z-API (rede, HTTP ou resposta de erro)."""


def _validate_phone(telefone: str) -> str:
    digits_only = re.sub(r"\D", "", telefone)
    if not PHONE_REGEX.match(digits_only):
        raise InvalidPhoneError(
            f"Telefone '{telefone}' não está em formato válido. "
            f"Use o formato internacional sem símbolos, ex: 5511999999999"
        )
    return digits_only


def build_message(nome: str) -> str:
    """Monta a mensagem exata exigida pelo desafio, personalizada com o nome."""
    return f"Olá, {nome} tudo bem com você?"


def send_message(
    instance_id: str,
    token: str,
    client_token: str,
    telefone: str,
    mensagem: str,
) -> None:
    """
    Envia uma mensagem de texto via Z-API.

    Lança InvalidPhoneError se o telefone for inválido, ou
    ZapiSendError se a chamada falhar (rede, timeout, ou erro
    retornado pela própria Z-API).
    """
    phone = _validate_phone(telefone)

    url = f"{ZAPI_BASE_URL}/{instance_id}/token/{token}/send-text"
    headers = {"Client-Token": client_token}
    payload = {"phone": phone, "message": mensagem}

    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
        )
    except requests.exceptions.RequestException as exc:
        raise ZapiSendError(
            f"Falha de conexão ao chamar a Z-API para o número {phone}: {exc}"
        ) from exc

    if response.status_code >= 400:
        raise ZapiSendError(
            f"Z-API retornou erro {response.status_code} para o número {phone}: "
            f"{response.text}"
        )

    logger.info("Mensagem enviada com sucesso para %s.", phone)
