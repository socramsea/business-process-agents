"""
Human handoff — when the agent should stop and call someone.
Handoff para humano — quando o agente deve parar e chamar alguém.

Promessa da §5 do ARCHITECTURE que só existia no documento. O princípio é o
mesmo do `indefinido` e do `vazio`: o agente pode dizer "isto não é comigo".
Section 5's promise, which existed only in the document.

Função pura, sem I/O: escalar é decisão, notificar é entrega. Separar os dois
deixa a regra testável sem webhook nenhum.
Pure function — escalating is a decision; notifying is delivery.
"""

from typing import Any


def decidir_escalada(
    resultado: dict[str, Any], estado: dict[str, Any], status_mensagem: str
) -> tuple[bool, str | None]:
    """
    Devolve (escalar, motivo). Motivo é None quando não escala.
    Returns (escalate, reason).

    A ordem importa: descadastro vem antes de quente, porque quem pediu para
    sair não deve receber ligação de vendedor por ter pontuação alta.
    """
    sinais = estado.get("sinais") or {}

    if sinais.get("descadastro"):
        # Não é venda: alguém precisa tirar da lista de verdade. Automatizar a
        # remoção sem humano é o tipo de coisa que vira multa.
        return True, "pediu descadastro — precisa sair da lista"

    if resultado.get("classificacao") == "quente":
        return True, "lead quente — vendedor deve ligar"

    if status_mensagem != "ok" and int(estado.get("mensagens", 0)) <= 1:
        # Falhou logo na primeira mensagem: não sabemos nada sobre esta pessoa.
        # A partir da segunda o acumulado sustenta a classificação, e escalar
        # toda falha inundaria o humano justamente quando o provedor cai.
        return True, "não consegui analisar a primeira mensagem"

    return False, None
