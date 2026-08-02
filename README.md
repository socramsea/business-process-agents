# Autonomous Business-Process Agents

[![CI](https://github.com/WSS13Framework/business-process-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/WSS13Framework/business-process-agents/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://github.com/WSS13Framework/business-process-agents)

A shared foundation for building production AI agents that do real work,
fail safely, and hand off to humans when they should — not chatbots or demos.

Uma base compartilhada para construir agentes de IA de produção que fazem
trabalho real, falham com segurança e passam para humanos quando devem.

## Why this exists / Por que existe

Most "AI agents" are one-off scripts. This project is the opposite: one shared
base (logging, retries, error handling, human hand-off) that every agent inherits,
so the 12th agent is faster to build than the 1st.

A maioria dos "agentes de IA" são scripts avulsos. Este projeto é o oposto: uma
base compartilhada que todo agente herda, então o 12º agente é mais rápido de
construir que o 1º.

## Design → see ARCHITECTURE.md

The full reasoning — interface contracts, per-tenant scoring, retry vs. circuit
breaker, autonomy limits vs. red lines — is documented in
[ARCHITECTURE.md](./ARCHITECTURE.md).

## Setup

```bash
pip install -r requirements-dev.txt

cp .env.example .env          # preencha com a sua chave / fill in your key
chmod 600 .env                # SÓ VOCÊ LÊ — veja abaixo / owner-only, see below
set -a; source .env; set +a   # exporta pro ambiente / export to the environment

pytest                        # roda offline, sem chave / runs offline, no key needed
```

O `chmod 600` não é zelo — é correção de uma exposição real. Com `umask 0002`,
que é o padrão de várias distribuições, o `cp` acima cria o `.env` com modo
**664**: legível por qualquer conta da máquina. O `.gitignore` protege contra o
git e não protege contra isso. Numa máquina com mais de um usuário — e uma
conta de serviço como `postgres` conta —, a chave fica ao alcance de quem
souber o caminho, e o caminho está neste README.

The `chmod 600` fixes a real exposure: with `umask 0002` the copy above creates
a world-readable `.env`. `.gitignore` does not protect against that.

A chave **nunca** entra no código. O SDK lê `ANTHROPIC_API_KEY` do ambiente
sozinho — por isso o cliente é construído sem argumento: `anthropic.Anthropic()`.
O `.env` é ignorado pelo git; só o `.env.example`, sem segredo, é versionado.

The key **never** goes in the code. The SDK reads `ANTHROPIC_API_KEY` from the
environment on its own — which is why the client takes no argument.

> Chave commitada em repositório público é revogada pela Anthropic em minutos
> por varredura automática. Até lá, roda no seu crédito.

## Banco de dados / Database

**Sem `DATABASE_URL`, tudo funciona.** O estado vai para o SQLite (`memoria.db`),
o CLI roda e a suíte passa. É o modo de quem clonou o repositório agora.
Without `DATABASE_URL` everything works — state goes to SQLite.

Com Postgres, o schema deixa de nascer sozinho e passa a ser das migrações:

```bash
export DATABASE_URL=postgresql://usuario:senha@localhost:5432/agentes
alembic upgrade head          # aplica o que falta / applies what's missing
alembic history               # o que existe / what exists
alembic downgrade -1          # desfaz a última / undoes the last one
```

O Postgres guarda a **memória da empresa** — Pessoa, Identidade e Mensagem
(`core/memoria_corporativa.py`). `MemoriaCorporativaPostgres` **não cria
tabela**: se ela não existir, é erro de deploy e tem que aparecer.

O SQLite guarda outra coisa: o **estado acumulado do SDR**, que é derivado e
recalculável. Ele cria a sua tabela inline porque nunca foi schema de produção.
Os dois coexistem e não se sobrepõem.

### Rodar os testes de Postgres / Running the Postgres tests

Eles pulam sem banco, com o motivo visível na saída do pytest. Para rodar:

```bash
export DATABASE_URL_TESTE=postgresql://usuario:senha@localhost:5432/agentes_teste
pytest -k postgres -v
```

> **`DATABASE_URL_TESTE` precisa apontar para outro banco.** O preparo dos
> testes dá `TRUNCATE` nas tabelas da memória da empresa. `core/config.py`
> recusa rodar se as duas URLs forem iguais, mas a primeira linha de defesa é
> você preencher certo.
> The test database MUST be a different one — the suite truncates it.

### Backup

`deploy/backup.sh` copia o estado, escolhendo o backend sozinho: `pg_dump`
quando há `DATABASE_URL`, `sqlite3 .backup` quando não há. A cópia sai com modo
`600` e **o script nunca apaga nada** — não há retenção, e apagar cópia antiga é
decisão de quem opera, não de um cron.

O diretório `backup/` inteiro é ignorado pelo git: um `pg_dump` traz nome,
telefone e o que cada lead escreveu, em claro.

## Stack

`Python` · `Claude API` · `n8n` · `PostgreSQL` · vector store · structured logging

## Status

🚧 Work in progress — building the shared base and a reference agent (lead triage)
first, then scaling to more agents on top of it.
