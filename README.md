# Desafio: Supabase + Z-API

Lê contatos cadastrados no Supabase e envia, via WhatsApp (Z-API), a mensagem
personalizada `"Olá, <nome_contato> tudo bem com você?"` para até 3 números.

## Como funciona

```
Supabase (tabela "contatos")
        │  busca até MAX_CONTACTS contatos
        ▼
     main.py
        │  monta a mensagem e envia, um contato por vez
        ▼
      Z-API
        │  dispara via WhatsApp conectado
        ▼
  Celular do contato
```

Estrutura do projeto:

```
.
├── main.py                  # orquestra o fluxo (busca + envio)
├── src/
│   ├── config.py             # carrega e valida variáveis de ambiente
│   ├── supabase_client.py    # busca contatos no Supabase
│   ├── zapi_client.py        # valida telefone e envia mensagem via Z-API
│   └── logging_setup.py      # configuração de logs
├── tests/                    # testes unitários (mockados, sem rede real)
├── .env.example               # modelo das variáveis necessárias
└── requirements.txt
```

## Pré-requisitos

- Python 3.10+
- Conta gratuita no [Supabase](https://supabase.com)
- Conta gratuita na [Z-API](https://www.z-api.io) com uma instância conectada ao WhatsApp

## 1. Setup da tabela no Supabase

1. Crie um projeto no Supabase.
2. No **Table Editor**, crie uma tabela chamada `contatos` com as colunas:

   | coluna     | tipo |
   |------------|------|
   | id         | int8 (padrão, gerado automaticamente) |
   | nome       | text |
   | telefone   | text |

3. Cadastre de 1 a 3 contatos. O telefone deve estar no formato internacional,
   só números, sem espaços ou símbolos:

   ```
   nome: Maria
   telefone: 5511999999999
   ```

   (`55` = Brasil, `11` = DDD, restante = número)

4. Em **Project Settings → API**, copie a **Project URL** e a **anon / publishable key**
   — são elas que vão no `.env`. Nunca use a `service_role` / `secret key` aqui.

## 2. Setup da instância na Z-API

1. Crie uma instância gratuita na Z-API e conecte seu WhatsApp escaneando o QR Code.
2. Anote o **Instance ID** e o **Token** da instância.
3. Em **Segurança** (configurações da conta), copie o **Client-Token**.

## 3. Variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

```env
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=sb_publishable_xxxxxxxxxxxxxxxxxxxxxxxx

ZAPI_INSTANCE_ID=sua_instance_id_aqui
ZAPI_TOKEN=seu_token_aqui
ZAPI_CLIENT_TOKEN=seu_client_token_aqui

MAX_CONTACTS=3
```

⚠️ O `.env` nunca é commitado (está no `.gitignore`).

## 4. Instalação

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Como rodar

```bash
python main.py
```

Saída esperada (exemplo):

```
2026-06-20 18:30:01 | INFO     | __main__ | 3 contato(s) encontrado(s). Iniciando envios...
2026-06-20 18:30:02 | INFO     | src.zapi_client | Mensagem enviada com sucesso para 5511999999999.
2026-06-20 18:30:03 | INFO     | src.zapi_client | Mensagem enviada com sucesso para 5511888888888.
2026-06-20 18:30:04 | INFO     | src.zapi_client | Mensagem enviada com sucesso para 5511777777777.
2026-06-20 18:30:04 | INFO     | __main__ | Concluído. Sucesso: 3 | Falhas: 0
```

Se algum contato falhar (telefone inválido, erro na Z-API), o erro é logado e o
script segue para os próximos contatos — uma falha isolada não interrompe o lote.

## Rodando os testes

```bash
pip install pytest
pytest tests/ -v
```

Os testes usam *mocks* para Supabase e Z-API — nenhuma chamada de rede real é
feita durante os testes. Eles também rodam automaticamente em todo push via
GitHub Actions (`.github/workflows/tests.yml`).

## Tratamento de erros

| Situação | Comportamento |
|---|---|
| `.env` ausente ou incompleto | Erro claro no log, processo encerra antes de tentar qualquer chamada |
| Falha ao consultar o Supabase | Erro logado, processo encerra |
| Nenhum contato encontrado | Aviso logado, processo encerra sem erro |
| Contato com nome/telefone vazio | Contato ignorado, aviso logado, restante segue normalmente |
| Telefone em formato inválido | Erro logado para aquele contato, restante segue normalmente |
| Falha de rede ou erro HTTP na Z-API | Erro logado para aquele contato, restante segue normalmente |

## Troubleshooting

- **`Variável de ambiente obrigatória 'X' não foi definida`** → confira se o `.env`
  existe na raiz do projeto e se todos os campos do `.env.example` estão preenchidos.
- **Z-API retorna 401** → token, instance ID ou client-token incorretos.
- **Z-API retorna erro indicando instância desconectada** → reabra o painel da Z-API
  e reconecte o WhatsApp escaneando o QR Code novamente.
- **Nenhum contato encontrado** → confirme que a tabela `contatos` tem linhas com
  `nome` e `telefone` preenchidos no Supabase.
