"""
Roda a suíte de regressão da INSTRUCAO contra a API de verdade.
Runs the INSTRUCAO regression suite against the live API.

    python3 -m evals.rodar                    # todos os casos, OpenAI
    python3 -m evals.rodar --categoria gerente
    python3 -m evals.rodar --provedor anthropic
    python3 -m evals.rodar --caso prop_imp_01

Sai com código 1 se algum caso divergir — dá pra usar como portão antes de
commitar uma mudança na instrução.
Exits 1 if any case diverges, so it works as a gate before committing a change.
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.base_enricher import BaseEnricher, enriquecer
from evals.casos import CASOS
from evals.comparar import (
    comparar,
    resumir,
    resumo_auditavel,
    taxa_por_fronteira,
)

VERDE = "\033[32m"
VERMELHO = "\033[31m"
CINZA = "\033[90m"
FIM = "\033[0m"


def montar_fonte(provedor: str) -> BaseEnricher:
    if provedor == "anthropic":
        from agents.lead_triage.signals import MensagemEnricher

        return MensagemEnricher()

    from enrichers.mensagem_openai import MensagemEnricherOpenAI

    return MensagemEnricherOpenAI()


def rodar_caso(caso: dict[str, Any], provedor: str) -> dict[str, Any]:
    # Passa pelo enriquecer() de propósito: um caso que quebra não derruba a
    # rodada inteira, mesma regra do pipeline de produção.
    resultado = enriquecer(caso["mensagem"], [montar_fonte(provedor)])[0]

    if resultado["status"] != "ok":
        return {
            **caso,
            "devolvido": {},
            "divergencias": [],
            "erro": f"{resultado['status']}: {resultado['detalhe']}",
        }

    devolvido = resultado["dados"]
    return {
        **caso,
        "devolvido": devolvido,
        "divergencias": comparar(caso, devolvido),
        "erro": None,
    }


def imprimir(r: dict[str, Any]) -> None:
    ok = not r["divergencias"] and not r["erro"]
    marca = f"{VERDE}PASSOU{FIM}" if ok else f"{VERMELHO}FALHOU{FIM}"

    print(f"\n{marca}  [{r['id']}] {CINZA}{r['categoria']}{FIM}")
    print(f"  mensagem : {r['mensagem']}")

    if r["erro"]:
        print(f"  {VERMELHO}erro     : {r['erro']}{FIM}")
        return

    print(f"  esperado : {json.dumps(r['esperado'], ensure_ascii=False)}")
    print(f"  devolvido: {json.dumps(r['devolvido'], ensure_ascii=False)}")

    if r["divergencias"]:
        print(f"  {VERMELHO}divergências:{FIM}")
        for d in r["divergencias"]:
            print(
                f"    - {d['campo']}: esperado {d['esperado']!r}, "
                f"devolvido {d['devolvido']!r}"
            )


def main() -> int:
    p = argparse.ArgumentParser(description="Suíte de regressão da INSTRUCAO")
    p.add_argument("--provedor", default="openai", choices=["openai", "anthropic"])
    p.add_argument("--categoria", help="roda só uma categoria")
    p.add_argument("--caso", help="roda só um caso, pelo id")
    p.add_argument("--paralelo", type=int, default=8, help="chamadas simultâneas")
    p.add_argument("--json", action="store_true", help="saída em JSON, pra script")
    p.add_argument(
        "--registrar",
        action="store_true",
        help="grava o resumo em evals/historico/ pra medição ficar conferível depois",
    )
    args = p.parse_args()

    casos = CASOS
    if args.categoria:
        casos = [c for c in casos if c["categoria"] == args.categoria]
    if args.caso:
        casos = [c for c in casos if c["id"] == args.caso]

    if not casos:
        print("nenhum caso bateu com o filtro", file=sys.stderr)
        return 2

    print(f"{len(casos)} casos · provedor {args.provedor}", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.paralelo) as pool:
        resultados = list(pool.map(lambda c: rodar_caso(c, args.provedor), casos))

    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return 0 if all(not r["divergencias"] and not r["erro"] for r in resultados) else 1

    for r in resultados:
        imprimir(r)

    s = resumir(resultados)
    print(f"\n{'=' * 60}")
    print(f"{s['passaram']}/{s['total']} passaram  ({s['taxa']:.0%})")

    # Duas taxas separadas: um numero so esconde a fronteira.
    fronteira = taxa_por_fronteira(resultados)
    for grupo in ("atrito", "demais"):
        campos = fronteira[grupo]
        if not campos:
            continue
        linha = "  ".join(f"{c} {v['taxa']:.0%}" for c, v in campos.items())
        print(f"  {grupo:8} {linha}")
    if s["por_campo"]:
        print(f"campos que mais erraram : {s['por_campo']}")
    if s["por_categoria"]:
        print(f"categorias com falha    : {s['por_categoria']}")

    if args.registrar:
        from agents.lead_triage.signals import INSTRUCAO

        agora = datetime.now(timezone.utc)
        registro = resumo_auditavel(
            resultados, INSTRUCAO, agora.isoformat(timespec="seconds"), args.provedor
        )
        destino = Path("evals/historico")
        destino.mkdir(exist_ok=True)
        nome = f"{agora:%Y%m%d-%H%M%S}-{registro['instrucao_sha']}.json"
        (destino / nome).write_text(
            json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\nregistrado: evals/historico/{nome}")

    return 0 if s["falharam"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
