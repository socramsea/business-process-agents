"""
Comparação entre o gabarito e o que o modelo devolveu. Sem rede, sem API.
Comparison between the answer key and what the model returned. No network.

Fica separado do runner de propósito: assim a lógica que decide "isto é uma
regressão" tem teste offline e roda na CI, mesmo que a chamada real não role.
Kept apart from the runner on purpose, so the "is this a regression" logic is
itself unit-tested and runs in CI even when the live call cannot.
"""

import hashlib
import re
from typing import Any

MAX_PALAVRAS_RESUMO = 15

# Se o resumo começa assim, não está em primeira pessoa.
ABERTURAS_TERCEIRA_PESSOA = (
    "a pessoa",
    "o lead",
    "a lead",
    "o cliente",
    "a cliente",
    "o usuário",
    "ele ",
    "ela ",
    # sujeitos de terceira pessoa que o modelo usou nas rodadas reais
    "ninguém",
    "ninguem",
    "alguém",
    "alguem",
    "clientes",
    "leads",
    "visitantes",
    "recepção",
    "recepcao",
    "a empresa",
    "o pessoal",
    "o povo",
    "erro ",
)

# Primeira pessoa em português tem duas marcas confiáveis: pronome/possessivo,
# e verbo terminado em -mos (1ª do plural). O resto é lista de verbos comuns
# na 1ª do singular, que não têm terminação única que os distinga.
PRONOMES_PRIMEIRA_PESSOA = {
    "eu",
    "nós",
    "nos",
    "me",
    "mim",
    "meu",
    "meus",
    "minha",
    "minhas",
    "nosso",
    "nossos",
    "nossa",
    "nossas",
    "comigo",
    "conosco",
}

VERBOS_PRIMEIRA_PESSOA = {
    "quero",
    "queria",
    "preciso",
    "precisava",
    "tenho",
    "tinha",
    "busco",
    "buscava",
    "procuro",
    "procurava",
    "gostaria",
    "estou",
    "estava",
    "sou",
    "era",
    "pretendo",
    "faço",
    "fiz",
    "montei",
    "abri",
    "fundei",
    "administro",
    "trabalho",
    "atendo",
    "presto",
    "vendo",
    "compro",
    "aprovo",
    "decido",
    "cuido",
    "gerencio",
    "represento",
    "estudo",
    "pesquiso",
    "recomendo",
    "indico",
    # pretéritos irregulares, que não terminam em -ei
    "fui",
    "vi",
    "li",
    "quis",
    "pude",
    "tive",
    "vim",
    "dei",
    "disse",
    # pretérito da 1ª do singular terminado em -i. Vai por lista porque a
    # terminação sozinha pegaria 'aqui', 'ali', 'daqui'.
    "pedi",
    "saí",
    "sai",
    "parti",
    "vendi",
    "respondi",
    "decidi",
    "conheci",
    "recebi",
    "percebi",
    "escolhi",
    "assisti",
    "descobri",
    # 1a do singular no presente. Toda forma termina em -o, e a terminacao
    # sozinha pegaria substantivo ("video", "orcamento", "erro") — vai por lista.
    "copio",
    "perco",
    "recebo",
    "digito",
    "mando",
    "ligo",
    "gasto",
    "monto",
    "emito",
    "respondo",
    "consigo",
    "fecho",
    "abro",
    "lembro",
    "acompanho",
    "cadastro",
    "publico",
    "posto",
    "dou",
    "vejo",
    "sei",
    "posso",
    "devo",
    "uso",
    "levo",
    "passo",
    "mexo",
}


def checar_resumo(resumo: str) -> list[str]:
    """
    Devolve a lista de restrições violadas. Lista vazia = resumo dentro das regras.
    Returns the list of violated constraints. Empty list = the summary is fine.
    """
    problemas = []
    texto = (resumo or "").strip()

    if not texto:
        return ["resumo vazio"]

    palavras = len(texto.split())
    if palavras > MAX_PALAVRAS_RESUMO:
        problemas.append(f"{palavras} palavras (máximo {MAX_PALAVRAS_RESUMO})")

    minusculo = texto.lower()

    if minusculo.startswith(ABERTURAS_TERCEIRA_PESSOA):
        problemas.append("começa em terceira pessoa")
    elif not _tem_primeira_pessoa(minusculo):
        problemas.append("sem marca de primeira pessoa")

    return problemas


def _tem_primeira_pessoa(texto: str) -> bool:
    palavras = re.findall(r"[a-zà-ú]+", texto)

    for p in palavras:
        if p in PRONOMES_PRIMEIRA_PESSOA or p in VERBOS_PRIMEIRA_PESSOA:
            return True
        # -mos é a 1ª do plural: estamos, queremos, temos, precisamos, buscamos.
        if len(p) > 4 and p.endswith("mos"):
            return True
        # -ei é o pretérito da 1ª do singular: gostei, entrei, montei, solicitei.
        # O corte em 5 letras evita 'lei', 'rei', 'grei'.
        if len(p) >= 5 and p.endswith("ei"):
            return True

    return False


