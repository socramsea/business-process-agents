"""
Liga o Alembic ao core/config.py. Sem modelo ORM de propósito.
Wires Alembic to core/config.py. No ORM models, on purpose.

O projeto é SQL cru e vai continuar sendo: o `autogenerate` do Alembic só
serve com modelo declarativo, e modelo declarativo aqui seria uma segunda
descrição do schema para manter em dia com a primeira. Migração escrita à mão
é mais trabalho por migração e menos surpresa por deploy.
No autogenerate: hand-written migrations, one description of the schema.
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine

# O alembic.ini já faz prepend_sys_path, mas isso vale só para o CLI. Quando o
# conftest chama o Alembic por dentro do processo do pytest, quem garante o
# import é esta linha.
# The ini's prepend_sys_path only covers the CLI; this covers in-process runs.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import config as cfg  # noqa: E402

alembic_config = context.config

if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)


def url_do_banco() -> str:
    """
    A URL, em ordem de precedência: `-x url=...` primeiro, ambiente depois.
    URL precedence: the -x flag first, environment second.

    O `-x` existe para o teste apontar para DATABASE_URL_TESTE sem precisar
    mexer no ambiente do processo — mexer no ambiente para rodar teste é como
    um teste acaba escrevendo em produção.
    """
    do_argumento = context.get_x_argument(as_dictionary=True).get("url", "")
    if do_argumento:
        return cfg.url_para_sqlalchemy(do_argumento)

    do_ambiente = cfg.banco_url()
    cfg.exigir(DATABASE_URL=do_ambiente)
    return cfg.url_para_sqlalchemy(do_ambiente)


def migrar_sem_conexao() -> None:
    """Modo offline: emite o SQL em vez de executar. `alembic upgrade head --sql`."""
    context.configure(
        url=url_do_banco(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def migrar_com_conexao() -> None:
    """Modo normal: conecta e aplica."""
    motor = create_engine(url_do_banco(), pool_pre_ping=True)

    with motor.connect() as conexao:
        context.configure(connection=conexao)

        with context.begin_transaction():
            context.run_migrations()

    motor.dispose()


if context.is_offline_mode():
    migrar_sem_conexao()
else:
    migrar_com_conexao()
