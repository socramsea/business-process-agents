"""
Lead memory — the contract that makes a returning lead recognizable.
Memória do lead — o contrato que faz quem volta ser reconhecido.

Até aqui o `lead_id` entrava no handle e saía no resultado sem tocar em nada:
identidade decorativa. Cada mensagem apagava a anterior.
Until now `lead_id` went in and came out untouched — decorative identity.

Armazenamento fica aqui porque é compartilhado; as REGRAS de acumulação ficam
em agents/lead_triage/acumulo.py, porque conhecem o nome de cada sinal.
Storage lives here because it is shared; the accumulation RULES live with the
agent, because they know each signal by name.

ESTE MÓDULO É O ESTADO LEGADO DO SDR, e só isso.

O que ele guarda é a pontuação acumulada — sinais travados, contagem de
mensagens, agentes já indicados. Pela constituição isso é **estado derivado**
(Camada 3): recalculável a partir das Mensagens, e por isso não ganha
persistência corporativa.

A memória da Empresa Digital — Pessoa, Identidade, Mensagem — mora em
`core/memoria_corporativa.py`, com o schema governado pelas migrações. Aqui
não há Postgres: a implementação que existiu implementava o modelo
`(tenant, lead) -> blob`, que é o modelo de registro que a constituição
rejeita, e foi removida em vez de mantida como infraestrutura órfã.
The corporate memory lives elsewhere; this is the SDR's derived state only.
"""

import json
import sqlite3
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class MemoriaLead(ABC):
    """Contrato comum: carrega o estado de um lead, salva o estado de um lead."""

    @abstractmethod
    def carregar(self, tenant_id: str, lead_id: str) -> dict[str, Any]:
        """
        Devolve o estado guardado, ou dicionário vazio se o lead é novo.
        Returns the stored state, or an empty dict if the lead is new.

        Vazio é resposta legítima, não erro — é a primeira mensagem de alguém.
        """
        ...

    @abstractmethod
    def salvar(self, tenant_id: str, lead_id: str, estado: dict[str, Any]) -> None:
        """Grava o estado. Sobrescreve o anterior."""
        ...

    @abstractmethod
    def fechar(self) -> None:
        """
        Solta o que estiver aberto.
        Releases whatever is held open.

        Está no contrato porque sem isto quem segura um MemoriaLead não
        consegue fechar sem antes descobrir qual implementação recebeu — e
        perguntar o tipo concreto para decidir o que chamar é o contrário de
        contrato.

        Abstrato, e não um método vazio herdável, de propósito: implementação
        nova que segure conexão e esqueça de fechar vazaria em silêncio.
        Obrigada a escrever o método, ela é obrigada a decidir.
        Abstract on purpose — an implementation that holds a connection and
        forgets to close it would leak silently.
        """
        ...


class MemoriaEmMemoria(MemoriaLead):
    """
    Guarda num dicionário do processo. Some quando o processo morre.
    Keeps state in a process dict — gone when the process dies.

    Não é dublê de teste: é implementação legítima para rodar sem persistência.
    Os testes usam ela justamente porque o comportamento é o mesmo do SQLite,
    sem tocar em disco.
    """

    def __init__(self) -> None:
        self._dados: dict[tuple[str, str], dict[str, Any]] = {}

    def carregar(self, tenant_id: str, lead_id: str) -> dict[str, Any]:
        # Cópia: quem chamou não deve conseguir mutar o guardado por acidente.
        return dict(self._dados.get((tenant_id, lead_id), {}))

    def salvar(self, tenant_id: str, lead_id: str, estado: dict[str, Any]) -> None:
        self._dados[(tenant_id, lead_id)] = dict(estado)

    def fechar(self) -> None:
        """Não segura recurso nenhum: o dicionário morre com o processo."""


class MemoriaSQLite(MemoriaLead):
    """
    SQLite com um blob JSON por (tenant_id, lead_id).
    SQLite with one JSON blob per (tenant_id, lead_id).

    Blob e não colunas de propósito: o formato do estado ainda vai mudar, e
    migração de schema a cada campo novo custaria mais que o ganho de consultar
    por coluna, que ninguém precisa fazer ainda.
    JSON blob on purpose — the state shape is still moving.

    O tenant faz parte da chave desde já. Multi-tenant não está no MVP, mas
    chave errada é a migração mais cara que existe.
    """

    def __init__(self, caminho: str | Path = "memoria.db"):
        # Conexão única, não uma por chamada. Com ':memory:' cada connect()
        # cria um banco NOVO e vazio — a tabela criada aqui não existiria na
        # leitura seguinte. Em arquivo funcionava por acidente: o disco guardava.
        # One connection, not one per call — ':memory:' would otherwise create
        # a fresh empty database on every connect().
        self._con = sqlite3.connect(str(caminho), check_same_thread=False)
        # check_same_thread=False permite uso de várias threads, mas NÃO torna
        # a conexão segura sozinha. O lock é que faz isso.
        self._lock = threading.Lock()
        self._criar_tabela()

    def _criar_tabela(self) -> None:
        with self._lock, self._con:
            self._con.execute(
                """
                CREATE TABLE IF NOT EXISTS lead (
                    tenant_id TEXT NOT NULL,
                    lead_id   TEXT NOT NULL,
                    estado    TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, lead_id)
                )
                """
            )

    def carregar(self, tenant_id: str, lead_id: str) -> dict[str, Any]:
        with self._lock:
            linha = self._con.execute(
                "SELECT estado FROM lead WHERE tenant_id = ? AND lead_id = ?",
                (tenant_id, lead_id),
            ).fetchone()

        if linha is None:
            return {}

        carregado: dict[str, Any] = json.loads(linha[0])
        return carregado

    def salvar(self, tenant_id: str, lead_id: str, estado: dict[str, Any]) -> None:
        with self._lock, self._con:
            self._con.execute(
                """
                INSERT INTO lead (tenant_id, lead_id, estado) VALUES (?, ?, ?)
                ON CONFLICT (tenant_id, lead_id) DO UPDATE SET estado = excluded.estado
                """,
                (tenant_id, lead_id, json.dumps(estado, ensure_ascii=False)),
            )

    def fechar(self) -> None:
        with self._lock:
            self._con.close()
