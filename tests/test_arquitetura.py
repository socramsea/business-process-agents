"""
Os princípios da constituição, como portão executável.
The constitution's principles, as an executable gate.

Princípio sem teste de violação é frase de parede. Estes são os dois que a
Fase A precisa manter de pé enquanto a memória corporativa nasce: P1 (nenhum
Funcionário conhece outro) e P2 (nenhum Funcionário sabe o canal).

Ver ARQUITETURA_EMPRESA_DIGITAL.md §2 e DECISOES_ARQUITETURAIS_001.md §6.

O pacote dos Funcionários ainda se chama `agents/` — a renomeação para
`funcionarios/` é da fase de nomenclatura, não desta. Os portões apontam para
onde o Funcionário mora hoje; mudam de endereço junto com ele.
The Funcionário package is still `agents/`; renaming belongs to a later phase.
"""

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))

PACOTE_DOS_FUNCIONARIOS = RAIZ / "agents"

# Vocabulário de canal. Um Funcionário que escreve qualquer um destes está
# sabendo por onde a pessoa chegou.
CANAIS = (
    "whatsapp",
    "evolution",
    "remotejid",
    "instagram",
    "telegram",
    "messenger",
    "apikey",
)

# EXCEÇÃO ÚNICA E DOCUMENTADA — pendente de arbitragem do Marcos.
#
# `signals.py` menciona WhatsApp e Instagram DENTRO do texto da instrução, na
# frase "(WhatsApp e Instagram são onde a dor aparece, não qual ela é)". Ela
# ensina o modelo a NÃO tratar o canal como sinal — é P2 em substância e
# violação de P2 na letra.
#
# Não removi e não afrouxei o portão: registrei a exceção aqui, visível, para
# que qualquer ocorrência NOVA falhe. Se o Marcos decidir que prosa de
# instrução conta como violação, esta linha sai e a instrução muda.
# A single documented exception, pending the architect's ruling.
EXCECAO_CONHECIDA = (
    "agents/lead_triage/signals.py",
    "(WhatsApp e Instagram são onde a dor aparece, não qual ela é).",
)


def modulos_dos_funcionarios() -> list[Path]:
    return sorted(PACOTE_DOS_FUNCIONARIOS.rglob("*.py"))


def pacote_de(caminho: Path) -> str:
    """`agents/lead_triage/agent.py` -> `lead_triage`."""
    return caminho.relative_to(PACOTE_DOS_FUNCIONARIOS).parts[0]


def importados_por(caminho: Path) -> list[str]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"))

    nomes: list[str] = []
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes.extend(alias.name for alias in no.names)
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.append(no.module)

    return nomes


# ---- P1: nenhum Funcionário conhece outro Funcionário ----
def test_nenhum_funcionario_importa_outro_funcionario():
    """
    Dez Funcionários que se chamam direto são até noventa ligações para manter.
    Dez que reagem a Fatos são dez. É essa ausência de seta que permite o
    décimo entrar sem tocar nos nove.

    Hoje existe um só, então o portão passa por vacuidade — e é exatamente por
    isso que ele precisa existir agora: quando o Atendimento nascer, é este
    teste que vai dizer se a promessa se sustentou.
    """
    infracoes = []

    for modulo in modulos_dos_funcionarios():
        meu_pacote = pacote_de(modulo)

        for importado in importados_por(modulo):
            if not importado.startswith("agents."):
                continue
            outro = importado.split(".")[1]
            if outro != meu_pacote:
                infracoes.append(f"{modulo.relative_to(RAIZ)} importa {importado}")

    assert not infracoes, "Funcionário conhecendo outro Funcionário:\n" + "\n".join(
        infracoes
    )


# ---- P2: nenhum Funcionário sabe por qual canal a pessoa chegou ----
def test_nenhum_funcionario_importa_canal():
    """
    A porta traduz mundo -> Fato. O Funcionário recebe sempre a mesma forma:
    quem, o quê, quando. Importar um canal é o jeito mais direto de quebrar
    isso, e é o que este portão fecha.
    """
    infracoes = [
        f"{m.relative_to(RAIZ)} importa {i}"
        for m in modulos_dos_funcionarios()
        for i in importados_por(m)
        if any(canal in i.lower() for canal in CANAIS)
    ]

    assert not infracoes, "Funcionário importando canal:\n" + "\n".join(infracoes)


def test_nenhum_vocabulario_de_canal_NOVO_dentro_do_funcionario():
    """
    Além do import: nome de canal escrito em qualquer lugar do pacote é sinal
    de que o Funcionário está sabendo por onde a pessoa chegou.

    A única ocorrência conhecida está declarada em EXCECAO_CONHECIDA, com o
    motivo. Qualquer outra falha aqui.
    """
    arquivo_permitido, linha_permitida = EXCECAO_CONHECIDA

    infracoes = []
    for modulo in modulos_dos_funcionarios():
        relativo = str(modulo.relative_to(RAIZ))

        for numero, linha in enumerate(
            modulo.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not any(canal in linha.lower() for canal in CANAIS):
                continue
            if relativo == arquivo_permitido and linha.strip() == linha_permitida:
                continue
            infracoes.append(f"{relativo}:{numero}: {linha.strip()}")

    assert not infracoes, "vocabulário de canal dentro do Funcionário:\n" + "\n".join(
        infracoes
    )


def test_a_excecao_conhecida_ainda_existe():
    """
    O contrário do teste acima, e igualmente necessário: se a instrução mudar e
    a frase sair, a exceção vira letra morta e tem que ser removida daqui. Um
    portão que carrega exceção obsoleta ensina a ignorar exceções.
    """
    arquivo, linha = EXCECAO_CONHECIDA
    conteudo = (RAIZ / arquivo).read_text(encoding="utf-8")

    assert linha in conteudo, (
        f"a exceção documentada não existe mais em {arquivo} — "
        "remova EXCECAO_CONHECIDA deste arquivo"
    )


# ---- a memória não pertence a Funcionário ----
def test_a_memoria_corporativa_nao_conhece_funcionario():
    """
    Norma M-3.5 a M-3.7: a memória é da empresa. Se ela importasse um
    Funcionário, o que o SDR escreve seria do SDR, e o Atendimento não poderia
    continuar de onde ele parou — que é a coisa toda.
    """
    for modulo in ("core/memoria_corporativa.py", "core/dominios.py"):
        importados = importados_por(RAIZ / modulo)

        assert not [i for i in importados if i.startswith("agents.")], (
            f"{modulo} conhece um Funcionário"
        )


def test_a_memoria_corporativa_nao_conhece_canal():
    """
    A Mensagem guarda `canal` como dado — um texto que veio de fora. Isso é
    diferente de a memória saber o que é WhatsApp: ela não trata nenhum canal
    de forma especial, e por isso canal novo não exige migração nem código.
    """
    for modulo in ("core/memoria_corporativa.py", "core/dominios.py"):
        codigo = (RAIZ / modulo).read_text(encoding="utf-8").lower()

        # A palavra aparece em comentário explicando a norma; o que não pode
        # existir é ramificação por canal.
        assert 'canal == "' not in codigo, f"{modulo} ramifica por canal"
        assert "if canal" not in codigo, f"{modulo} ramifica por canal"
