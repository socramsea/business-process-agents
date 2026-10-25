"""
Prova a migração 0001 — a primeira da Empresa Digital.
Proves migration 0001 — the Digital Company's first.

A maior parte roda SEM banco nenhum: o modo offline do Alembic (`--sql`) emite
o DDL sem abrir conexão. Aplicar de verdade contra Postgres é trabalho do CI e
dos testes de contrato; aqui se pega o erro que aparece antes disso — cabeça
dupla, migração sem volta, coluna que sumiu.
Most of this runs with no database at all, via Alembic's offline mode.
"""

import subprocess
import sys
from pathlib import Path

from alembic.config import Config as ConfigAlembic
from alembic.script import ScriptDirectory

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))

# URL falsa: o modo offline gera o DDL sem conectar, então nenhum banco precisa
# existir para este arquivo rodar.
URL_DE_MENTIRA = "postgresql://ninguem@lugar-nenhum/vazio"

TABELAS = ("pessoa", "identidade", "mensagem")


def scripts() -> ScriptDirectory:
    return ScriptDirectory.from_config(ConfigAlembic(str(RAIZ / "alembic.ini")))


def ddl() -> str:
    saida = subprocess.run(
        ["alembic", "-x", f"url={URL_DE_MENTIRA}", "upgrade", "head", "--sql"],
        cwd=RAIZ,
        check=True,
        capture_output=True,
        text=True,
    )
    return saida.stdout.lower()


def ddl_da_volta() -> str:
    saida = subprocess.run(
        ["alembic", "-x", f"url={URL_DE_MENTIRA}", "downgrade", "head:base", "--sql"],
        cwd=RAIZ,
        check=True,
        capture_output=True,
        text=True,
    )
    return saida.stdout.lower()


# ---- a cadeia ----
def test_a_0001_e_a_unica_cabeca():
    """
    Duas cabeças = duas migrações criadas na mesma base sem merge. O
    `alembic upgrade head` falha na hora — mas falha no deploy. Aqui falha antes.
    """
    assert scripts().get_heads() == ["0001"]


def test_a_cadeia_comeca_no_nada():
    revisoes = list(scripts().walk_revisions())

    assert len(revisoes) == 1, "a Fase A tem exatamente uma migração"
    assert revisoes[0].revision == "0001"
    assert revisoes[0].down_revision is None, "a primeira migração não vem de outra"


def test_a_migracao_sabe_voltar():
    """
    Migração sem downgrade é caminho de mão única: descobre-se que precisa
    voltar exatamente quando não dá mais.
    """
    for revisao in scripts().walk_revisions():
        assert callable(getattr(revisao.module, "upgrade", None))
        assert callable(getattr(revisao.module, "downgrade", None))


# ---- os três domínios ----
def test_cria_os_tres_dominios_aprovados():
    gerado = ddl()

    for tabela in TABELAS:
        assert f"create table {tabela}" in gerado


def test_NAO_cria_a_antiga_tabela_lead():
    """
    O ponto inteiro desta migração nascer de novo. `lead` é um estado da relação
    num momento, não o que a pessoa é — modelar a pessoa como registro é o que a
    constituição proíbe (§1). A migração antiga foi descartada sem entrar no
    histórico, e este teste é o que impede ela de voltar por conveniência.
    """
    assert "create table lead" not in ddl()


def test_pessoa_tem_id_proprio_e_e_a_chave_com_a_empresa():
    """
    O id da Pessoa é interno e opaco (P-1.1), e a empresa entra na chave porque
    a mesma pessoa em duas Empresas Digitais são duas Pessoas (P-1.5).
    """
    gerado = ddl()

    assert "pk_pessoa" in gerado
    assert "primary key (empresa_id, id)" in gerado


def test_identidade_e_separada_de_pessoa_e_aponta_para_ela():
    gerado = ddl()

    assert "create table identidade" in gerado
    assert "fk_identidade_pessoa" in gerado
    # A chave é (empresa, canal, valor): é ela que impede duas Pessoas
    # reivindicarem o mesmo identificador — a corrupção sem conserto.
    assert "primary key (empresa_id, canal, valor)" in gerado


def test_identidade_nasce_nao_verificada():
    """
    Ter chegado por um canal não verifica nada: prova que alguém usou aquele
    endereço, não quem (P-1.2). O padrão do banco tem que ser falso.
    """
    gerado = ddl()

    assert "verificada" in gerado
    assert "default false" in gerado


def test_mensagem_guarda_texto_canal_e_quem_falou():
    gerado = ddl()

    for coluna in ("texto", "canal", "quem_falou", "quando", "pessoa_id"):
        assert coluna in gerado, f"a mensagem não guarda {coluna}"


def test_quem_falou_e_fechado_no_banco():
    """Valor novo aqui é decisão de arquitetura, não digitação."""
    gerado = ddl()

    assert "ck_mensagem_quem_falou" in gerado
    for quem in ("'pessoa'", "'funcionario'", "'humano'"):
        assert quem in gerado


def test_canal_NAO_e_fechado_no_banco():
    """
    O oposto de `quem_falou`, e de propósito: canal novo não pode exigir
    migração, senão adicionar Instagram vira mudança de schema e a promessa de
    independência de canal (P2) é falsa.
    """
    assert "ck_mensagem_canal" not in ddl()


def test_NAO_existe_tabela_conversa():
    """
    Conversa é a sequência de Mensagens, não um objeto com começo e fim (C-2.1).
    Inventar sessão exigiria uma regra de corte arbitrária que viraria dado
    errado.
    """
    assert "create table conversa" not in ddl()


def test_a_conversa_tem_indice_proprio():
    """A leitura que todo Funcionário faz precisa ser barata."""
    assert "ix_mensagem_conversa" in ddl()


def test_deduplicacao_por_entrega_do_canal():
    """
    Um canal reentregando por timeout inventaria conversa que não houve. Índice
    parcial porque `externo` é opcional e NULL não deve colidir.
    """
    gerado = ddl()

    assert "ux_mensagem_externo" in gerado
    assert "externo is not null" in gerado


# ---- a volta ----
def test_o_downgrade_derruba_os_tres_dominios():
    volta = ddl_da_volta()

    for tabela in TABELAS:
        assert f"drop table {tabela}" in volta


def test_a_volta_respeita_a_ordem_das_dependencias():
    """
    `mensagem` e `identidade` apontam para `pessoa`. Derrubar `pessoa` primeiro
    quebraria a chave estrangeira — o downgrade falharia no meio, deixando o
    banco num estado que nenhuma migração descreve.
    """
    volta = ddl_da_volta()

    assert volta.index("drop table mensagem") < volta.index("drop table pessoa")
    assert volta.index("drop table identidade") < volta.index("drop table pessoa")
