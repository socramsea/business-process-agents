"""
Prova o cliente da Evolution sem instância e sem rede.
Proves the Evolution client with no instance and no network.

CLASSIFICAÇÃO OBRIGATÓRIA NESTE ARQUIVO:

  test_...            FATO — afirma só o comportamento do NOSSO código diante
                      de uma entrada dada. Vale mesmo que a Evolution seja
                      completamente diferente do que supomos.

  test_HIPOTESE_...   Afirma algo sobre a EVOLUTION que nunca foi observado.
                      Verde aqui NÃO é validação: se a suposição estiver
                      errada, o teste passa e a produção falha.

Documentação é hipótese; verdade é execução. Havendo divergência entre a
documentação e a resposta real da API, a documentação está errada e É O TESTE
QUE MUDA — nunca o contrário.
Documentation is hypothesis; execution is truth. On divergence, the test changes.

Para promover HIPÓTESE a FATO basta uma chamada real:
    python3 -c "import sys,json;sys.path.insert(0,'.')
    from core.evolution import Evolution; print(json.dumps(Evolution().bruto(),indent=2))"
"""

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import httpx
import pytest

from core.evolution import Evolution, _normalizar, _registros

# Os três fixtures abaixo são HIPÓTESE: formato de registro tirado da
# documentação e de SDK de terceiro, nunca observado numa resposta real.
RECEBIDA = {
    "key": {"remoteJid": "5511999990000@s.whatsapp.net", "fromMe": False, "id": "MSG1"},
    "pushName": "Marcos",
    "message": {"conversation": "tenho uma clinica em Botafogo"},
    "messageTimestamp": 1780000000,
}
ENVIADA = {
    "key": {"remoteJid": "5511999990000@s.whatsapp.net", "fromMe": True, "id": "MSG2"},
    "message": {"conversation": "oi, tudo bem?"},
}
AUDIO = {
    "key": {"remoteJid": "5511888880000@s.whatsapp.net", "fromMe": False, "id": "MSG3"},
    "message": {"audioMessage": {"url": "..."}},
}


def montar(carga: object, status: int = 200) -> Evolution:
    def responder(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status, text=json.dumps(carga))

    return Evolution(
        url="https://evo.exemplo",
        chave="k",
        instancia="i",
        transport=httpx.MockTransport(responder),
    )


# ---- _registros: as duas formas de envelope ----
def test_aceita_lista_nua():
    assert _registros([RECEBIDA]) == [RECEBIDA]


def test_aceita_envelope_aninhado():
    """
    FATO sobre o parser: ele extrai destes três formatos.
    Ressalva: a ESCOLHA dos três é hipótese. Se o real for um quarto formato,
    este teste passa e `_registros` devolve lista vazia em produção.
    """
    assert _registros({"messages": {"records": [RECEBIDA]}}) == [RECEBIDA]
    assert _registros({"messages": [RECEBIDA]}) == [RECEBIDA]
    assert _registros({"records": [RECEBIDA]}) == [RECEBIDA]


def test_formato_desconhecido_devolve_vazio_em_vez_de_quebrar():
    """Envelope inesperado não pode derrubar o polling — devolve nada e segue."""
    assert _registros({"algo": "inesperado"}) == []
    assert _registros("texto") == []
    assert _registros(None) == []


# ---- _normalizar ----
def test_HIPOTESE_mensagem_recebida_vira_o_minimo_que_o_pipeline_usa():
    # HIPÓTESE: os nomes de campo key.remoteJid, key.fromMe, key.id, pushName,
    # message.conversation e messageTimestamp vêm de documentação e de SDK de
    # terceiro. Nenhum foi observado numa resposta real.
    # FALTA: uma saída de Evolution.bruto() de instância real mostrando os
    # nomes de verdade.
    n = _normalizar(RECEBIDA)

    assert n == {
        "id": "MSG1",
        "telefone": "5511999990000",
        "remote_jid": "5511999990000@s.whatsapp.net",
        "texto": "tenho uma clinica em Botafogo",
        "nome": "Marcos",
        "quando": 1780000000,
    }


def test_HIPOTESE_telefone_sai_sem_o_sufixo_do_jid():
    """
    HIPÓTESE, e a mais frágil do arquivo: que remoteJid seja
    'telefone@s.whatsapp.net' E que esse telefone seja o número real.
    A issue #1916 do projeto se chama literalmente '[BUG] remoteJid is
    different than the real whatsapp number'.
    FALTA: comparar o remoteJid de uma mensagem real com o número que a enviou.
    Se divergirem, lead_id extraído daqui identifica a pessoa errada.
    """
    assert _normalizar(RECEBIDA)["telefone"] == "5511999990000"


