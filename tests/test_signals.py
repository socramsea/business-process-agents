"""
Prova a extração de sinais da mensagem sem gastar um token da API.
Proves message signal extraction without spending a single API token.

Um cliente falso devolve a resposta que a Claude API devolveria. Assim o teste
roda offline, sempre igual, de graça, e não depende da API estar no ar.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import anthropic

from agents.lead_triage.agent import PESOS_SINAIS, LeadTriageAgent
from agents.lead_triage.signals import (
    AGENTES,
    ESQUEMA_SINAIS,
    MensagemEnricher,
    pontuar_sinais,
)
from tests.fakes import (
    COMPRADOR,
    NEUTRO,
    SAINDO,
    CapturaDeLog,
    ClienteFalso,
    RespostaFalsa,
    cliente_com,
)


def fonte(sinais: dict | None = None) -> MensagemEnricher:
    return MensagemEnricher(cliente=cliente_com(sinais))


# ---- invariantes do schema ----
def test_todo_campo_do_schema_esta_em_required():
    """
    Strict mode da OpenAI rejeita schema com campo em properties fora de required.
    O erro só apareceria numa chamada real — este teste antecipa.
    """
    assert set(ESQUEMA_SINAIS["properties"]) == set(ESQUEMA_SINAIS["required"])


def test_schema_proibe_campo_extra():
    assert ESQUEMA_SINAIS["additionalProperties"] is False


def test_catalogo_de_agentes_esta_no_enum():
    assert ESQUEMA_SINAIS["properties"]["agente_indicado"]["enum"] == list(AGENTES)


def test_indefinido_e_uma_opcao_valida():
    """Sem 'indefinido' no catálogo, o modelo é forçado a chutar um agente."""
    assert "indefinido" in AGENTES


# ---- MensagemEnricher ----
def test_ok_traz_os_sinais():
    r = fonte(COMPRADOR).buscar("tenho 50 mil, fecho essa semana")

    assert r["status"] == "ok"
    assert r["fonte"] == "mensagem"
    assert r["dados"]["orcamento"] is True


def test_mensagem_vazia_nem_chama_a_api():
    cliente = ClienteFalso(RespostaFalsa(COMPRADOR))
    r = MensagemEnricher(cliente=cliente).buscar("   ")

    assert r["status"] == "vazio"
    assert cliente.chamadas == [], "não se paga token pra analisar string vazia"


def test_recusa_do_modelo_nao_quebra():
    """Recusa vem HTTP 200 com content vazio — ler content[0] estouraria aqui."""
    cliente = ClienteFalso(RespostaFalsa(None, stop_reason="refusal"))
    r = MensagemEnricher(cliente=cliente).buscar("qualquer coisa")

    assert r["status"] == "vazio"
    assert "recusou" in r["detalhe"]


def test_a_excecao_da_api_sobe_pro_enriquecer_tratar():
    cliente = ClienteFalso(estoura=anthropic.APIConnectionError(request=None))

    try:
        MensagemEnricher(cliente=cliente).buscar("oi")
    except anthropic.APIConnectionError:
        return
    raise AssertionError("a exceção deveria ter subido")


def test_usa_o_modelo_e_o_schema_certos():
    cliente = ClienteFalso(RespostaFalsa(NEUTRO))
    MensagemEnricher(cliente=cliente).buscar("oi")

    chamada = cliente.chamadas[0]
    assert chamada["model"] == "claude-opus-5"
    formato = chamada["extra_body"]["output_config"]["format"]
    assert formato["type"] == "json_schema"
    assert "descadastro" in formato["schema"]["properties"]


# ---- pontuar_sinais ----
def test_sinais_viram_pontos():
    r = fonte(COMPRADOR).buscar("tenho 50 mil, fecho essa semana")
    pontos, _ = pontuar_sinais(r, PESOS_SINAIS)

    assert pontos == 45  # orcamento 25 + urgencia 20


def test_descadastro_devolve_negativo_de_proposito():
    """
    A soma crua tem que sair negativa daqui. Se zerasse aqui, o -100 não teria
    força pra cancelar os pontos do enriquecimento no total. Quem zera é o agente.
    """
    r = fonte(SAINDO).buscar("me tira do mailing")
    pontos, _ = pontuar_sinais(r, PESOS_SINAIS)

    assert pontos == -100


def test_resumo_vira_observacao_pro_vendedor():
    r = fonte(COMPRADOR).buscar("tenho 50 mil")
    _, observacoes = pontuar_sinais(r, PESOS_SINAIS)

    assert "quer fechar identidade visual esta semana" in observacoes[0]


def test_falha_nao_pontua_mas_fala():
    falha = {
        "fonte": "mensagem",
        "status": "falha",
        "dados": {},
        "detalhe": "APIConnectionError: caiu",
    }
    pontos, observacoes = pontuar_sinais(falha, PESOS_SINAIS)

    assert pontos == 0
    assert "não consegui analisar" in observacoes[0]


# ---- LeadTriageAgent ponta a ponta ----
def test_a_mensagem_finalmente_muda_a_nota():
    """O teste que estava vermelho desde o stub."""
    comprador = LeadTriageAgent("forja", cliente=ClienteFalso(RespostaFalsa(COMPRADOR)))
    saindo = LeadTriageAgent("forja", cliente=ClienteFalso(RespostaFalsa(SAINDO)))

    r_comprador = comprador.handle("tenho 50 mil, fecho essa semana", "lead-001")
    r_saindo = saindo.handle("me tira do mailing", "lead-002")

    assert r_comprador["pontos"] > r_saindo["pontos"]


def test_lead_com_sinal_e_site_chega_a_quente():
    """Só agora 'quente' é alcançável: 45 da conversa + 25 do site = 70."""
    ok_site = {
        "fonte": "site",
        "status": "ok",
        "dados": {"titulo": "Forja Criativa"},
        "detalhe": None,
    }
    agente = LeadTriageAgent("forja", cliente=ClienteFalso(RespostaFalsa(COMPRADOR)))

    r = agente.handle("tenho 50 mil, fecho essa semana", "lead-001", enriquecimento=[ok_site])

    assert r["pontos"] == 70
    assert r["classificacao"] == "quente"


def test_descadastro_vence_o_enriquecimento():
    """Site bonito não compra quem pediu pra sair."""
    ok_site = {
        "fonte": "site",
        "status": "ok",
        "dados": {"titulo": "Forja Criativa"},
        "detalhe": None,
    }
    agente = LeadTriageAgent("forja", cliente=ClienteFalso(RespostaFalsa(SAINDO)))

    r = agente.handle("me tira do mailing", "lead-002", enriquecimento=[ok_site])

    assert r["pontos"] == 0
    assert r["classificacao"] == "frio"


def test_llm_fora_do_ar_nao_derruba_o_atendimento():
    cliente = ClienteFalso(estoura=anthropic.APIConnectionError(request=None))
    agente = LeadTriageAgent("forja", cliente=cliente)

    r = agente.handle("tenho 50 mil", "lead-001")

    assert r["classificacao"] == "frio"
    assert any("não consegui analisar" in o for o in r["observacoes"])


# ---- captura de consumo (Etapa 1) ----
class ConsumoFalso:
    def __init__(self, entrada: int, saida: int):
        self.input_tokens = entrada
        self.output_tokens = saida


def test_registra_tokens_e_custo():
    """O consumo já vinha na resposta e era descartado."""
    resposta = RespostaFalsa(NEUTRO)
    resposta.usage = ConsumoFalso(1000, 200)
    resposta._request_id = "req_abc123"

    with CapturaDeLog() as log:
        MensagemEnricher(cliente=ClienteFalso(resposta)).buscar("tenho uma clinica")

    registros = log.evento("llm consultado")
    assert len(registros) == 1

    r = registros[0]
    assert r.tokens_entrada == 1000
    assert r.tokens_saida == 200
    # 1000 * 5/1M + 200 * 25/1M = 0.005 + 0.005
    assert r.custo_usd == 0.01
    assert r.request_id == "req_abc123"
    assert r.modelo == "claude-opus-5"


def test_resposta_sem_usage_nao_quebra_o_atendimento():
    """
    Log de custo não pode derrubar o atendimento de um lead. Sem `usage` —
    mudança de SDK, dublê antigo — grava zero e segue.
    """
    with CapturaDeLog() as log:
        r = MensagemEnricher(cliente=ClienteFalso(RespostaFalsa(NEUTRO))).buscar("oi")

    assert r["status"] == "ok", "a classificação segue mesmo sem consumo"

    registro = log.evento("llm consultado")[0]
    assert registro.tokens_entrada == 0 and registro.tokens_saida == 0


def test_mensagem_vazia_nao_registra_consumo():
    """Não há chamada, logo não há consumo a registrar."""
    with CapturaDeLog() as log:
        MensagemEnricher(cliente=ClienteFalso(RespostaFalsa(NEUTRO))).buscar("   ")

    assert log.evento("llm consultado") == []