def comparar(caso: dict[str, Any], devolvido: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Confronta um caso com o que o modelo devolveu.

    Só cobra os campos que o caso declarou. O que não está no gabarito não é
    divergência — ninguém precisa opinar sobre 'urgencia' num caso de autoridade.
    Only the fields the case declared are checked.
    """
    divergencias = []

    for campo, esperado in caso["esperado"].items():
        obtido = devolvido.get(campo)
        if obtido != esperado:
            divergencias.append({"campo": campo, "esperado": esperado, "devolvido": obtido})

    for problema in checar_resumo(str(devolvido.get("resumo", ""))):
        divergencias.append(
            {"campo": "resumo", "esperado": problema, "devolvido": devolvido.get("resumo")}
        )

    return divergencias


def taxa_por_campo(resultados: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Acerto por campo, medido só onde o gabarito cobra aquele campo.
    Per-field accuracy, measured only where the answer key pins that field down.

    Existe para o portão de regressão: uma taxa global esconde troca de erro entre
    campos — melhorar 'agente_indicado' e piorar 'autoridade' pode dar o mesmo total.
    A global rate hides one field improving while another regresses.
    """
    contagem: dict[str, dict[str, int]] = {}

    def registrar(campo: str, acertou: bool) -> None:
        c = contagem.setdefault(campo, {"certos": 0, "total": 0})
        c["total"] += 1
        c["certos"] += int(acertou)

    for r in resultados:
        if r.get("erro"):
            continue

        errados = {d["campo"] for d in r["divergencias"]}

        for campo in r["esperado"]:
            registrar(campo, campo not in errados)

        # 'resumo' é cobrado em todo caso, não só quando o gabarito o declara.
        registrar("resumo", "resumo" not in errados)

    return {
        campo: {**v, "taxa": v["certos"] / v["total"] if v["total"] else 0.0}
        for campo, v in sorted(contagem.items())
    }


def taxa_por_fronteira(resultados: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Separa os casos de fronteira dos demais e mede cada grupo por campo.
    Splits boundary cases from the rest and measures each group per field.

    Um número só esconde a fronteira: caso fácil é maioria e dilui o difícil.
    Uma queda de 100% para 89% no grupo 'atrito' some dentro de um total que
    mal se move, e é justamente ali que a regressão aparece primeiro.
    A single number hides the boundary — easy cases outnumber and dilute.
    """
    grupos: dict[str, list[dict[str, Any]]] = {"atrito": [], "demais": []}
    for r in resultados:
        grupos["atrito" if r.get("atrito") else "demais"].append(r)

    return {nome: taxa_por_campo(rs) for nome, rs in grupos.items()}


def impressao_da_instrucao(instrucao: str) -> str:
    """
    Identidade do texto que produziu os números. Não é o commit — é o conteúdo.
    The identity of the text that produced the numbers — content, not commit.

    Amarrar a medição ao sha do git deixaria o registro mentir quando a
    instrução muda sem commit. O hash do próprio texto é reproduzível por
    qualquer um, sem git: mesma instrução, mesma impressão.
    """
    return hashlib.sha256(instrucao.encode("utf-8")).hexdigest()[:12]


def resumo_auditavel(
    resultados: list[dict[str, Any]], instrucao: str, quando: str, provedor: str
) -> dict[str, Any]:
    """
    O registro que fica no repositório para a medição ser conferível depois.
    The record kept in the repo so the measurement stays checkable later.

    Sem isto, as taxas do portão vivem em /tmp e somem com a sessão — restaria
    a palavra de quem reportou, que é exatamente o que este projeto não aceita.
    Without this, the gate's rates live in /tmp and vanish with the session.
    """
    s = resumir(resultados)
    fronteira = taxa_por_fronteira(resultados)

    divergencias = sorted(
        {
            (r["id"], d["campo"], str(d["esperado"]), str(d["devolvido"]))
            for r in resultados
            for d in r["divergencias"]
        }
    )

    return {
        "quando": quando,
        "provedor": provedor,
        "instrucao_sha": impressao_da_instrucao(instrucao),
        "casos": s["total"],
        "passaram": s["passaram"],
        "por_campo": {c: v["taxa"] for c, v in taxa_por_campo(resultados).items()},
        "atrito": {c: v["taxa"] for c, v in fronteira["atrito"].items()},
        "demais": {c: v["taxa"] for c, v in fronteira["demais"].items()},
        "divergencias": [
            {"id": i, "campo": c, "esperado": e, "devolvido": d}
            for i, c, e, d in divergencias
        ],
    }


def resumir(resultados: list[dict[str, Any]]) -> dict[str, Any]:
    """Consolida a rodada: quantos passaram, quais campos mais erraram."""
    passaram = [r for r in resultados if not r["divergencias"] and not r.get("erro")]
    falharam = [r for r in resultados if r["divergencias"] or r.get("erro")]

    por_campo: dict[str, int] = {}
    por_categoria: dict[str, int] = {}
    for r in falharam:
        por_categoria[r["categoria"]] = por_categoria.get(r["categoria"], 0) + 1
        for d in r["divergencias"]:
            por_campo[d["campo"]] = por_campo.get(d["campo"], 0) + 1

    total = len(resultados)
    return {
        "total": total,
        "passaram": len(passaram),
        "falharam": len(falharam),
        "taxa": len(passaram) / total if total else 0.0,
        "por_campo": dict(sorted(por_campo.items(), key=lambda kv: -kv[1])),
        "por_categoria": dict(sorted(por_categoria.items(), key=lambda kv: -kv[1])),
    }
