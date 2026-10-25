"""
Prova que o lead que volta é reconhecido, e que a nota é do relacionamento.
Proves the returning lead is recognized and the score is about the relationship.

Nenhum relógio: o instante entra por parâmetro em todo teste.
No clock anywhere — the timestamp is a parameter in every test.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from agents.lead_triage.acumulo import ESTADO_VAZIO, acumular, agentes_distintos
from agents.lead_triage.agent import LeadTriageAgent
from core.memoria import MemoriaEmMemoria, MemoriaSQLite
from tests.fakes import ClienteFalso, RespostaFalsa

T1 = "2026-07-01T10:00:00+00:00"
T2 = "2026-07-08T10:00:00+00:00"
T3 = "2026-07-15T10:00:00+00:00"


def sinais(**kwargs: object) -> dict:
    base = {
        "orcamento": False,
        "urgencia": False,
        "autoridade": False,
        "descadastro": False,
        "agente_indicado": "indefinido",
        "resumo": "",
    }
    return {**base, **kwargs}


# ---- acumular: as regras que o Marcos arbitrou ----
def test_orcamento_e_autoridade_travam_em_true():
    """São fatos sobre a pessoa. Quem é dono na segunda continua dono na quinta."""
    e = acumular(ESTADO_VAZIO, sinais(orcamento=True, autoridade=True), T1)
    e = acumular(e, sinais(orcamento=False, autoridade=False), T2)

    assert e["sinais"]["orcamento"] is True
    assert e["sinais"]["autoridade"] is True


def test_urgencia_nao_acumula():
    """
    Urgência que trava é urgência falsa: 'preciso pra outubro' dito em julho
    viraria lead quente em dezembro, e o vendedor priorizaria quem já desistiu.
    """
    e = acumular(ESTADO_VAZIO, sinais(urgencia=True), T1)
    assert e["sinais"]["urgencia"] is True

    e = acumular(e, sinais(urgencia=False), T2)
    assert e["sinais"]["urgencia"] is False, "vale sempre a última mensagem"


def test_descadastro_trava_e_nao_volta():
    e = acumular(ESTADO_VAZIO, sinais(descadastro=True), T1)
    e = acumular(e, sinais(descadastro=False, orcamento=True), T2)

    assert e["sinais"]["descadastro"] is True, "quem pediu pra sair, saiu"


def test_agente_indicado_guarda_o_ultimo_como_decisao():
    e = acumular(ESTADO_VAZIO, sinais(agente_indicado="atendimento"), T1)
    e = acumular(e, sinais(agente_indicado="comercial"), T2)

    assert e["agente_indicado"] == "comercial"


def test_agente_indicado_guarda_todos_os_vistos():
    """
    Sobrescrever jogaria fora informação já paga pra extrair. Lead com dor de
    atendimento numa mensagem e comercial na outra TEM os dois problemas.
    """
    e = acumular(ESTADO_VAZIO, sinais(agente_indicado="atendimento"), T1)
    e = acumular(e, sinais(agente_indicado="comercial"), T2)

    assert agentes_distintos(e) == ["atendimento", "comercial"]
    assert [v["quando"] for v in e["agentes_vistos"]] == [T1, T2]


def test_indefinido_nao_entra_na_lista_nem_apaga_a_decisao():
    e = acumular(ESTADO_VAZIO, sinais(agente_indicado="comercial"), T1)
    e = acumular(e, sinais(agente_indicado="indefinido"), T2)

    assert e["agente_indicado"] == "comercial", "indefinido não desfaz o que já se sabia"
    assert agentes_distintos(e) == ["comercial"]


def test_agente_repetido_nao_duplica_na_lista_de_distintos():
    e = acumular(ESTADO_VAZIO, sinais(agente_indicado="comercial"), T1)
    e = acumular(e, sinais(agente_indicado="comercial"), T2)

    assert agentes_distintos(e) == ["comercial"]
    assert len(e["agentes_vistos"]) == 2, "o histórico guarda as duas ocorrências"


def test_conta_mensagens():
    e = acumular(ESTADO_VAZIO, sinais(), T1)
    e = acumular(e, sinais(), T2)
    e = acumular(e, sinais(), T3)

    assert e["mensagens"] == 3


def test_guarda_quando_cada_sinal_travou():
    """Não é usado em regra nenhuma hoje — está aqui pra validade não exigir migração."""
    e = acumular(ESTADO_VAZIO, sinais(orcamento=True), T1)
    e = acumular(e, sinais(autoridade=True), T2)

    assert e["travado_em"] == {"orcamento": T1, "autoridade": T2}


def test_acumular_nao_muta_o_estado_anterior():
    anterior = acumular(ESTADO_VAZIO, sinais(orcamento=True), T1)
    copia = {**anterior, "sinais": dict(anterior["sinais"])}

    acumular(anterior, sinais(autoridade=True), T2)

    assert anterior["sinais"] == copia["sinais"], "função pura não mexe na entrada"


# ---- o contrato: as TRÊS implementações se comportam igual ----
# A fixture `memoria` (tests/conftest.py) roda cada teste abaixo uma vez por
# implementação: em-memoria, sqlite e postgres. A que não puder rodar aparece
# como SKIPPED com o motivo — nunca some em silêncio de dentro de um `for`.
# Each test below runs once per implementation; a missing one shows as SKIPPED.
def test_memoria_vazia_devolve_dicionario_vazio(memoria):
    """Lead novo não é erro — é a primeira mensagem de alguém."""
    assert memoria.carregar("t1", "nunca-visto") == {}


def test_guarda_e_devolve(memoria):
    memoria.salvar("t1", "lead-1", {"mensagens": 2})

    assert memoria.carregar("t1", "lead-1") == {"mensagens": 2}


def test_tenant_separa_leads_de_mesmo_id(memoria):
    """Chave errada é a migração mais cara que existe. O tenant entra desde já."""
    memoria.salvar("cliente-a", "lead-1", {"mensagens": 9})

    assert memoria.carregar("cliente-b", "lead-1") == {}


def test_salvar_duas_vezes_sobrescreve(memoria):
    memoria.salvar("t1", "lead-1", {"mensagens": 1})
    memoria.salvar("t1", "lead-1", {"mensagens": 2})

    assert memoria.carregar("t1", "lead-1")["mensagens"] == 2


def test_carregar_devolve_copia(memoria):
    """
    Mutar o que veio do carregar não pode alterar o guardado. No SQLite e no
    Postgres sai de graça (a leitura desserializa um objeto novo); na
    MemoriaEmMemoria precisa de cópia explícita. É contrato, não detalhe de uma.
    """
    memoria.salvar("t1", "lead-1", {"mensagens": 1})

    carregado = memoria.carregar("t1", "lead-1")
    carregado["mensagens"] = 99

    assert memoria.carregar("t1", "lead-1")["mensagens"] == 1


def test_estado_aninhado_sobrevive_a_ida_e_volta(memoria):
    """
    O estado real do lead é aninhado — `sinais`, `travado_em`, `agentes_vistos`
    com lista de dicionário dentro. O JSONB do Postgres e o TEXT do SQLite
    guardam isso por caminhos diferentes; o que volta tem que ser igual nos dois.
    The real lead state is nested; both backends must round-trip it identically.
    """
    estado = {
        "mensagens": 2,
        "sinais": {"orcamento": True, "urgencia": False},
        "travado_em": {"orcamento": T1},
        "agentes_vistos": [{"agente": "comercial", "quando": T1}],
        "visto_em": T2,
    }
    memoria.salvar("t1", "lead-1", estado)

    assert memoria.carregar("t1", "lead-1") == estado


# ---- comportamento de uma implementação só ----
def test_sqlite_sobrevive_a_reabertura(tmp_path: Path):
    """O que a MemoriaEmMemoria não faz e o SQLite faz: sobreviver ao processo."""
    caminho = tmp_path / "persiste.db"
    MemoriaSQLite(caminho).salvar("t1", "lead-1", {"mensagens": 3})

    assert MemoriaSQLite(caminho).carregar("t1", "lead-1") == {"mensagens": 3}


# ---- o agente ponta a ponta: o lead que volta ----
def agente(memoria: MemoriaEmMemoria, **sinais_do_modelo: object) -> LeadTriageAgent:
    return LeadTriageAgent(
        "forja",
        cliente=ClienteFalso(RespostaFalsa(sinais(**sinais_do_modelo))),
        memoria=memoria,
    )


def test_o_lead_que_volta_e_reconhecido():
    """O buraco central: até aqui cada mensagem apagava a anterior."""
    m = MemoriaEmMemoria()

    primeira = agente(m, orcamento=True).handle("tenho 50 mil", "lead-1", quando=T1)
    segunda = agente(m, urgencia=True).handle("preciso sexta", "lead-1", quando=T2)

    assert primeira["mensagens"] == 1
    assert segunda["mensagens"] == 2


def test_sinais_de_mensagens_diferentes_somam():
    """
    'Tenho 50 mil' na segunda + 'preciso sexta' na quinta = 45 pontos.
    Sem acumulação eram dois leads de 25 e 20, nenhum deles perto de quente.
    """
    m = MemoriaEmMemoria()

    primeira = agente(m, orcamento=True).handle("tenho 50 mil", "lead-1", quando=T1)
    segunda = agente(m, urgencia=True).handle("preciso sexta", "lead-1", quando=T2)

    assert primeira["pontos"] == 25
    assert segunda["pontos"] == 45, "orcamento travado + urgencia da vez"


def test_leads_diferentes_nao_se_misturam():
    m = MemoriaEmMemoria()

    agente(m, orcamento=True).handle("tenho 50 mil", "lead-1", quando=T1)
    outro = agente(m, urgencia=True).handle("preciso sexta", "lead-2", quando=T2)

    assert outro["pontos"] == 20, "o lead-2 não herda o orçamento do lead-1"


def test_falha_na_extracao_nao_apaga_o_que_ja_se_sabia():
    """
    LLM fora do ar na terceira mensagem não pode zerar um lead que já disse
    que tem verba. O acumulado é fato; a falha é da chamada de agora.
    """
    import anthropic

    m = MemoriaEmMemoria()
    agente(m, orcamento=True, autoridade=True).handle("tenho 50 mil", "lead-1", quando=T1)

    caiu = LeadTriageAgent(
        "forja",
        cliente=ClienteFalso(estoura=anthropic.APIConnectionError(request=None)),
        memoria=m,
    ).handle("e aí?", "lead-1", quando=T2)

    assert caiu["pontos"] == 40, "orcamento 25 + autoridade 15 seguem valendo"
    assert any("não consegui analisar" in o for o in caiu["observacoes"])


def test_duas_dores_aparecem_no_resultado():
    m = MemoriaEmMemoria()

    agente(m, agente_indicado="atendimento").handle("não dou conta", "lead-1", quando=T1)
    r = agente(m, agente_indicado="comercial").handle("perco venda", "lead-1", quando=T2)

    assert r["agente_indicado"] == "comercial"
    assert r["agentes_vistos"] == ["atendimento", "comercial"]


def test_descadastro_em_qualquer_mensagem_zera_pra_sempre():
    m = MemoriaEmMemoria()

    agente(m, orcamento=True, autoridade=True).handle("tenho 50 mil", "lead-1", quando=T1)
    saiu = agente(m, descadastro=True).handle("me tira do mailing", "lead-1", quando=T2)
    depois = agente(m, orcamento=True).handle("mudei de ideia?", "lead-1", quando=T3)

    assert saiu["pontos"] == 0
    assert depois["pontos"] == 0, "descadastro travado vence o que vier depois"


def test_sqlite_aguenta_threads_simultaneas(tmp_path: Path):
    """
    A conexão é compartilhada entre chamadas. Sem lock, duas threads gravando
    ao mesmo tempo dão 'recursive use of cursors' ou corrompem a escrita.
    """
    from concurrent.futures import ThreadPoolExecutor

    m = MemoriaSQLite(tmp_path / "concorrente.db")

    def grava(n: int) -> None:
        m.salvar("t1", f"lead-{n}", {"mensagens": n})

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(grava, range(40)))

    assert all(m.carregar("t1", f"lead-{n}")["mensagens"] == n for n in range(40))
