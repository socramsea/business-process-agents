"""
Ponto de entrada — o mínimo para isto rodar com lead de verdade.
Entry point — the minimum needed to run this against a real lead.

    python3 -m agents.lead_triage.cli --lead lead-001 --mensagem "tenho uma clínica..."

O estado persiste em SQLite entre chamadas, então mandar duas mensagens do
mesmo `--lead` acumula. É isso que separa este CLI de um script de demonstração.
State persists in SQLite between calls, so two messages accumulate.
"""

import argparse
import json
import sys

from agents.lead_triage.agent import LeadTriageAgent
from core.log import configurar
from core.memoria import MemoriaSQLite


def main() -> int:
    p = argparse.ArgumentParser(description="Triagem de um lead")
    p.add_argument("--mensagem", required=True, help="o que o lead escreveu")
    p.add_argument("--lead", required=True, help="id do lead; o mesmo id acumula")
    p.add_argument("--tenant", default="forja", help="cliente dono deste lead")
    p.add_argument("--db", default="memoria.db", help="arquivo do SQLite")
    p.add_argument(
        "--tipo",
        default="empresa",
        choices=["empresa", "pessoa"],
        help="muda o peso de cada fonte de enriquecimento",
    )
    p.add_argument("--silencioso", action="store_true", help="não emite o log estruturado")
    args = p.parse_args()

    if not args.silencioso:
        # O log vai pra stdout junto com o resultado. Em produção o certo é
        # separar por stream ou por destino; aqui vale a simplicidade.
        configurar()

    agente = LeadTriageAgent(args.tenant, memoria=MemoriaSQLite(args.db))
    resultado = agente.handle(args.mensagem, args.lead, tipo_lead=args.tipo)

    print(json.dumps(resultado, ensure_ascii=False, indent=2))

    # Código 2 quando precisa de humano: dá pra encadear num `&&` ou num cron
    # sem ninguém ter que parsear JSON pra descobrir que tem gente esperando.
    return 2 if resultado["escalar"] else 0


if __name__ == "__main__":
    sys.exit(main())
