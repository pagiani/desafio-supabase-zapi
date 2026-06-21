"""Testes unitários para src/supabase_client.py (sem chamadas de rede reais)."""
import sys
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.supabase_client import Contact, fetch_contacts


def _mock_client_returning(rows):
    client = Mock()
    response = Mock()
    response.data = rows
    (
        client.table.return_value.select.return_value.limit.return_value.execute
    ).return_value = response
    return client


def test_fetch_contacts_returns_valid_contacts():
    client = _mock_client_returning(
        [
            {"nome": "Maria", "telefone": "5511999999999"},
            {"nome": "João", "telefone": "5511888888888"},
        ]
    )

    contacts = fetch_contacts(client, limit=3)

    assert contacts == [
        Contact(nome="Maria", telefone="5511999999999"),
        Contact(nome="João", telefone="5511888888888"),
    ]


def test_fetch_contacts_skips_incomplete_rows():
    client = _mock_client_returning(
        [
            {"nome": "Maria", "telefone": "5511999999999"},
            {"nome": "", "telefone": "5511888888888"},
            {"nome": "Carlos", "telefone": None},
        ]
    )

    contacts = fetch_contacts(client, limit=3)

    assert contacts == [Contact(nome="Maria", telefone="5511999999999")]


def test_fetch_contacts_returns_empty_list_when_no_rows():
    client = _mock_client_returning([])

    contacts = fetch_contacts(client, limit=3)

    assert contacts == []
