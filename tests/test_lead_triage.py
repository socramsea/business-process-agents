"""
Prova a pontuação derivada do enriquecimento e o agente que a usa.
Proves enrichment-derived scoring and the agent that uses it.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.lead_triage.agent import LeadTriageAgent
from agents.lead_triage.scoring import pontuar_enriquecimento
from tests.fakes import NEUTRO, cliente_com

PESOS = {
    "empresa": {"site": 25, "youtube": 15},
    "pessoa": {"site": 5, "youtube": 40},
}

OK_SITE = {
    "fonte": "site",
    "status": "ok",
    "dados": {"titulo": "Forja Criativa", "url": "https://forjacriativa.ia.br"},
    "detalhe": None,
}
OK_YOUTUBE = {
    "fonte": "youtube",
    "status": "ok",
    "dados": {"titulo": "Canal da Forja"},
    "detalhe": None,
}
VAZIO_SITE = {
    "fonte": "site",
    "status": "vazio",
    "dados": {},
    "detalhe": "página carregou, mas sem título nem description",
}
FALHA_SITE = {
    "fonte": "site",
    "status": "falha",
    "dados": {},
    "detalhe": "ConnectTimeout: site fora do ar",
}


# ---- pontuar_enriquecimento ----
def test_so_status_ok_pontua():
    pontos, _ = pontuar_enriquecimento([OK_SITE, OK_YOUTUBE], "empresa", PESOS)

    assert pontos == 40  # 25 + 15


def test_vazio_e_falha_nao_pontuam_mas_falam():
    pontos, observacoes = pontuar_enriquecimento([VAZIO_SITE, FALHA_SITE], "empresa", PESOS)

    assert pontos == 0
    assert len(observacoes) == 2, "não pontuar não é motivo pra ficar calado"
    assert "busquei e não achei" in observacoes[0]
    assert "não consegui consultar" in observacoes[1]


def test_falha_carrega_o_motivo_pra_virar_conversa():
    _, observacoes = pontuar_enriquecimento([FALHA_SITE], "empresa", PESOS)

    assert "site fora do ar" in observacoes[0]


def test_o_mesmo_sinal_vale_diferente_por_tipo_de_lead():
    """A mesma fonte pesa diferente pra empresa e pra pessoa."""
    como_empresa, _ = pontuar_enriquecimento([OK_YOUTUBE], "empresa", PESOS)
    como_pessoa, _ = pontuar_enriquecimento([OK_YOUTUBE], "pessoa", PESOS)

    assert como_empresa == 15
    assert como_pessoa == 40


def test_tipo_de_lead_desconhecido_nao_pontua_nem_quebra():
    pontos, observacoes = pontuar_enriquecimento([OK_SITE], "extraterrestre", PESOS)

    assert pontos == 0
    assert len(observacoes) == 1, "sem peso pra somar, mas o dado achado ainda serve"


def test_fonte_fora_da_tabela_de_pesos_nao_pontua():
    de_fora = {**OK_SITE, "fonte": "tiktok"}
    pontos, _ = pontuar_enriquecimento([de_fora], "empresa", PESOS)

    assert pontos == 0


def test_formato_torto_aparece_em_vez_de_sumir():
    torto = {"fonte": "site", "status": "sei_la", "dados": {}, "detalhe": None}
    pontos, observacoes = pontuar_enriquecimento([torto], "empresa", PESOS)

    assert pontos == 0
    assert "formato inesperado" in observacoes[0]


def test_lista_vazia_da_zero():
    assert pontuar_enriquecimento([], "empresa", PESOS) == (0, [])


# ---- LeadTriageAgent ----
def test_sem_enriquecimento_pontua_zero():
    r = LeadTriageAgent("forja-criativa", cliente=cliente_com(NEUTRO)).handle("oi", "lead-001")

    assert r["pontos"] == 0
    assert r["classificacao"] == "frio"
    # A mensagem neutra fala ("só perguntou..."), mas não pontua.
    assert r["observacoes"] == ["mensagem: só perguntou o que a empresa faz"]


def test_com_enriquecimento_a_nota_sobe():
    agente = LeadTriageAgent("forja-criativa", cliente=cliente_com(NEUTRO))

    sem = agente.handle("oi", "lead-001")
    com = agente.handle("oi", "lead-001", enriquecimento=[OK_SITE, OK_YOUTUBE])

    assert com["pontos"] > sem["pontos"]
    assert com["observacoes"], "o enriquecimento tem que alimentar a conversa também"


def test_contrato_de_saida_do_agente():
    r = LeadTriageAgent("forja-criativa", cliente=cliente_com(NEUTRO)).handle("oi", "lead-001")

    assert set(r) == {
        "lead_id",
        "pontos",
        "classificacao",
        "observacoes",
        "mensagens",
        "agente_indicado",
        "agentes_vistos",
        "escalar",
        "motivo_escalada",
    }
    assert r["lead_id"] == "lead-001"
    assert r["classificacao"] in {"quente", "morno", "frio"}


def test_enriquecimento_sozinho_nao_faz_lead_quente():
    """
    Site + YouTube achados = 40 pontos, e a régua de quente é 70.
    Existir na internet não é intenção de compra — isso vem da conversa.
    """
    agente = LeadTriageAgent("forja-criativa", cliente=cliente_com(NEUTRO))
    r = agente.handle("oi", "lead-001", enriquecimento=[OK_SITE, OK_YOUTUBE])

    assert r["pontos"] == 40
    assert r["classificacao"] == "morno"
