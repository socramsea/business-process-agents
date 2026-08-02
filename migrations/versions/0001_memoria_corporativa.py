"""memoria corporativa: pessoa, identidade, mensagem

Revision ID: 0001
Revises:
Create Date: 2026-08-02

A PRIMEIRA migração da Empresa Digital. Nasce com os domínios aprovados —
Pessoa, Identidade e Mensagem — e com os nomes certos.

Não existe tabela `lead`. Uma migração criando `lead` chegou a ser escrita
antes da constituição e foi DESCARTADA sem entrar no histórico: lead é um
estado da relação num momento, não o que a pessoa é, e modelar a pessoa como
registro é o que a constituição proíbe (§1).

Três tabelas e nada além. Os outros dez domínios da §4 nascem quando um
Funcionário precisar deles — tabela criada antes disso é infraestrutura pela
infraestrutura (P8).

NÃO EXISTE TABELA `empresa` nesta migração, e é deliberado: `empresa_id` é a
fronteira de isolamento e entra em toda chave e toda consulta, mas o registro
da Empresa Digital (configuração, régua, teto de autonomia) nasce quando
houver configuração para guardar. Aqui ele não teria coluna nenhuma além do id.
No `empresa` table yet — it would have no column beyond its own id.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---- Pessoa ----
    # `id` é interno e OPACO: nunca deriva de telefone, e-mail ou remoteJid
    # (norma P-1.1). Chave composta com empresa_id porque a mesma pessoa do
    # mundo real, em duas Empresas Digitais, são duas Pessoas — sem exceção e
    # sem correlação (norma P-1.5). Dois clientes da Forja podem ser
    # concorrentes; descobrir que o mesmo comprador falou com os dois é
    # vazamento comercial.
    op.create_table(
        "pessoa",
        sa.Column("empresa_id", sa.Text(), nullable=False),
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("criada_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("empresa_id", "id", name="pk_pessoa"),
    )

    # ---- Identidade ----
    # Entidade SEPARADA da Pessoa (§1). Uma Pessoa tem N Identidades; uma
    # Identidade pertence a uma só Pessoa.
    #
    # A chave primária (empresa_id, canal, valor) é o que impede duas Pessoas
    # reivindicarem o mesmo identificador — a corrupção que não tem conserto
    # depois, porque misturadas as conversas não há como saber de quem era cada
    # mensagem.
    #
    # `verificada` nasce FALSE: ter chegado por um canal não verifica nada,
    # prova que alguém usou aquele endereço, não quem (norma P-1.2). E
    # identidade não verificada nunca pode fundir Pessoas automaticamente
    # (norma P-1.4) — a unificação não existe nesta fase, e quando existir esta
    # coluna é o que a governa.
    op.create_table(
        "identidade",
        sa.Column("empresa_id", sa.Text(), nullable=False),
        sa.Column("canal", sa.Text(), nullable=False),
        sa.Column("valor", sa.Text(), nullable=False),
        sa.Column("pessoa_id", sa.Text(), nullable=False),
        sa.Column(
            "verificada", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("origem", sa.Text(), nullable=False),
        sa.Column("desde", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("empresa_id", "canal", "valor", name="pk_identidade"),
        sa.ForeignKeyConstraint(
            ["empresa_id", "pessoa_id"],
            ["pessoa.empresa_id", "pessoa.id"],
            name="fk_identidade_pessoa",
        ),
    )
    op.create_index("ix_identidade_pessoa", "identidade", ["empresa_id", "pessoa_id"])

    # ---- Mensagem ----
    # A unidade imutável da Conversa (norma C-2.1). Não há tabela `conversa`:
    # conversa é a SEQUÊNCIA destas linhas, e inventar sessão exigiria uma regra
    # de corte arbitrária — silêncio de 24h? troca de assunto? — que viraria
    # dado errado. Recortar em janelas é derivável daqui; desfatiar não seria.
    #
    # `canal` é coluna DA MENSAGEM (norma C-2.3), e é TEXT sem CHECK de
    # propósito: canal novo não pode exigir migração, senão adicionar um canal
    # vira mudança de schema e a promessa de independência de canal é falsa.
    #
    # `quem_falou` é o oposto: fechado por CHECK, porque valor novo ali é
    # decisão de arquitetura, não digitação.
    op.create_table(
        "mensagem",
        sa.Column("empresa_id", sa.Text(), nullable=False),
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("pessoa_id", sa.Text(), nullable=False),
        sa.Column("quem_falou", sa.Text(), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("canal", sa.Text(), nullable=False),
        sa.Column("quando", sa.DateTime(timezone=True), nullable=False),
        # Identificador no sistema de origem. Existe só para deduplicar: um
        # canal reentregando por timeout inventaria conversa que não houve.
        sa.Column("externo", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("empresa_id", "id", name="pk_mensagem"),
        sa.ForeignKeyConstraint(
            ["empresa_id", "pessoa_id"],
            ["pessoa.empresa_id", "pessoa.id"],
            name="fk_mensagem_pessoa",
        ),
        sa.CheckConstraint(
            "quem_falou IN ('pessoa', 'funcionario', 'humano')",
            name="ck_mensagem_quem_falou",
        ),
    )
    # A conversa: tudo de uma Pessoa, em ordem de tempo. É a leitura que todo
    # Funcionário faz, e é a que precisa ser barata.
    op.create_index(
        "ix_mensagem_conversa", "mensagem", ["empresa_id", "pessoa_id", "quando"]
    )
    # Deduplicação por entrega do canal. Parcial porque `externo` é opcional —
    # nem toda porta tem identificador próprio, e NULL não deve colidir.
    op.create_index(
        "ux_mensagem_externo",
        "mensagem",
        ["empresa_id", "canal", "externo"],
        unique=True,
        postgresql_where=sa.text("externo IS NOT NULL"),
    )


def downgrade() -> None:
    # APAGA TUDO: pessoas, identidades e conversas. Existe porque migração sem
    # volta é caminho de mão única, e descobre-se que precisa voltar
    # exatamente quando não dá mais. Rodar isto em produção perde a memória da
    # empresa inteira — faça backup antes (deploy/backup.sh).
    # DROPS EVERYTHING. Back up first.
    #
    # Ordem inversa da criação: mensagem e identidade apontam para pessoa.
    op.drop_table("mensagem")
    op.drop_table("identidade")
    op.drop_table("pessoa")
