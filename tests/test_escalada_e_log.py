"""
Prova o handoff pra humano e o log estruturado.
Proves the human handoff and the structured log.

Os dois existem pela mesma razão: sem eles o agente decide sozinho e ninguém vê.
"""

import json
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.lead_triage.agent import LeadTriageAgent
from agents.lead_triage.escalada import decidir_escalada
from core.log import FormatadorJSON, configurar, registro_da_decisao
from core.memoria import MemoriaEmMemoria
from tests.fakes import ClienteFalso, RespostaFalsa

T1 = "2026-07-01T10:00:00+00:00"
T2 = "2026-07-08T10:00:00+00:00"


def sinais(**kw: object) -> dict:
    base = {
        "orcamento": False,
        "urgencia": False,
        "autoridade": False,
        "descadastro": False,
        "agente_indicado": "indefinido",
        "resumo": "",
    }
    return {**base, **kw}


# ---- decidir_escalada ----
def test_lead_quente_escala():
    escalar, motivo = decidir_escalada(
        {"classificacao": "quente"}, {"sinais": {}, "mensagens": 1}, "ok"
    )

    assert escalar is True
    assert "vendedor" in motivo


def test_descadastro_escala_e_vence_o_quente():
    """
    Quem pediu pra sair não pode receber ligação de vendedor por ter pontuação
    alta. A ordem da regra é o que garante isso.
    """
    escalar, motivo = decidir_escalada(
        {"classificacao": "quente"}, {"sinais": {"descadastro": True}, "mensagens": 3}, "ok"
    )

    assert escalar is True
    assert "descadastro" in motivo


def test_falha_na_primeira_mensagem_escala():
    """Não sabemos nada sobre esta pessoa — humano assume."""
    escalar, motivo = decidir_escalada(
        {"classificacao": "frio"}, {"sinais": {}, "mensagens": 1}, "falha"
    )

    assert escalar is True
    assert "primeira mensagem" in motivo


def test_falha_depois_da_primeira_nao_escala():
    """
    Escalar toda falha inundaria o humano justamente quando o provedor cai.
    A partir da segunda mensagem o acumulado sustenta a classificação.
    """
    escalar, _ = decidir_escalada(
        {"classificacao": "morno"}, {"sinais": {"orcamento": True}, "mensagens": 4}, "falha"
    )

    assert escalar is False


def test_lead_morno_sem_falha_nao_escala():
    escalar, motivo = decidir_escalada(
        {"classificacao": "morno"}, {"sinais": {}, "mensagens": 2}, "ok"
    )

    assert escalar is False
    assert motivo is None


# ---- o agente devolve a escalada ----
def test_agente_marca_escalada_no_resultado():
    m = MemoriaEmMemoria()
    agente = LeadTriageAgent(
        "forja",
        cliente=ClienteFalso(RespostaFalsa(sinais(descadastro=True))),
        memoria=m,
    )

    r = agente.handle("me tira do mailing", "lead-1", quando=T1)

    assert r["escalar"] is True
    assert "descadastro" in r["motivo_escalada"]


def test_lead_comum_nao_escala():
    m = MemoriaEmMemoria()
    agente = LeadTriageAgent("forja", cliente=ClienteFalso(RespostaFalsa(sinais())), memoria=m)

    r = agente.handle("oi", "lead-1", quando=T1)

    assert r["escalar"] is False
    assert r["motivo_escalada"] is None


# ---- registro_da_decisao ----
def test_registro_guarda_o_status_de_cada_fonte():
    """
    Saber que o lead deu 40 pontos é diferente de saber que deu 40 porque o
    site respondeu e o modelo não.
    """
    registro = registro_da_decisao(
        "forja",
        "lead-1",
        {"pontos": 40, "classificacao": "morno", "escalar": False},
        [
            {"fonte": "mensagem", "status": "falha", "detalhe": "APIConnectionError: caiu"},
            {"fonte": "site", "status": "ok", "detalhe": None},
        ],
    )

    assert registro["fontes"]["mensagem"]["status"] == "falha"
    assert registro["fontes"]["mensagem"]["detalhe"] == "APIConnectionError: caiu"
    assert registro["fontes"]["site"]["status"] == "ok"
    assert registro["tenant_id"] == "forja" and registro["lead_id"] == "lead-1"


def test_formatador_devolve_json_com_o_extra_no_topo():
    """O que veio em `extra` não pode ficar aninhado — ninguém filtra o que está escondido."""
    registro = logging.LogRecord("agentes", logging.INFO, "", 0, "lead classificado", None, None)
    registro.lead_id = "lead-1"
    registro.pontos = 70

    saida = json.loads(FormatadorJSON().format(registro))

    assert saida["evento"] == "lead classificado"
    assert saida["lead_id"] == "lead-1"
    assert saida["pontos"] == 70
    assert saida["nivel"] == "info"


def test_configurar_e_idempotente():
    configurar()
    configurar()

    from core.log import LOGGER

    assert len(LOGGER.handlers) == 1, "chamar duas vezes não pode duplicar linha de log"
