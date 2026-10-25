"""
Structured logging — so a 3am failure is visible instead of silent.
Log estruturado — para uma falha às 3h ser visível em vez de silenciosa.

O projeto inteiro tratava falha com cuidado — `vazio`, `falha`, `detalhe` com o
motivo — e não gravava nada em lugar nenhum. Se a API caísse de madrugada, o
lead era atendido, a observação era gerada, e ninguém ficava sabendo. Você
descobriria pela fatura.
The project handled failure carefully and recorded none of it.

JSON por linha porque log de agente é lido por máquina antes de humano: filtrar
por `lead_id` num `jq` vale mais que alinhamento bonito no terminal.
"""

import json
import logging
import sys
from typing import Any

LOGGER = logging.getLogger("agentes")


class FormatadorJSON(logging.Formatter):
    """Uma linha JSON por registro. O que veio em `extra` entra no mesmo nível."""

    CAMPOS_PADRAO = frozenset(logging.LogRecord("", 0, "", 0, "", None, None).__dict__)

    def format(self, record: logging.LogRecord) -> str:
        saida: dict[str, Any] = {
            "quando": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "nivel": record.levelname.lower(),
            "evento": record.getMessage(),
        }
        # Tudo que veio por `extra=` sobe pro topo do JSON, em vez de ficar
        # escondido dentro de uma chave aninhada que ninguém filtra.
        saida.update(
            {k: v for k, v in record.__dict__.items() if k not in self.CAMPOS_PADRAO}
        )
        if record.exc_info:
            saida["excecao"] = self.formatException(record.exc_info)

        return json.dumps(saida, ensure_ascii=False, default=str)


def configurar(nivel: int = logging.INFO) -> None:
    """
    Liga o log na saída padrão. Idempotente — chamar duas vezes não duplica linha.
    Idempotent: calling twice does not duplicate output.
    """
    if LOGGER.handlers:
        return

    destino = logging.StreamHandler(sys.stdout)
    destino.setFormatter(FormatadorJSON())
    LOGGER.addHandler(destino)
    LOGGER.setLevel(nivel)
    # Não propaga pro root: senão a mensagem sai duas vezes se a aplicação já
    # tiver configurado logging por conta própria.
    LOGGER.propagate = False


def registro_da_decisao(
    tenant_id: str,
    lead_id: str,
    resultado: dict[str, Any],
    fontes: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Monta o que fica gravado de uma decisão. Função pura: dá para testar o
    conteúdo do log sem capturar stdout nem depender de handler.
    Pure function — the log content is testable without capturing stdout.

    Guarda o status de CADA fonte, não só o resultado final. É a diferença entre
    saber que o lead deu 40 pontos e saber que deu 40 porque o site respondeu e
    o modelo não.
    """
    return {
        "tenant_id": tenant_id,
        "lead_id": lead_id,
        "pontos": resultado.get("pontos"),
        "classificacao": resultado.get("classificacao"),
        "agente_indicado": resultado.get("agente_indicado"),
        "agentes_vistos": resultado.get("agentes_vistos"),
        "mensagens": resultado.get("mensagens"),
        "escalar": resultado.get("escalar"),
        "motivo_escalada": resultado.get("motivo_escalada"),
        "fontes": {
            f.get("fonte", "?"): {"status": f.get("status"), "detalhe": f.get("detalhe")}
            for f in fontes
        },
    }
