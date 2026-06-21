"""Testes unitários para src/zapi_client.py (sem chamadas de rede reais)."""
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.zapi_client import (
    InvalidPhoneError,
    ZapiSendError,
    build_message,
    send_message,
)


def test_build_message_formats_exact_string_required_by_challenge():
    assert build_message("Maria") == "Olá, Maria tudo bem com você?"


def test_send_message_raises_for_invalid_phone():
    with pytest.raises(InvalidPhoneError):
        send_message(
            instance_id="id",
            token="token",
            client_token="client-token",
            telefone="123",
            mensagem="oi",
        )


@patch("src.zapi_client.requests.post")
def test_send_message_success(mock_post):
    mock_post.return_value = Mock(status_code=200, text="{}")

    send_message(
        instance_id="instance123",
        token="token123",
        client_token="client-token-123",
        telefone="5511999999999",
        mensagem="Olá, Maria tudo bem com você?",
    )

    mock_post.assert_called_once()
    called_url = mock_post.call_args.args[0]
    assert "instance123" in called_url
    assert "token123" in called_url


@patch("src.zapi_client.requests.post")
def test_send_message_raises_on_http_error(mock_post):
    mock_post.return_value = Mock(status_code=401, text="Unauthorized")

    with pytest.raises(ZapiSendError):
        send_message(
            instance_id="id",
            token="token",
            client_token="client-token",
            telefone="5511999999999",
            mensagem="oi",
        )


@patch(
    "src.zapi_client.requests.post",
    side_effect=requests.exceptions.ConnectionError("boom"),
)
def test_send_message_raises_on_network_error(mock_post):
    with pytest.raises(ZapiSendError):
        send_message(
            instance_id="id",
            token="token",
            client_token="client-token",
            telefone="5511999999999",
            mensagem="oi",
        )