def test_HIPOTESE_mensagem_que_nos_enviamos_e_ignorada():
    """
    HIPÓTESE: que o campo se chame `fromMe` e seja booleano.
    FALTA: um registro real de mensagem enviada pela própria conta.
    Se o nome for outro, nossas respostas entram no pipeline como se fossem
    mensagens do lead.
    """
    assert _normalizar(ENVIADA) is None


def test_HIPOTESE_audio_e_ignorado():
    """
    HIPÓTESE: que áudio venha em message.audioMessage e SEM
    message.conversation.
    FALTA: um áudio real recebido. Se áudio trouxer conversation preenchido
    com legenda ou transcrição, ele entra no pipeline como texto do lead.
    """
    assert _normalizar(AUDIO) is None


def test_registro_torto_nao_quebra():
    assert _normalizar({}) is None
    assert _normalizar({"key": "nao e dict"}) is None
    assert _normalizar({"key": {"fromMe": False}, "message": {"conversation": "  "}}) is None


# ---- o cliente monta o pedido certo ----
def test_HIPOTESE_manda_apikey_e_o_caminho_da_instancia():
    # HIPÓTESE em três partes, e uma delas é pior que as outras:
    #   caminho /chat/findMessages/{instancia}  — documentado
    #   header  apikey                          — documentado
    #   corpo   {"where": {}} traz TODAS         — SEM FONTE, inferência minha
    # FALTA: uma chamada real. HTTP 200 promove caminho e header. O `where`
    # vazio exige comparar o resultado com e sem filtro.
    capturado = {}

    def responder(req: httpx.Request) -> httpx.Response:
        capturado["url"] = str(req.url)
        capturado["apikey"] = req.headers.get("apikey")
        capturado["corpo"] = json.loads(req.content)
        return httpx.Response(200, text="[]")

    Evolution(
        url="https://evo.exemplo",
        chave="segredo",
        instancia="forja",
        transport=httpx.MockTransport(responder),
    ).mensagens()

    assert capturado["url"] == "https://evo.exemplo/chat/findMessages/forja"
    assert capturado["apikey"] == "segredo"
    assert capturado["corpo"] == {"where": {}}


def test_HIPOTESE_filtro_por_conversa_entra_no_corpo():
    # HIPÓTESE: corpo {"where": {"key": {"remoteJid": ...}}}. Documentado, e a
    # issue #1632 do projeto relata este filtro não funcionando em algumas
    # versões — ou seja, a documentação já diverge do comportamento relatado.
    # FALTA: chamar com filtro e conferir que só volta a conversa pedida.
    capturado = {}

    def responder(req: httpx.Request) -> httpx.Response:
        capturado["corpo"] = json.loads(req.content)
        return httpx.Response(200, text="[]")

    Evolution(
        url="https://e", chave="k", instancia="i", transport=httpx.MockTransport(responder)
    ).mensagens("5511999990000@s.whatsapp.net")

    assert capturado["corpo"] == {
        "where": {"key": {"remoteJid": "5511999990000@s.whatsapp.net"}}
    }


def test_HIPOTESE_filtra_enviadas_e_audio_numa_carga_mista():
    # HIPÓTESE: herda o formato de registro dos três fixtures acima.
    # FALTA: a mesma saída real de bruto() que promove os anteriores.
    recebidas = montar([RECEBIDA, ENVIADA, AUDIO]).mensagens()

    assert len(recebidas) == 1
    assert recebidas[0]["id"] == "MSG1"


def test_bruto_devolve_sem_interpretar():
    """Existe para descobrir o formato real; não pode normalizar nada."""
    carga = {"formato": "que eu nao previ", "messages": {"records": []}}

    assert montar(carga).bruto() == carga


def test_erro_http_sobe():
    """Quem trata é o chamador, igual aos enrichers."""
    with pytest.raises(httpx.HTTPStatusError):
        montar([], status=500).mensagens()


def test_config_ausente_falha_antes_de_chamar_a_rede():
    with pytest.raises(ValueError, match="EVOLUTION_URL"):
        Evolution(url="", chave="", instancia="").mensagens()
