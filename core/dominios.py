"""
The approved domains of the Digital Company. Data only — no behaviour.
Os domínios aprovados da Empresa Digital. Só dados — nenhum comportamento.

Três domínios, e nada além disso nesta fase: Pessoa, Identidade e Mensagem.
Cada um existe porque a memória corporativa não funciona sem ele, não porque o
organograma ficaria bonito. Domínio nasce quando um Funcionário precisa dele.
Three domains only — a domain is born when a Funcionário needs it.

Ver DECISOES_ARQUITETURAIS_001.md §1, §2 e §5.

TUDO AQUI É IMUTÁVEL (`frozen=True`). Não é preciosismo: a Mensagem é imutável
por norma constitucional (C-2.4), e memória que se reescreve não é memória.
Pessoa e Identidade herdam a mesma disciplina — quem quiser mudar estado
produz um valor novo, e a mudança aparece.
Everything here is frozen — the Message is immutable by constitutional norm.
"""

from dataclasses import dataclass
from datetime import datetime

# Quem falou numa Mensagem. Fechado de propósito: o banco valida por CHECK, e
# um valor novo aqui é decisão de arquitetura, não digitação.
# Closed on purpose — the database enforces it with a CHECK constraint.
QUEM_FALOU = ("pessoa", "funcionario", "humano")


@dataclass(frozen=True)
class Pessoa:
    """
    Um ser humano ou organização com quem a Empresa Digital mantém relação.
    Someone the Digital Company has a relationship with.

    NÃO é um lead. Lead é um estado da relação num momento; a Pessoa continua a
    mesma quando o estado muda.

    `id` é interno e OPACO. Nunca deriva de telefone, e-mail, remoteJid ou de
    qualquer valor de canal (norma P-1.1). O motivo é concreto: o `remoteJid` do
    WhatsApp nunca foi observado rodando neste projeto, e a issue #1916 do
    projeto Evolution relata que ele diverge do número real. Identidade errada
    misturaria conversas de pessoas diferentes na mesma Pessoa — e depois de
    misturado não há como separar. Com id interno, o erro vira conserto de
    Identidade e a Pessoa segue intacta.
    The id is opaque and internal — never derived from a channel value.
    """

    empresa_id: str
    id: str
    criada_em: datetime


@dataclass(frozen=True)
class Identidade:
    """
    Como uma Pessoa é ALCANÇADA num canal. Entidade separada da Pessoa.
    How a Person is reachable on a channel — a separate entity.

    Uma Pessoa tem N Identidades; uma Identidade pertence a uma só Pessoa,
    dentro de uma Empresa Digital.

    `verificada` só é verdadeira quando a pessoa PROVOU controlar o
    identificador — respondeu a um código, clicou num link, autenticou (norma
    P-1.2). Ter chegado por um canal não verifica nada: prova que alguém usou
    aquele endereço, não quem.
    Verified means the person proved control — not merely that a message arrived.
    """

    empresa_id: str
    canal: str
    valor: str
    pessoa_id: str
    verificada: bool
    origem: str
    desde: datetime


@dataclass(frozen=True)
class Mensagem:
    """
    A unidade imutável da Conversa (norma C-2.1).
    The immutable unit of a Conversation.

    "Conversa" é a sequência ordenada destas, não um objeto com começo e fim.
    Não existe sessão: toda regra de corte — silêncio de 24h, troca de assunto —
    é arbitrária e vira dado errado. Fatiar depois é derivável do que está
    guardado; desfatiar não é.
    No sessions: any cut-off rule is arbitrary and becomes wrong data.

    `canal` é atributo DA MENSAGEM (norma C-2.3). Uma conversa que começa no
    WhatsApp e continua por e-mail é a mesma conversa, e nenhum Funcionário
    precisa saber a diferença.

    `externo` é o identificador no sistema de origem, e existe só para
    deduplicar: reprocessar a mesma entrega não pode gravar a mensagem duas
    vezes. É opcional porque nem toda porta tem um.
    """

    empresa_id: str
    id: str
    pessoa_id: str
    quem_falou: str
    texto: str
    canal: str
    quando: datetime
    externo: str | None = None
