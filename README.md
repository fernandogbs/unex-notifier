# UNEX Notifier (MVP)

Bot local em Python para monitorar e-mails acadêmicos, classificar com Gemini e imprimir um resumo diário no terminal.

## 1) Requisitos

- Python 3.11+
- Conta de e-mail com IMAP ativo (Gmail, Outlook, Yahoo ou outro)
- Senha de acesso IMAP (ou app password, quando o provedor exigir)
- Chave Gemini API

## 2) Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m src.main --init
```

O comando `--init` cria o `.env` de forma interativa para reduzir setup manual.
Ele pergunta em linguagem amigável e grava as variáveis técnicas (`IMAP_*`) automaticamente.

Forma rápida (script único, sem ativar venv manualmente):

```bash
bash run.sh init
bash run.sh smoke
bash run.sh run
```

Se preferir setup manual, copie `.env.example` para `.env` e ajuste os campos:

- `IMAP_*`: conexão IMAP (host, porta, usuário, senha e mailbox)
- `ALLOWED_DOMAINS`: domínios permitidos separados por vírgula (ex.: `faculdade.edu.br,universidade.edu.br`)
- `GEMINI_*`: chave e modelo do Gemini (`gemini-2.5-flash` por padrão)
- `SQLITE_PATH`: cache local dos e-mails processados

## 3) Execução

Com `run.sh`:

```bash
bash run.sh init
bash run.sh smoke
bash run.sh run
```

Se quiser forçar uma versão específica do Python:

```bash
PYTHON_BIN=python3.11 bash run.sh init
```

Execução direta com Python:

```bash
python -m src.main
```

Execução sem marcar e-mails como lidos (debug):

```bash
python -m src.main --dry-run
```

Smoke check de configuração (IMAP + Gemini):

```bash
python -m src.main --smoke-check
```

## 4) Testes

```bash
pytest
```

## 5) Cron (Linux)

Abra o crontab:

```bash
crontab -e
```

Exemplo para rodar todos os dias às 18:30:

```cron
30 18 * * * unex-notifier/.venv/bin/python -m src.main >> unex-notifier/.data/cron.log 2>&1
```

## 6) Arquitetura

- `src/config`: settings e validação de ambiente
- `src/domain`: entidades e regras puras (filtro/urgência)
- `src/infra`: integrações IMAP, Gemini e SQLite
- `src/application`: orquestração da pipeline e geração do digest
