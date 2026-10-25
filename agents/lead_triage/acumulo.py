"""
Signal accumulation across messages — the lead's score is about the relationship.
Acumulação de sinais entre mensagens — a nota é do relacionamento, não do texto.

O defeito que isto corrige: a nota era calculada por mensagem. "Tenho 50 mil"
na segunda e "preciso pra sexta" na quinta davam dois leads frios; juntos são
um quente. Quanto mais o lead conversava, pior o sistema o entendia.
The bug this fixes: the score was per message, so a chattier lead scored worse.

Função pura, sem relógio e sem I/O: o instante entra por parâmetro. Teste que
depende do relógio da máquina é teste que falha sozinho de madrugada.
Pure function — the timestamp is a parameter, never read from the clock.
"""

from typing import Any

# Trava em true e nunca volta: são fatos sobre a pessoa, não sobre a mensagem.
# Quem é dono da clínica na segunda continua dono na quinta.
SINAIS_QUE_TRAVAM = ("orcamento", "autoridade", "descadastro")

# Não acumula: vale sempre o valor da última mensagem.
# Urgência que trava é urgência falsa — "preciso pra outubro" dito em julho
# viraria lead quente em dezembro, e o vendedor priorizaria quem já desistiu.
SINAIS_SEM_ACUMULO = ("urgencia",)

ESTADO_VAZIO: dict[str, Any] = {
    "mensagens": 0,
    "sinais": {},
    "travado_em": {},
    "agente_indicado": "indefinido",
    "agentes_vistos": [],
}


def acumular(anterior: dict[str, Any], novos: dict[str, Any], quando: str) -> dict[str, Any]:
    """
    Funde o estado guardado com os sinais da mensagem que acabou de chegar.
    Merges stored state with the signals from the message that just arrived.

    `quando` é o instante em formato ISO, vindo de quem chamou.
    """
    estado = {**ESTADO_VAZIO, **anterior}
    sinais = dict(estado.get("sinais") or {})
    travado_em = dict(estado.get("travado_em") or {})

    for nome in SINAIS_QUE_TRAVAM:
        ja_era = bool(sinais.get(nome))
        agora_e = bool(novos.get(nome))
        sinais[nome] = ja_era or agora_e
        # Guarda quando travou pela primeira vez. Não é usado em regra nenhuma
        # hoje — está aqui para uma eventual validade não exigir migração.
        if agora_e and not ja_era:
            travado_em[nome] = quando

    for nome in SINAIS_SEM_ACUMULO:
        sinais[nome] = bool(novos.get(nome))

    agentes_vistos = list(estado.get("agentes_vistos") or [])
    agente_novo = novos.get("agente_indicado", "indefinido")
    agente_decidido = estado.get("agente_indicado", "indefinido")

    if agente_novo and agente_novo != "indefinido":
        # A decisão é a mais recente, mas a lista guarda todas. Sobrescrever
        # jogaria fora informação já paga: lead com dor de atendimento numa
        # mensagem e comercial na outra TEM os dois problemas, e saber disso
        # justifica proposta maior.
        agente_decidido = agente_novo
        agentes_vistos.append({"agente": agente_novo, "quando": quando})

    return {
        **estado,
        "mensagens": int(estado.get("mensagens", 0)) + 1,
        "sinais": sinais,
        "travado_em": travado_em,
        "agente_indicado": agente_decidido,
        "agentes_vistos": agentes_vistos,
        "visto_em": quando,
    }


def agentes_distintos(estado: dict[str, Any]) -> list[str]:
    """
    Quais agentes o lead já sinalizou, sem repetição, na ordem em que apareceram.
    Which agents the lead has signalled, deduped, in order of appearance.

    Mais de um = mais de uma dor. É argumento de venda, não ruído.
    """
    vistos: list[str] = []
    for registro in estado.get("agentes_vistos") or []:
        agente = registro.get("agente")
        if agente and agente not in vistos:
            vistos.append(agente)
    return vistos
