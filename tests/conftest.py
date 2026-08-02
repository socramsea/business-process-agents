"""
Preparo compartilhado dos testes.
Shared test setup.

O que mora aqui: a fixture `memoria`, que roda o MESMO teste de contrato contra
as três implementações de MemoriaLead. Antes, um `for` dentro do teste
percorria duas — e um `for` esconde ausência: se o Postgres não estivesse na
lista, nada na saída do pytest diria isso. Como fixture parametrizada, cada
implementação vira uma linha própria, e a que não roda aparece como SKIPPED com
o motivo escrito.
As a parametrized fixture, a skipped backend is visible instead of silent.
"""

import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import psycopg
import pytest
from alembic.config import Config as ConfigAlembic
from alembic.script import ScriptDirectory

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))

from core import config  # noqa: E402
from core.memoria import MemoriaEmMemoria, MemoriaLead, MemoriaSQLite  # noqa: E402
from core.memoria_corporativa import (  # noqa: E402
    MemoriaCorporativa,
    MemoriaCorporativaEmMemoria,
    MemoriaCorporativaPostgres,
)


def cabecas_do_alembic() -> list[str]:
    """
    As cabeças declaradas em migrations/versions/, lidas do disco sem tocar em
    banco nenhum.
    Alembic heads, read from disk without touching any database.
    """
    return list(
        ScriptDirectory.from_config(ConfigAlembic(str(RAIZ / "alembic.ini"))).get_heads()
    )


@pytest.fixture(scope="session")
def migracoes_aplicadas() -> str:
    """
    Aplica as migrações no banco de TESTE e devolve a URL.
    Applies migrations to the TEST database and returns its URL.

    Chama o `alembic` como processo, e não pela API Python, de propósito: é
    exatamente o comando que o deploy roda. Teste que exercita um caminho
    diferente do de produção prova o caminho errado.
    Runs the real CLI — the same command a deploy runs.

    `banco_url_de_teste()` recusa devolver a URL se ela for igual à de produção,
    então este fixture não tem como apontar para o banco de cliente.
    """
    url = config.banco_url_de_teste()

    if not url:
        pytest.skip("DATABASE_URL_TESTE não definida — Postgres não foi testado")

    # GUARDA ESTRITA. Pular só quando o Alembic está LEGITIMAMENTE sem revisão:
    # nesse estado não existe schema de domínio nenhum, e não há o que exercer.
    #
    # A condição é a contagem de cabeças, lida do disco — NÃO é `except
    # UndefinedTable`. A diferença decide o valor deste portão:
    #
    #   zero revisões        + tabela ausente  →  consequência do estado. SKIP.
    #   qualquer revisão     + tabela ausente  →  migração não aplicada, ou
    #                                             aplicada errada. ERRO VERMELHO.
    #
    # Um try/except transformaria os dois casos em skip e esconderia o segundo,
    # que é justamente uma falha de deploy em produção.
    #
    # Isto se desfaz sozinho: no dia em que a Fase A criar a primeira migração,
    # `cabecas_do_alembic()` deixa de ser vazia e os testes voltam a rodar sem
    # ninguém lembrar de nada.
    # Self-healing: the skip disappears the moment a real migration exists.
    if not cabecas_do_alembic():
        pytest.skip(
            "Alembic com zero revisões — ainda não existe schema de domínio "
            "para exercer. Estes testes voltam sozinhos quando a Fase A criar "
            "a primeira migração."
        )

    subprocess.run(
        ["alembic", "-x", f"url={url}", "upgrade", "head"],
        cwd=RAIZ,
        check=True,
        capture_output=True,
        text=True,
    )
    return url


@pytest.fixture(params=["em-memoria", "sqlite"])
def memoria(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[MemoriaLead]:
    """
    Uma implementação de MemoriaLead por rodada, sempre limpa.
    One MemoriaLead implementation per round, always clean.

    Duas e não três: `MemoriaPostgres` foi removida junto com o modelo que ela
    implementava. O estado acumulado do SDR é derivado (Camada 3) e não ganha
    persistência corporativa — a memória da empresa mora em
    `memoria_corporativa`, com os seus próprios domínios.
    """
    banco: MemoriaLead

    if request.param == "em-memoria":
        banco = MemoriaEmMemoria()
    else:
        banco = MemoriaSQLite(tmp_path / "contrato.db")

    yield banco
    # Sai igual para as duas porque `fechar()` está no contrato. Fosse método
    # só das concretas, este preparo teria que perguntar o tipo antes.
    banco.fechar()


@pytest.fixture(params=["em-memoria", "postgres"])
def memoria_corporativa(request: pytest.FixtureRequest) -> Iterator[MemoriaCorporativa]:
    """
    A memória da empresa, uma implementação por rodada, sempre limpa.
    Corporate memory — one implementation per round, always clean.

    Duas e não três: a memória corporativa nasce com o schema das migrações, e
    SQLite não participa dela. O SQLite continua servindo o estado legado do
    SDR, intocado.
    """
    if request.param == "em-memoria":
        banco: MemoriaCorporativa = MemoriaCorporativaEmMemoria()
        yield banco
        banco.fechar()
        return

    url = request.getfixturevalue("migracoes_aplicadas")
    _esvaziar_dominios(url)

    banco = MemoriaCorporativaPostgres(url)
    yield banco
    banco.fechar()


def _esvaziar_dominios(url: str) -> None:
    """
    Zera os três domínios entre testes, na ordem das dependências.
    Truncates the three domains, respecting foreign keys.

    Só recebe a URL de teste — `config.banco_url_de_teste()` recusa devolver
    qualquer coisa igual à de produção, então isto não alcança dado de cliente.
    """
    with psycopg.connect(url) as con:
        con.execute("TRUNCATE TABLE mensagem, identidade, pessoa")


