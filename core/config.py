"""
Configuration — one place to read the environment, and it fails at boot.
Configuração — um lugar só para ler o ambiente, e falha na partida.

O que isto conserta: `os.environ` estava sendo lido solto dentro do cliente da
Evolution, e as chaves de LLM eram lidas implicitamente pelos SDKs. Config
errada não aparecia na partida — aparecia na primeira mensagem de lead, às 3h
da manhã, como falha de rede.
What this fixes: env vars were read ad hoc, so bad config surfaced on the first
lead instead of at boot.

Duas regras que valem para todo consumidor deste módulo:

1. **A chave nunca entra no código.** Só nome de variável mora aqui; valor vem
   do ambiente. Chave commitada em repositório público é revogada por varredura
   automática em minutos, e até lá qualquer um gasta no seu crédito.

2. **Falta de config reclama de TUDO de uma vez.** Corrigir uma variável,
   rodar, descobrir a segunda, corrigir, rodar, descobrir a terceira é três
   ciclos para um problema só.
   Missing config reports everything at once, not one variable per attempt.
"""

import os


class ConfiguracaoInvalida(ValueError):
    """
    Falta variável de ambiente, ou ela veio vazia.

    Herda de ValueError de propósito: quem já trata ValueError na borda continua
    tratando, e quem quiser distinguir consegue.
    Subclasses ValueError so existing handlers keep working.
    """


def ler(nome: str, padrao: str = "") -> str:
    """
    Lê uma variável do ambiente. Ausente e vazia são a mesma coisa aqui.
    Reads an env var — absent and empty are the same thing.

    `os.environ.get(nome)` devolveria None e `os.environ.get(nome, "")` devolveria
    a string vazia de um `EVOLUTION_URL=` mal preenchido no .env. As duas
    situações são a mesma para quem chama: não há valor.
    """
    return (os.environ.get(nome) or padrao).strip()


def exigir(**valores: str) -> None:
    """
    Falha se algum valor estiver vazio, listando TODOS os que faltam.
    Raises listing every missing value, not just the first.

        exigir(EVOLUTION_URL=url, EVOLUTION_API_KEY=chave)

    A chave do argumento é o nome da variável de ambiente de propósito: a
    mensagem de erro sai com o nome que a pessoa precisa procurar no .env, não
    com o nome da variável Python.
    """
    faltando = sorted(nome for nome, valor in valores.items() if not valor)

    if faltando:
        raise ConfiguracaoInvalida(
            "faltam variáveis de ambiente: " + ", ".join(faltando)
        )


def banco_url() -> str:
    """
    URL do Postgres de produção. Vazia quando não há Postgres configurado —
    o chamador decide se isso é erro ou se cai para SQLite.
    Production Postgres URL; empty when unset, so the caller decides.
    """
    return ler("DATABASE_URL")


def url_para_sqlalchemy(url: str) -> str:
    """
    'postgresql://...' -> 'postgresql+psycopg://...'

    O SQLAlchemy 2 ainda resolve `postgresql://` cru para psycopg2, que este
    projeto não instala. Sem esta tradução a migração morre com
    ModuleNotFoundError apontando para uma biblioteca que ninguém pediu — erro
    que custa meia hora para quem nunca viu.
    SQLAlchemy still defaults bare 'postgresql://' to psycopg2, which we don't install.

    Mora aqui e não em migrations/env.py porque env.py roda migração no import:
    função de tradução escondida lá dentro seria impossível de testar sem tocar
    num banco.
    Lives here because env.py runs migrations on import — untestable in place.
    """
    for prefixo in ("postgresql://", "postgres://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + url[len(prefixo) :]

    return url


def banco_url_de_teste() -> str:
    """
    URL do Postgres de TESTE. Variável separada de propósito, e não é zelo
    exagerado: os testes de contrato precisam de banco limpo, e apontar isso
    para produção apagaria lead de cliente.
    Separate on purpose — contract tests need a clean database.

    Devolve vazio se ela não existir OU se for igual à de produção. Vazio faz o
    teste pular com o motivo à vista; igual faria o teste apagar produção.
    Returns empty when unset OR equal to production.
    """
    teste = ler("DATABASE_URL_TESTE")

    if teste and teste == banco_url():
        raise ConfiguracaoInvalida(
            "DATABASE_URL_TESTE é igual a DATABASE_URL — os testes apagariam "
            "os dados de produção. Aponte DATABASE_URL_TESTE para outro banco."
        )

    return teste
