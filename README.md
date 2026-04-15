# UNEX Notifier (MVP)

Bot local em Python para monitorar e-mails acadêmicos, classificar com Gemini e imprimir um resumo diário no terminal.

## 1) Requisitos

- Python 3.11+
- Conta Gmail com IMAP ativo
- App Password do Google
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

Se preferir setup manual, copie `.env.example` e ajuste os campos:

- `IMAP_*`: conexão Gmail/IMAP
- `ALLOWED_DOMAINS`: domínios permitidos separados por vírgula
- `GEMINI_*`: chave e modelo do Gemini
- `SQLITE_PATH`: cache local dos e-mails processados

## 3) Execução

Forma rápida (script único):

```bash
./run.sh init
./run.sh smoke
./run.sh run
```

Execução normal:

```bash
python -m src.main
```

Execução sem marcar como lido (debug):

```bash
python -m src.main --dry-run
```

Smoke check de conectividade:

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
30 18 * * * /home/fernando/Documents/personal/unex_notifier/.venv/bin/python -m src.main >> /home/fernando/Documents/personal/unex_notifier/.data/cron.log 2>&1
```

## 6) Arquitetura

- `src/config`: settings e validação de ambiente
- `src/domain`: entidades e regras puras (filtro/urgência)
- `src/infra`: integrações IMAP, Gemini e SQLite
- `src/application`: orquestração da pipeline e geração do digest
