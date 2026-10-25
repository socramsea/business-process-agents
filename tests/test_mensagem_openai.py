"""
Prova o enricher da OpenAI offline — e que ele é intercambiável com o da Anthropic.
Proves the OpenAI enricher offline — and that it's swappable with the Anthropic one.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import openai

from agents.lead_triage.agent import PESOS_SINAIS
from agents.lead_triage.signals import (
    AGENTES,
    ESQUEMA_SINAIS,
    INSTRUCAO,
    MensagemEnricher,
    pontuar_sinais,
)
from core.base_enricher import enriquecer
from enrichers.mensagem_openai import MensagemEnricherOpenAI
from tests.fakes import (
    COMPRADOR,
    NEUTRO,
    SAINDO,
    ClienteOpenAIFalso,
    RespostaOpenAIFalsa,
    cliente_com,
)


def fonte(sinais: dict | None = None, **kwargs: object) -> MensagemEnricherOpenAI:
    resposta = RespostaOpenAIFalsa(sinais, **kwargs)  # type: ignore[arg-type]
    return MensagemEnricherOpenAI(cliente=ClienteOpenAIFalso(resposta))


# ---- os quatro caminhos ----
def test_ok_traz_os_sinais():
    r = fonte(COMPRADOR).buscar("tenho 50 mil, fecho essa semana")

    assert r["status"] == "ok"
    assert r["fonte"] == "mensagem"
    assert r["detalhe"] is None
    assert r["dados"]["orcamento"] is True


def test_mensagem_vazia_nem_chama_a_api():
    cliente = ClienteOpenAIFalso(RespostaOpenAIFalsa(COMPRADOR))
    r = MensagemEnricherOpenAI(cliente=cliente).buscar("   ")

    assert r["status"] == "vazio"
    assert cliente.chamadas == [], "não se paga token pra analisar string vazia"


def test_recusa_do_modelo_nao_quebra():
    """
    Na OpenAI a recusa vem em message.refusal e o content vem None.
    Ler .content direto passaria None pro json.loads e estouraria.
    """
    r = fonte(None, refusal="não posso analisar isso").buscar("qualquer coisa")

    assert r["status"] == "vazio"
    assert "recusou" in r["detalhe"]


def test_resposta_cortada_no_teto_de_tokens():
    """finish_reason 'length' = JSON truncado. Dizer isso é melhor que JSONDecodeError."""
    r = fonte(COMPRADOR, finish_reason="length").buscar("uma mensagem enorme")

    assert r["status"] == "vazio"
    assert "cortada" in r["detalhe"]


def test_a_excecao_sobe_pro_enriquecer_tratar():
    cliente = ClienteOpenAIFalso(estoura=openai.APIConnectionError(request=None))

    try:
        MensagemEnricherOpenAI(cliente=cliente).buscar("oi")
    except openai.APIConnectionError:
        return
    raise AssertionError("a exceção deveria ter subido")


def test_falha_da_openai_nao_derruba_o_pipeline():
    cliente = ClienteOpenAIFalso(estoura=openai.APIConnectionError(request=None))

    resultados = enriquecer("oi", [MensagemEnricherOpenAI(cliente=cliente)])

    assert resultados[0]["status"] == "falha"
    assert resultados[0]["fonte"] == "mensagem"


# ---- a chamada monta o pedido certo ----
def test_usa_structured_outputs_estrito():
    cliente = ClienteOpenAIFalso(RespostaOpenAIFalsa(NEUTRO))
    MensagemEnricherOpenAI(cliente=cliente).buscar("oi")

    formato = cliente.chamadas[0]["response_format"]
    assert formato["type"] == "json_schema"
    assert formato["json_schema"]["strict"] is True
    # strict exige additionalProperties false e todos os campos em required.
    assert formato["json_schema"]["schema"]["additionalProperties"] is False


def test_o_catalogo_de_agentes_chega_no_pedido():
    """O enum viaja até a API: o modelo não consegue inventar um agente."""
    cliente = ClienteOpenAIFalso(RespostaOpenAIFalsa(NEUTRO))
    MensagemEnricherOpenAI(cliente=cliente).buscar("oi")

    schema = cliente.chamadas[0]["response_format"]["json_schema"]["schema"]

    assert schema["properties"]["agente_indicado"]["enum"] == list(AGENTES)
    assert "agente_indicado" in schema["required"]


def test_manda_a_mesma_instrucao_da_anthropic():
    """Prompt diferente compararia prompts, não provedores."""
    cliente = ClienteOpenAIFalso(RespostaOpenAIFalsa(NEUTRO))
    MensagemEnricherOpenAI(cliente=cliente).buscar("oi")

    mensagens = cliente.chamadas[0]["messages"]
    assert mensagens[0] == {"role": "system", "content": INSTRUCAO}
    assert mensagens[1] == {"role": "user", "content": "oi"}


def test_manda_o_mesmo_schema_da_anthropic():
    cliente = ClienteOpenAIFalso(RespostaOpenAIFalsa(NEUTRO))
    MensagemEnricherOpenAI(cliente=cliente).buscar("oi")

    enviado = cliente.chamadas[0]["response_format"]["json_schema"]["schema"]
    assert enviado is ESQUEMA_SINAIS


# ---- o que este marco realmente prova ----
def test_os_dois_provedores_sao_intercambiaveis():
    """
    Mesma mensagem, mesmos sinais, provedores diferentes: saída idêntica.
    É o contrato de interface funcionando — trocar o provedor por baixo não
    muda nada acima.
    """
    anthropic_r = MensagemEnricher(cliente=cliente_com(COMPRADOR)).buscar("tenho 50 mil")
    openai_r = fonte(COMPRADOR).buscar("tenho 50 mil")

    assert anthropic_r == openai_r


def test_pontuam_igual_na_mesma_regua():
    """A régua do tenant não precisa saber qual provedor respondeu."""
    for sinais in (COMPRADOR, SAINDO, NEUTRO):
        a = pontuar_sinais(MensagemEnricher(cliente=cliente_com(sinais)).buscar("x"), PESOS_SINAIS)
        o = pontuar_sinais(fonte(sinais).buscar("x"), PESOS_SINAIS)

        assert a == o, f"divergiu em {sinais['resumo']!r}"
