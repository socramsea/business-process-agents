"""
Prova a memória corporativa: Pessoa, Identidade e Mensagem.
Proves corporate memory: Person, Identity and Message.

Cada teste roda contra as DUAS implementações — em-memória e Postgres — porque
o contrato só vale se as duas se comportarem igual. A que não puder rodar
aparece como SKIPPED com o motivo, nunca some em silêncio.
Every test runs against both implementations; a missing one shows as SKIPPED.

Nenhum relógio: o instante entra por parâmetro em todo teste, como no resto do
projeto. Teste que depende do relógio da máquina é teste que falha sozinho de
madrugada.
"""

import sys
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.dominios import Identidade, Mensagem, Pessoa
from core.memoria_corporativa import MemoriaCorporativaEmMemoria, novo_id

T1 = datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc)
T2 = T1 + timedelta(days=7)
T3 = T1 + timedelta(days=14)

FORJA = "forja"
ZAP = "5511999990000"


# ---- Pessoa: identidade interna e opaca ----
def test_pessoa_desconhecida_devolve_None(memoria_corporativa):
    """Ninguém é erro — é alguém que nunca falou com esta empresa."""
    assert memoria_corporativa.pessoa_por_identidade(FORJA, "whatsapp", ZAP) is None


def test_primeira_mensagem_cria_a_pessoa(memoria_corporativa):
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )

    assert isinstance(pessoa, Pessoa)
    assert pessoa.empresa_id == FORJA
    assert pessoa.criada_em == T1


def test_o_id_da_pessoa_NAO_deriva_do_canal(memoria_corporativa):
    """
    A norma P-1.1, e ela existe por um motivo concreto: o `remoteJid` do
    WhatsApp nunca foi observado rodando neste projeto, e a issue #1916 do
    projeto Evolution relata que ele diverge do número real. Se o id fosse o
    telefone e o telefone estivesse errado, conversas de pessoas diferentes
    entrariam na mesma Pessoa — sem conserto depois.
    """
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )

    assert ZAP not in pessoa.id
    assert "whatsapp" not in pessoa.id
    assert pessoa.id != ZAP


def test_a_mesma_identidade_devolve_sempre_a_mesma_pessoa(memoria_corporativa):
    primeira = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )
    segunda = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T2
    )

    assert primeira.id == segunda.id, "a mesma pessoa não pode virar duas"
    assert segunda.criada_em == T1, "a data de criação é da primeira vez"


def test_pessoas_de_empresas_diferentes_nao_se_misturam(memoria_corporativa):
    """
    Norma P-1.5, e é a fronteira de segurança mais importante da plataforma:
    dois clientes da Forja podem ser concorrentes, e descobrir que o mesmo
    comprador falou com os dois é vazamento comercial.
    """
    memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )

    assert memoria_corporativa.pessoa_por_identidade("outra", "whatsapp", ZAP) is None


# ---- Identidade: separada da Pessoa ----
def test_identidade_e_entidade_separada(memoria_corporativa):
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )

    identidades = memoria_corporativa.identidades_de(FORJA, pessoa.id)

    assert len(identidades) == 1
    assert isinstance(identidades[0], Identidade)
    assert identidades[0].canal == "whatsapp"
    assert identidades[0].valor == ZAP
    assert identidades[0].pessoa_id == pessoa.id


def test_identidade_nasce_NAO_verificada(memoria_corporativa):
    """
    Norma P-1.2. Ter chegado por um canal prova que alguém usou aquele
    endereço, não quem.
    """
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )

    assert memoria_corporativa.identidades_de(FORJA, pessoa.id)[0].verificada is False


def test_duas_identidades_nao_verificadas_NAO_se_fundem_sozinhas(memoria_corporativa):
    """
    A norma P-1.4, provada pelo comportamento: a mesma pessoa do mundo real
    chegando por WhatsApp e por e-mail, sem ter provado controlar nenhum dos
    dois, produz DUAS Pessoas — e nada as une automaticamente.

    Unificar por conta própria misturaria vidas alheias com base em palpite.
    Quando a unificação existir, só evidência verificada vai autorizá-la.
    """
    por_zap = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )
    por_email = memoria_corporativa.resolver_pessoa(
        FORJA, "email", "marcos@forja.com.br", origem="formulario", quando=T2
    )

    assert por_zap.id != por_email.id, "não pode fundir por conta própria"
    assert len(memoria_corporativa.identidades_de(FORJA, por_zap.id)) == 1
    assert len(memoria_corporativa.identidades_de(FORJA, por_email.id)) == 1


# ---- Mensagem: a matéria-prima que estava sendo descartada ----
def test_a_mensagem_e_guardada_com_o_texto_inteiro(memoria_corporativa):
    """
    O buraco que a Fase A fecha. Até aqui o SDR guardava um placar de sinais e
    um contador; o que a pessoa escreveu era usado para extrair sinal e
    descartado. Sem isto, nenhum Funcionário consegue continuar de onde outro
    parou, porque não existe "última conversa".
    """
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )

    mensagem = memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA,
        pessoa_id=pessoa.id,
        quem_falou="pessoa",
        texto="tenho uma clinica em Botafogo e perco paciente no WhatsApp",
        canal="whatsapp",
        quando=T1,
    )

    assert isinstance(mensagem, Mensagem)
    assert mensagem.texto == "tenho uma clinica em Botafogo e perco paciente no WhatsApp"
    assert mensagem.quem_falou == "pessoa"


