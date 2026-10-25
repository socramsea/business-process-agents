#!/usr/bin/env bash
# Cópia diária do estado dos leads — a única cópia que existe.
# Daily copy of lead state — the only copy there is.
#
# Instalar no cron (03:00 todo dia):
#   crontab -e
#   0 3 * * * /home/sea/Projetos/business-process-agents/deploy/backup.sh
#
# DOIS BACKENDS, UM SCRIPT, pelo mesmo motivo que MemoriaLead tem três
# implementações: quem chama não deveria precisar saber onde o estado mora.
#   DATABASE_URL definida → pg_dump   (produção)
#   sem ela               → sqlite3   (local)
#
# No SQLite usa `.backup` e não `cp`: cópia de SQLite com escrita em andamento
# pode sair corrompida, e a API de backup online é segura com escritor
# concorrente. O comando certo custa o mesmo que o errado.
# Uses `sqlite3 .backup`, not `cp`: copying SQLite mid-write can corrupt.
#
# ESTE SCRIPT NUNCA APAGA NADA. Não há retenção: cópia velha fica. Quando o
# disco doer, a decisão de apagar é de quem opera, não de um cron.
# This script never deletes. Retention is a human decision.

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESTINO="$RAIZ/backup"
DATA="$(date +%F)"

mkdir -p "$DESTINO"

if [ -n "${DATABASE_URL:-}" ]; then
    # Formato custom: comprimido e restaurável seletivamente.
    #   pg_restore --dbname="$DATABASE_URL" arquivo.dump
    COPIA="$DESTINO/memoria-$DATA.dump"

    # A URL tem senha dentro — nunca é ecoada, nem em mensagem de erro.
    pg_dump --format=custom --file="$COPIA" "$DATABASE_URL"
    ORIGEM="postgres"
else
    BANCO="${1:-$RAIZ/memoria.db}"

    if [ ! -f "$BANCO" ]; then
        echo "sem banco em $BANCO e sem DATABASE_URL — nada a copiar" >&2
        exit 0
    fi

    COPIA="$DESTINO/memoria-$DATA.db"

    sqlite3 "$BANCO" ".backup '$COPIA'"
    ORIGEM="sqlite"
fi

# Só o dono lê: o banco guarda sinal de negócio por lead, e a cópia herda o
# mesmo dever. O umask padrão criaria 644.
# Owner-only: the copy carries the same business data as the original.
chmod 600 "$COPIA"

echo "$(date -Iseconds) copiado de $ORIGEM: $COPIA ($(stat -c%s "$COPIA") bytes)"
