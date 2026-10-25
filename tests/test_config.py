"""
Prova que configuração faltando falha na PARTIDA, dizendo tudo que falta.
Proves missing config fails at BOOT, naming everything that's missing.

Nada aqui toca rede nem banco: config é leitura de ambiente, e ambiente o
monkeypatch controla inteiro.
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.config import (
    ConfiguracaoInvalida,
    banco_url,
    banco_url_de_teste,
    exigir,
    ler,
    url_para_sqlalchemy,
)


# ---- ler ----
def test_variavel_ausente_vira_string_vazia(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NAO_EXISTE", raising=False)

    assert ler("NAO_EXISTE") == ""


def test_variavel_vazia_e_ausente_sao_a_mesma_coisa(monkeypatch: pytest.MonkeyPatch):
    """`EVOLUTION_URL=` mal preenchido no .env não pode passar por configurado."""
    monkeypatch.setenv("VAZIA", "")

    assert ler("VAZIA") == ler("TAMBEM_NAO_EXISTE") == ""


def test_espaco_em_volta_e_removido(monkeypatch: pytest.MonkeyPatch):
    """Copiar chave de um painel web traz espaço junto mais vezes do que se admite."""
    monkeypatch.setenv("COM_ESPACO", "  valor  ")

    assert ler("COM_ESPACO") == "valor"


def test_so_espaco_conta_como_vazio(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SO_ESPACO", "   ")

    assert ler("SO_ESPACO") == ""


def test_padrao_vale_quando_nao_ha_variavel(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("SEM_NADA", raising=False)

    assert ler("SEM_NADA", "reserva") == "reserva"


# ---- exigir ----
def test_tudo_preenchido_nao_reclama():
    exigir(UMA="a", OUTRA="b")


def test_reclama_de_TODAS_as_que_faltam_de_uma_vez():
    """
    O ponto inteiro desta função. Reclamar de uma por vez faria a pessoa
    corrigir, rodar, descobrir a segunda, corrigir, rodar — três ciclos para um
    problema só.
    """
    with pytest.raises(ConfiguracaoInvalida) as erro:
        exigir(PRIMEIRA="", SEGUNDA="tem valor", TERCEIRA="")

    mensagem = str(erro.value)
    assert "PRIMEIRA" in mensagem
    assert "TERCEIRA" in mensagem
    assert "SEGUNDA" not in mensagem, "não pode acusar quem está preenchida"


def test_a_lista_sai_ordenada():
    """Ordem estável faz a mensagem ser comparável entre execuções."""
    with pytest.raises(ConfiguracaoInvalida) as erro:
        exigir(ZEBRA="", ALFA="", MEIO="")

    assert "ALFA, MEIO, ZEBRA" in str(erro.value)


def test_continua_sendo_ValueError():
    """Quem já tratava ValueError na borda não pode quebrar por causa da subclasse."""
    with pytest.raises(ValueError):
        exigir(FALTANDO="")


# ---- url_para_sqlalchemy ----
def test_traduz_o_esquema_para_psycopg3():
    assert (
        url_para_sqlalchemy("postgresql://u:s@host:5432/banco")
        == "postgresql+psycopg://u:s@host:5432/banco"
    )


def test_traduz_tambem_o_esquema_curto_que_provedores_entregam():
    """Heroku, Railway e afins entregam `postgres://` — SQLAlchemy nem aceita."""
    assert url_para_sqlalchemy("postgres://u@h/b") == "postgresql+psycopg://u@h/b"


def test_url_que_ja_diz_o_driver_passa_intacta():
    url = "postgresql+psycopg://u@h/b"

    assert url_para_sqlalchemy(url) == url


def test_troca_so_o_comeco():
    """Senha que contenha 'postgres://' dentro não pode ser reescrita."""
    url = "postgresql://u:postgres://x@h/b"

    assert url_para_sqlalchemy(url) == "postgresql+psycopg://u:postgres://x@h/b"


# ---- banco de teste separado do de produção ----
def test_sem_variavel_de_teste_devolve_vazio(monkeypatch: pytest.MonkeyPatch):
    """Vazio faz o teste de Postgres pular com motivo à vista, não falhar feio."""
    monkeypatch.delenv("DATABASE_URL_TESTE", raising=False)

    assert banco_url_de_teste() == ""


def test_url_de_teste_igual_a_de_producao_e_recusada(monkeypatch: pytest.MonkeyPatch):
    """
    A proteção que impede a suíte de apagar lead de cliente: o preparo dos
    testes dá TRUNCATE na tabela. Apontar as duas para o mesmo banco uma vez é
    suficiente para perder tudo.
    The guard that stops the suite from truncating production.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql://u@h/producao")
    monkeypatch.setenv("DATABASE_URL_TESTE", "postgresql://u@h/producao")

    with pytest.raises(ConfiguracaoInvalida, match="igual a DATABASE_URL"):
        banco_url_de_teste()


def test_urls_diferentes_passam(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u@h/producao")
    monkeypatch.setenv("DATABASE_URL_TESTE", "postgresql://u@h/teste")

    assert banco_url_de_teste() == "postgresql://u@h/teste"


def test_banco_url_le_a_variavel_de_producao(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u@h/b")

    assert banco_url() == "postgresql://u@h/b"
