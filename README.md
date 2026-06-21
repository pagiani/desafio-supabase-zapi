# Supabase + Z-API

Script que busca contatos cadastrados numa tabela do Supabase e envia, via WhatsApp (Z-API), a mensagem `"Olá, <nome> tudo bem com você?"` para cada um.

## Estrutura

`main.py` orquestra o fluxo. A lógica fica separada em `src/`: `supabase_client.py` busca os contatos, `zapi_client.py` valida o telefone e envia a mensagem, `config.py` carrega e valida as variáveis de ambiente. Testes em `tests/` mockam as duas APIs, então rodam sem internet.

## Setup da tabela no Supabase

Crie uma tabela `contatos` com as colunas `nome` (text) e `telefone` (text), além do `id` padrão. Telefone no formato internacional, só dígitos: `5511999999999` (55 = Brasil, 11 = DDD).

Em Project Settings → API, pegue a Project URL e a chave `anon` / `publishable` (não use a `service_role`/`secret`).

## Setup da Z-API

Crie uma instância gratuita e conecte seu WhatsApp pelo QR Code. Você vai precisar do Instance ID, do Token da instância e do Client-Token (esse último fica em Segurança, nas configurações da conta).

## Variáveis de ambiente

```bash
cp .env.example .env
```

Preencha no `.env`:

```
SUPABASE_URL=
SUPABASE_KEY=
ZAPI_INSTANCE_ID=
ZAPI_TOKEN=
ZAPI_CLIENT_TOKEN=
MAX_CONTACTS=3
```

O `.env` não é commitado (está no `.gitignore`).

## Rodando

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Um contato com telefone inválido ou erro pontual na Z-API não interrompe os demais — o erro fica logado e o script segue para o próximo.

## Testes

```bash
pip install pytest
pytest tests/ -v
```

Rodam também via GitHub Actions a cada push.

## Erros comuns

Variável de ambiente faltando: confira se o `.env` está preenchido como o `.env.example`.
Z-API retornando 401: instance ID, token ou client-token errados.
Instância desconectada: reabra o painel da Z-API e escaneie o QR Code de novo.
Nenhum contato retornado: confira se a tabela `contatos` tem linhas com nome e telefone preenchidos.