def test_a_conversa_sai_em_ordem_de_tempo(memoria_corporativa):
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )
    for quando, texto in ((T3, "terceira"), (T1, "primeira"), (T2, "segunda")):
        memoria_corporativa.registrar_mensagem(
            empresa_id=FORJA,
            pessoa_id=pessoa.id,
            quem_falou="pessoa",
            texto=texto,
            canal="whatsapp",
            quando=quando,
        )

    conversa = memoria_corporativa.conversa_de(FORJA, pessoa.id)

    assert [m.texto for m in conversa] == ["primeira", "segunda", "terceira"]


def test_a_conversa_atravessa_canais(memoria_corporativa):
    """
    Norma C-2.3: o canal é atributo da Mensagem. Uma conversa que começa no
    WhatsApp e continua por e-mail é a MESMA conversa, e nenhum Funcionário
    precisa saber a diferença.
    """
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )
    memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA, pessoa_id=pessoa.id, quem_falou="pessoa",
        texto="oi pelo zap", canal="whatsapp", quando=T1,
    )
    memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA, pessoa_id=pessoa.id, quem_falou="pessoa",
        texto="segue por email", canal="email", quando=T2,
    )

    conversa = memoria_corporativa.conversa_de(FORJA, pessoa.id)

    assert len(conversa) == 2, "é uma conversa só"
    assert [m.canal for m in conversa] == ["whatsapp", "email"]


def test_quem_a_empresa_respondeu_tambem_entra(memoria_corporativa):
    """A conversa é o que foi dito dos dois lados, não só o que chegou."""
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )
    memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA, pessoa_id=pessoa.id, quem_falou="pessoa",
        texto="voces atendem clinica?", canal="whatsapp", quando=T1,
    )
    memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA, pessoa_id=pessoa.id, quem_falou="funcionario",
        texto="atendemos sim", canal="whatsapp", quando=T2,
    )

    assert [m.quem_falou for m in memoria_corporativa.conversa_de(FORJA, pessoa.id)] == [
        "pessoa",
        "funcionario",
    ]


def test_quem_falou_invalido_e_recusado(memoria_corporativa):
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )

    with pytest.raises(ValueError, match="quem_falou"):
        memoria_corporativa.registrar_mensagem(
            empresa_id=FORJA, pessoa_id=pessoa.id, quem_falou="robo",
            texto="oi", canal="whatsapp", quando=T1,
        )


def test_reentrega_do_canal_nao_duplica_a_conversa(memoria_corporativa):
    """
    Canal que reentrega por timeout inventaria conversa que não houve. Com o
    identificador de origem, reprocessar devolve o que já existe.
    """
    pessoa = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )
    primeira = memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA, pessoa_id=pessoa.id, quem_falou="pessoa",
        texto="oi", canal="whatsapp", quando=T1, externo="MSG-1",
    )
    repetida = memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA, pessoa_id=pessoa.id, quem_falou="pessoa",
        texto="oi", canal="whatsapp", quando=T1, externo="MSG-1",
    )

    assert primeira.id == repetida.id
    assert len(memoria_corporativa.conversa_de(FORJA, pessoa.id)) == 1


def test_conversas_de_pessoas_diferentes_nao_se_misturam(memoria_corporativa):
    uma = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", ZAP, origem="conversa", quando=T1
    )
    outra = memoria_corporativa.resolver_pessoa(
        FORJA, "whatsapp", "5511888880000", origem="conversa", quando=T1
    )
    memoria_corporativa.registrar_mensagem(
        empresa_id=FORJA, pessoa_id=uma.id, quem_falou="pessoa",
        texto="da primeira", canal="whatsapp", quando=T1,
    )

    assert len(memoria_corporativa.conversa_de(FORJA, uma.id)) == 1
    assert memoria_corporativa.conversa_de(FORJA, outra.id) == []


# ---- imutabilidade ----
def test_a_mensagem_e_imutavel_no_objeto():
    """
    Norma C-2.4. Correção é mensagem nova, nunca edição da anterior — memória
    que se reescreve não é memória.
    """
    mensagem = Mensagem(
        empresa_id=FORJA, id="m1", pessoa_id="p1", quem_falou="pessoa",
        texto="original", canal="whatsapp", quando=T1,
    )

    with pytest.raises(FrozenInstanceError):
        mensagem.texto = "reescrito"


def test_o_contrato_NAO_tem_como_alterar_nem_apagar_mensagem():
    """
    A ausência é o projeto: não há caminho porque não deve haver. Este teste
    existe para alguém que adicionar `atualizar_mensagem` por conveniência
    descobrir na hora que está mudando a constituição, não o código.
    """
    metodos = dir(MemoriaCorporativaEmMemoria)

    for proibido in ("atualizar_mensagem", "apagar_mensagem", "editar_mensagem"):
        assert proibido not in metodos


def test_o_contrato_ainda_NAO_unifica_pessoas():
    """
    Unificação não faz parte da Fase A. A estrutura que a torna possível existe
    (Identidade separada de Pessoa); a operação não. Quando existir, identidade
    não verificada nunca poderá fundir sozinha.
    """
    assert "unificar_pessoas" not in dir(MemoriaCorporativaEmMemoria)


# ---- o id opaco ----
def test_ids_sao_diferentes_a_cada_chamada():
    assert novo_id() != novo_id()


def test_o_id_nao_carrega_informacao():
    """Opaco quer dizer isto: só hexadecimal, sem nada legível dentro."""
    gerado = novo_id()

    assert len(gerado) == 32
    assert all(c in "0123456789abcdef" for c in gerado)
