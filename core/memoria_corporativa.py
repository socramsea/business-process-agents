"""
Corporate memory — what the Digital Company knows. One memory, many domains.
Memória corporativa — o que a Empresa Digital sabe. Uma só, com domínios dentro.

NÃO existe memória privada de Funcionário. O que o SDR escreve aqui, o
Atendimento lê. É essa ausência de dono que permite um Funcionário continuar o
trabalho de outro sem conhecê-lo (normas M-3.5 a M-3.7).
There is no per-Funcionário memory: what one writes, another reads.

O QUE ESTE CONTRATO NÃO TEM, e a ausência é o projeto:

  atualizar_mensagem   ·   apagar_mensagem
      A Mensagem é imutável (C-2.4). Correção é mensagem nova, nunca edição da
      anterior. Não há método porque não deve haver caminho.

  unificar_pessoas
      Unificação de identidade não faz parte da Fase A. A estrutura que a
      torna possível existe (Identidade separada de Pessoa), a operação não.
      Quando existir, identidade não verificada nunca poderá fundir sozinha
      (norma P-1.4).

Ver DECISOES_ARQUITETURAIS_001.md §1, §2, §3.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from psycopg_pool import ConnectionPool

from core.dominios import QUEM_FALOU, Identidade, Mensagem, Pessoa

TIMEOUT_CONEXAO_SEGUNDOS = 10.0


def novo_id() -> str:
    """
    Identificador interno e opaco. Não carrega informação nenhuma sobre a coisa
    que identifica — é esse o ponto (norma P-1.1).
    An opaque internal id: it carries no information about what it identifies.
    """
    return uuid4().hex


class MemoriaCorporativa(ABC):
    """Contrato único da memória da empresa. Uma implementação por armazenamento."""

    # ---- Pessoas e Identidades ----

    @abstractmethod
    def pessoa_por_identidade(
        self, empresa_id: str, canal: str, valor: str
    ) -> Pessoa | None:
        """
        Quem é alcançado por este identificador neste canal, ou None.
        Who is reachable at this channel identifier, or None.

        None é resposta legítima: é alguém que nunca falou com esta empresa.
        """
        ...

    @abstractmethod
    def resolver_pessoa(
        self,
        empresa_id: str,
        canal: str,
        valor: str,
        origem: str,
        quando: datetime,
        verificada: bool = False,
    ) -> Pessoa:
        """
        Devolve a Pessoa alcançada por (canal, valor), criando-a se for a
        primeira vez. Atômico.
        Returns the Person reachable at (channel, value), creating on first sight.

        Criar Pessoa para uma identidade nunca vista NÃO é unificar: unificar é
        ligar duas Pessoas que já existem, e isso não existe nesta fase.

        Atômico de propósito: duas mensagens da mesma pessoa nova chegando ao
        mesmo tempo não podem produzir duas Pessoas. Identidade duplicada é
        exatamente a corrupção que o id interno existe para evitar.
        """
        ...

    @abstractmethod
    def identidades_de(self, empresa_id: str, pessoa_id: str) -> list[Identidade]:
        """Por onde esta Pessoa é alcançável. Ordenado por `desde`."""
        ...

    # ---- Conversa ----

    @abstractmethod
    def registrar_mensagem(
        self,
        empresa_id: str,
        pessoa_id: str,
        quem_falou: str,
        texto: str,
        canal: str,
        quando: datetime,
        externo: str | None = None,
    ) -> Mensagem:
        """
        Acrescenta ao fim da conversa. Nunca edita, nunca reordena.
        Appends to the conversation — never edits, never reorders.

        Idempotente quando `externo` vem preenchido: reprocessar a mesma entrega
        devolve a mensagem que já existe em vez de duplicá-la. Sem isso, um
        canal reentregando por timeout inventaria conversa que não houve.
        """
        ...

    @abstractmethod
    def conversa_de(self, empresa_id: str, pessoa_id: str) -> list[Mensagem]:
        """
        Tudo que foi dito com esta Pessoa, em ordem de tempo.
        Everything said with this Person, in time order.

        É a sequência inteira, não uma sessão. Recortar em janelas é derivável
        daqui quando alguém precisar; o contrário não seria.
        """
        ...

    @abstractmethod
    def fechar(self) -> None:
        """Solta o que estiver aberto."""
        ...


def _validar_quem_falou(quem_falou: str) -> None:
    if quem_falou not in QUEM_FALOU:
        raise ValueError(
            f"quem_falou={quem_falou!r} não é um dos {QUEM_FALOU}"
        )


class MemoriaCorporativaEmMemoria(MemoriaCorporativa):
    """
    Guarda em dicionários do processo. Some quando o processo morre.
    In-process dictionaries — gone when the process dies.

    Não é dublê de teste: é implementação legítima para rodar sem banco. Os
    testes de contrato usam ela porque o comportamento tem que ser o mesmo do
    Postgres, e é isso que eles verificam.
    """

    def __init__(self, gerar_id: Callable[[], str] = novo_id) -> None:
        # Costura para teste, mesmo padrão de transport=/cliente=/memoria=.
        self._gerar_id = gerar_id
        self._pessoas: dict[tuple[str, str], Pessoa] = {}
        self._identidades: dict[tuple[str, str, str], Identidade] = {}
        self._mensagens: list[Mensagem] = []

    def pessoa_por_identidade(
        self, empresa_id: str, canal: str, valor: str
    ) -> Pessoa | None:
        identidade = self._identidades.get((empresa_id, canal, valor))
        if identidade is None:
            return None
        return self._pessoas[(empresa_id, identidade.pessoa_id)]

    def resolver_pessoa(
        self,
        empresa_id: str,
        canal: str,
        valor: str,
        origem: str,
        quando: datetime,
        verificada: bool = False,
    ) -> Pessoa:
        ja_conhecida = self.pessoa_por_identidade(empresa_id, canal, valor)
        if ja_conhecida is not None:
            return ja_conhecida

        pessoa = Pessoa(empresa_id=empresa_id, id=self._gerar_id(), criada_em=quando)
        self._pessoas[(empresa_id, pessoa.id)] = pessoa
        self._identidades[(empresa_id, canal, valor)] = Identidade(
            empresa_id=empresa_id,
            canal=canal,
            valor=valor,
            pessoa_id=pessoa.id,
            verificada=verificada,
            origem=origem,
            desde=quando,
        )
        return pessoa

    def identidades_de(self, empresa_id: str, pessoa_id: str) -> list[Identidade]:
        return sorted(
            (
                i
                for i in self._identidades.values()
                if i.empresa_id == empresa_id and i.pessoa_id == pessoa_id
            ),
            key=lambda i: (i.desde, i.canal, i.valor),
        )

    def registrar_mensagem(
        self,
        empresa_id: str,
        pessoa_id: str,
        quem_falou: str,
        texto: str,
        canal: str,
        quando: datetime,
        externo: str | None = None,
    ) -> Mensagem:
        _validar_quem_falou(quem_falou)

        if externo is not None:
            for existente in self._mensagens:
                if (
                    existente.empresa_id == empresa_id
                    and existente.canal == canal
                    and existente.externo == externo
                ):
                    return existente

        mensagem = Mensagem(
            empresa_id=empresa_id,
            id=self._gerar_id(),
            pessoa_id=pessoa_id,
            quem_falou=quem_falou,
            texto=texto,
            canal=canal,
            quando=quando,
            externo=externo,
        )
        self._mensagens.append(mensagem)
        return mensagem

    def conversa_de(self, empresa_id: str, pessoa_id: str) -> list[Mensagem]:
        return sorted(
            (
                m
                for m in self._mensagens
                if m.empresa_id == empresa_id and m.pessoa_id == pessoa_id
            ),
            key=lambda m: (m.quando, m.id),
        )

    def fechar(self) -> None:
        """Não segura recurso nenhum: os dicionários morrem com o processo."""


class MemoriaCorporativaPostgres(MemoriaCorporativa):
    """
    Postgres. O schema é das migrações — esta classe NÃO cria tabela.
    Postgres, with migrations owning the schema — this class creates nothing.

    Tabela ausente é erro de deploy e tem que estourar. Construtor que remenda
    schema é como um sistema acaba com duas versões de tabela em produção sem
    ninguém notar.
    """

    def __init__(
        self,
        url: str,
        pool: ConnectionPool | None = None,
        gerar_id: Callable[[], str] = novo_id,
    ) -> None:
        self._gerar_id = gerar_id

        if pool is not None:
            self._pool = pool
            return

        # open=False + open(wait=True): sem isto o pool conecta numa thread de
        # fundo e o construtor devolve um objeto que parece bom e falha só na
        # primeira consulta. Preferimos o erro aqui.
        self._pool = ConnectionPool(url, min_size=1, open=False)
        self._pool.open(wait=True, timeout=TIMEOUT_CONEXAO_SEGUNDOS)

    def pessoa_por_identidade(
        self, empresa_id: str, canal: str, valor: str
    ) -> Pessoa | None:
        with self._pool.connection() as con:
            linha = con.execute(
                """
                SELECT p.empresa_id, p.id, p.criada_em
                  FROM identidade i
                  JOIN pessoa p ON p.empresa_id = i.empresa_id AND p.id = i.pessoa_id
                 WHERE i.empresa_id = %s AND i.canal = %s AND i.valor = %s
                """,
                (empresa_id, canal, valor),
            ).fetchone()

        if linha is None:
            return None
        return Pessoa(empresa_id=linha[0], id=linha[1], criada_em=linha[2])

    def resolver_pessoa(
        self,
        empresa_id: str,
        canal: str,
        valor: str,
        origem: str,
        quando: datetime,
        verificada: bool = False,
    ) -> Pessoa:
        # Uma transação só, e a atomicidade vem do ON CONFLICT sobre a chave
        # (empresa_id, canal, valor): duas chamadas simultâneas para a mesma
        # identidade nova produzem UMA Pessoa, não duas.
        with self._pool.connection() as con:
            pessoa_id = self._gerar_id()

            con.execute(
                "INSERT INTO pessoa (empresa_id, id, criada_em) VALUES (%s, %s, %s)",
                (empresa_id, pessoa_id, quando),
            )
            gravado = con.execute(
                """
                INSERT INTO identidade
                       (empresa_id, canal, valor, pessoa_id, verificada, origem, desde)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (empresa_id, canal, valor) DO NOTHING
                RETURNING pessoa_id
                """,
                (empresa_id, canal, valor, pessoa_id, verificada, origem, quando),
            ).fetchone()

            if gravado is None:
                # A identidade já existia: alguém chegou primeiro. A Pessoa que
                # acabamos de inserir não foi usada por ninguém e sai, para não
                # deixar Pessoa órfã — que é lixo que ninguém alcança.
                con.execute(
                    "DELETE FROM pessoa WHERE empresa_id = %s AND id = %s",
                    (empresa_id, pessoa_id),
                )
                linha = con.execute(
                    """
                    SELECT p.empresa_id, p.id, p.criada_em
                      FROM identidade i
                      JOIN pessoa p
                        ON p.empresa_id = i.empresa_id AND p.id = i.pessoa_id
                     WHERE i.empresa_id = %s AND i.canal = %s AND i.valor = %s
                    """,
                    (empresa_id, canal, valor),
                ).fetchone()

                if linha is None:
                    # A identidade existia um instante atrás (o ON CONFLICT
                    # provou) e não existe mais. Alguém a removeu no meio.
                    # Inventar uma Pessoa aqui seria criar identidade duplicada
                    # em silêncio — exatamente o que esta transação evita.
                    raise RuntimeError(
                        f"identidade ({canal}, {valor}) da empresa {empresa_id} "
                        "desapareceu durante a resolução — nada foi gravado"
                    )

                return Pessoa(empresa_id=linha[0], id=linha[1], criada_em=linha[2])

        return Pessoa(empresa_id=empresa_id, id=pessoa_id, criada_em=quando)

    def identidades_de(self, empresa_id: str, pessoa_id: str) -> list[Identidade]:
        with self._pool.connection() as con:
            linhas = con.execute(
                """
                SELECT empresa_id, canal, valor, pessoa_id, verificada, origem, desde
                  FROM identidade
                 WHERE empresa_id = %s AND pessoa_id = %s
                 ORDER BY desde, canal, valor
                """,
                (empresa_id, pessoa_id),
            ).fetchall()

        return [
            Identidade(
                empresa_id=linha[0],
                canal=linha[1],
                valor=linha[2],
                pessoa_id=linha[3],
                verificada=linha[4],
                origem=linha[5],
                desde=linha[6],
            )
            for linha in linhas
        ]

    def registrar_mensagem(
        self,
        empresa_id: str,
        pessoa_id: str,
        quem_falou: str,
        texto: str,
        canal: str,
        quando: datetime,
        externo: str | None = None,
    ) -> Mensagem:
        _validar_quem_falou(quem_falou)

        with self._pool.connection() as con:
            if externo is not None:
                ja_entregue = con.execute(
                    """
                    SELECT empresa_id, id, pessoa_id, quem_falou, texto, canal,
                           quando, externo
                      FROM mensagem
                     WHERE empresa_id = %s AND canal = %s AND externo = %s
                    """,
                    (empresa_id, canal, externo),
                ).fetchone()
                if ja_entregue is not None:
                    return _mensagem(ja_entregue)

            mensagem_id = self._gerar_id()
            con.execute(
                """
                INSERT INTO mensagem
                       (empresa_id, id, pessoa_id, quem_falou, texto, canal,
                        quando, externo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    empresa_id,
                    mensagem_id,
                    pessoa_id,
                    quem_falou,
                    texto,
                    canal,
                    quando,
                    externo,
                ),
            )

        return Mensagem(
            empresa_id=empresa_id,
            id=mensagem_id,
            pessoa_id=pessoa_id,
            quem_falou=quem_falou,
            texto=texto,
            canal=canal,
            quando=quando,
            externo=externo,
        )

    def conversa_de(self, empresa_id: str, pessoa_id: str) -> list[Mensagem]:
        with self._pool.connection() as con:
            linhas = con.execute(
                """
                SELECT empresa_id, id, pessoa_id, quem_falou, texto, canal,
                       quando, externo
                  FROM mensagem
                 WHERE empresa_id = %s AND pessoa_id = %s
                 ORDER BY quando, id
                """,
                (empresa_id, pessoa_id),
            ).fetchall()

        return [_mensagem(linha) for linha in linhas]

    def fechar(self) -> None:
        self._pool.close()


def _mensagem(linha: tuple[object, ...]) -> Mensagem:
    """Uma linha de `mensagem` vira o domínio. Um lugar só que sabe a ordem."""
    return Mensagem(
        empresa_id=str(linha[0]),
        id=str(linha[1]),
        pessoa_id=str(linha[2]),
        quem_falou=str(linha[3]),
        texto=str(linha[4]),
        canal=str(linha[5]),
        quando=linha[6],  # type: ignore[arg-type]
        externo=None if linha[7] is None else str(linha[7]),
    )
