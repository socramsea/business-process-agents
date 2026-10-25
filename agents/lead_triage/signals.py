"""
Signal extraction — turns the lead's own words into scoreable signals.
Extração de sinais — transforma o que o lead escreveu em sinais pontuáveis.

Isto fecha o buraco central: até aqui o 'message' chegava no agente e morria lá.
This closes the central gap: until now 'message' reached the agent and died there.
"""

import json
from typing import Any

import anthropic

from core.base_enricher import BaseEnricher
from core.log import LOGGER

MODELO = "claude-opus-5"

# Teto POR TENTATIVA. O SDK repete 3 vezes por padrão (max_retries=2), então o
# pior caso é 3x isto. Sem timeout explícito o default é 600s, e 3x600 deixaria
# um lead esperando meia hora antes de a falha sequer virar observação.
# Per-attempt ceiling. The SDK retries 3x, so worst case is 3x this.
TIMEOUT_SEGUNDOS = 30.0

# Preço do claude-opus-5 em dólar por milhão de tokens, conforme a tabela
# vigente. CONSTANTE MANUAL: se a Anthropic mudar o preço, este número passa a
# mentir sem avisar. Os tokens no log são fato; o custo é aritmética em cima
# deles e só vale enquanto estes dois números estiverem certos.
# Manual constant — if pricing changes, this silently lies. Tokens are the fact.
PRECO_ENTRADA_POR_MILHAO = 5.00
PRECO_SAIDA_POR_MILHAO = 25.00

# Teto de saída. O modelo pensa por padrão no Opus 5, e o pensamento conta
# aqui dentro junto com a resposta — apertado demais, a resposta trunca.
MAX_TOKENS = 8192

# Componente de produção, não um prompt de rascunho. Toda alteração aqui deve
# ser validada rodando `python3 -m evals.rodar` antes de virar commit.
# Production component, not a draft prompt. Validate every change with the evals.
INSTRUCAO = """# Objetivo

Você lê a mensagem de um lead e extrai sinais de intenção de compra para um
vendedor. Devolve apenas os campos definidos em "Campos de Saída".

# Regras Gerais

- Classifique EXCLUSIVAMENTE pelo texto da mensagem.
- Não use conhecimento externo, não invente, não suponha sem evidência.
- Não infira um sinal a partir de outro: quem tem pressa não tem orçamento por
  causa disso, e quem cita valor não vira decisor por causa disso.
- Na dúvida, marque `false`. Um sinal falso é pior que sinal nenhum, porque manda
  o vendedor para a ligação errada.

# Critérios de Autoridade

`autoridade` = a pessoa tem poder de decisão para contratar.

Marque `true` quando o texto trouxer alguma destas evidências:

- Posse do negócio, inclusive implícita: "tenho uma clínica", "minha empresa",
  "meu consultório", "abri uma clínica", "nossa loja".
- Cargo de decisão declarado: "sou fundador", "sou sócio", "sou dono",
  "sou proprietário", "administro", "sou responsável pela empresa".
- Intenção declarada sobre o próprio negócio: "quero implantar na minha empresa",
  "preciso para minha clínica".
- Poder de compra declarado, ainda que não seja o dono: "eu aprovo o orçamento",
  "sou responsável pelas compras", "eu que decido o fornecedor".

Marque `false` quando:

- A pessoa se identificar como funcionário sem poder de decisão declarado.
- A pessoa falar em nome de terceiros: agência, prestador, consultor, fornecedor.
- A pessoa for estudante, pesquisador ou curioso.
- Não houver evidência suficiente no texto.

Um possessivo aplicado ao negócio ("minha clínica", "nossa loja") já é evidência
suficiente. Um cargo sem possessivo e sem poder de compra declarado
("sou gerente de marketing da Acme") não é.

# Critérios do Resumo

O `resumo` é a anotação que o vendedor lê antes de ligar. Ele deve:

- Ter no máximo 15 palavras.
- Estar em primeira pessoa, como se o lead falasse: "Quero...", "Preciso...".
- Trazer só a intenção comercial principal.
- Nunca começar com "A pessoa", "O lead" ou "O cliente".
- Nunca ser uma pergunta dirigida a quem vende, nem verbo no infinitivo
  ("Coletar orçamentos"), nem descrição de terceiro ("Cliente precisa de X").

Quando a mensagem NÃO trouxer intenção comercial — saudação, spam, texto sem
conteúdo — não invente intenção e não descreva a mensagem de fora
("Mensagem sem intenção comercial"). Escreva, ainda em primeira pessoa, o que a
pessoa fez: "Entrei em contato sem dizer o que preciso."

# Critérios do Agente Indicado

`agente_indicado` = qual dos quatro agentes eu implantaria neste cliente.
Classifique pelo agente que RESOLVE a dor, não pelo mecanismo que falha, e nunca
pelo produto pedido. Onde o trabalho trava não é a mesma pergunta que quem assume
o trabalho.

Ache na mensagem a oração que diz o que está dando errado hoje: o que a pessoa
perde, o que ela refaz na mão, o que ela não dá conta. Se ela não existir,
`indefinido`.

- `comercial`: lead perdido por demora, follow-up manual, sem controle de quem
  está no funil, CRM desatualizado. O que se perde é a venda.
- `atendimento`: volume de mensagens sem resposta, mesma pergunta repetida,
  atendimento fora do horário. O que se perde é a conversa.
- `marketing`: falta de conteúdo, presença digital fraca, campanha sem
  consistência. A falha é anterior ao contato: o lead nem chega.
- `operacional`: tarefa repetitiva, documento montado à mão, relatório manual,
  pesquisa recorrente. Repetição que não é conversa.

Três testes, nesta ordem, antes de escolher:

1. Produto ou dor? "Quero um vídeo", "preciso de um CRM" nomeiam produto —
   descarte. Ausência declarada é dor ("não tenho conteúdo postado"); desejo
   declarado é produto ("preciso de conteúdo").
2. Placar ou mecanismo? Métrica de vaidade e vocabulário de domínio não são dor.
   "Vendas caíram 22%", "tenho 312 seguidor e o concorrente tem 9 mil", "preciso
   de um CRM" trazem número ou jargão, não ruptura. Sem uma ruptura mecânica
   descrita — o que se perde, o que se refaz, o que não dá conta — é `indefinido`,
   mesmo que a palavra puxe forte para uma das áreas.
3. Causa ou consequência? Dores ligadas por "porque" — "perco venda PORQUE não
   dou conta de responder" — classificam pela CAUSA: aqui, `atendimento`. Duas
   dores soltas, sem elo entre si, `indefinido`.

Fronteiras: lead que não chega é marketing, lead que chegou e se perdeu é
comercial. Repetição de responder gente é atendimento.

Atrito manual não decide sozinho — decide de QUE trabalho ele é:

- Atrito em produzir ou distribuir conteúdo é `marketing`. Montar post, cortar
  foto, escrever legenda, publicar: o trabalho é da função de marketing, por mais
  braçal que seja.
- Atrito em processar dado interno é `operacional`. Conferir guia, montar escala,
  renomear laudo, digitar nota, consolidar relatório: nenhum dos outros três
  agentes assume isso.
- Atrito braçal que só existe porque alguém perguntou é `atendimento`, ainda que o
  trabalho seja consultar sistema ou planilha. O teste: a tarefa desapareceria se
  ninguém tivesse escrito? Se sim, é `atendimento`. Se ela aconteceria de qualquer
  jeito — a escala da fábrica, o laudo do laboratório, o fechamento do mês — é
  `operacional`.

`indefinido` é escolha, não desistência. Use sempre que não houver sinal claro:
só o produto pedido, só pedido de informação, queixa sem mecanismo, saudação,
spam. Não escolha o mais provável entre os quatro — descobrir é melhor que
inventar.

Não entram na decisão: o produto pedido, os outros campos deste schema, o ramo do
negócio (clínica não é `atendimento`, loja não é `comercial`) e o canal citado
(WhatsApp e Instagram são onde a dor aparece, não qual ela é).

# Campos de Saída

- `orcamento` (boolean): a pessoa citou um valor, uma verba, uma faixa de preço
  ou a própria capacidade de pagar. PERGUNTAR o preço não conta: "quanto custa?",
  "qual o valor?" e a palavra "orçamento" sozinha são pedidos de informação, não
  orçamento declarado.
- `urgencia` (boolean): citou prazo, data ou pressa.
- `autoridade` (boolean): conforme "Critérios de Autoridade".
- `descadastro` (boolean): pediu para sair, parar de receber ou declarou não ter
  interesse.
- `agente_indicado` (string): um entre `comercial`, `atendimento`, `marketing`,
  `operacional` ou `indefinido`, conforme "Critérios do Agente Indicado".
- `resumo` (string): conforme "Critérios do Resumo".

# Exemplos Positivos

"tenho uma clínica em Botafogo, quero vídeo institucional, até 8 mil, pra outubro"
→ orcamento true, urgencia true, autoridade true, descadastro false
→ resumo: "Quero vídeo institucional para minha clínica até outubro."

"sou responsável pelas compras da rede e preciso de proposta"
→ orcamento false, urgencia false, autoridade true, descadastro false
→ resumo: "Preciso de proposta para a rede onde faço as compras."

"quero um vídeo, o povo pergunta preço no direct e eu não dou conta de responder"
→ agente_indicado atendimento (a dor é o volume de mensagem; o vídeo é o produto)

"emito nota e contrato na mão pra cada cliente novo, queria um site"
→ agente_indicado operacional (a dor é o documento repetitivo; o site é o produto)

# Exemplos Negativos

"sou analista de marketing na Acme, meu chefe pediu pra pesquisar preços"
→ autoridade false (funcionário sem poder de decisão declarado)

"somos uma agência e buscamos parceiro de vídeo para nossos clientes"
→ autoridade false (fala por terceiros)

"faço TCC sobre marketing digital, pode me explicar como funciona?"
→ autoridade false (estudante)

"tenho uma clínica em Botafogo, quero vídeo institucional, até 8 mil, pra outubro"
→ agente_indicado indefinido (verba e prazo não são dor; nenhuma falha descrita)

"quero contratar um chatbot de atendimento pro meu site"
→ agente_indicado indefinido (nomeou produto da área de atendimento, sem dor)"""

# Catálogo de agentes para onde o lead pode ser encaminhado. 'indefinido' é
# resposta legítima, não buraco: encaminhar errado custa mais que não encaminhar.
# 'indefinido' is a legitimate answer, not a gap.
AGENTES = ("comercial", "atendimento", "marketing", "operacional", "indefinido")

ESQUEMA_SINAIS: dict[str, Any] = {
    "type": "object",
    "properties": {
        "orcamento": {"type": "boolean"},
        "urgencia": {"type": "boolean"},
        "autoridade": {"type": "boolean"},
        "descadastro": {"type": "boolean"},
        # enum fecha a porta no nível da API: o modelo não consegue devolver um
        # agente que não existe. Validar depois seria tarde.
        # The enum closes the door at the API level.
        "agente_indicado": {"type": "string", "enum": list(AGENTES)},
        "resumo": {"type": "string"},
    },
    # Strict mode da OpenAI exige TODO campo de properties aqui dentro.
    "required": [
        "orcamento",
        "urgencia",
        "autoridade",
        "descadastro",
        "agente_indicado",
        "resumo",
    ],
    "additionalProperties": False,
}


class MensagemEnricher(BaseEnricher):
    """
    A mensagem do lead tratada como fonte, igual site ou YouTube.
    The lead's message treated as a source, same as site or YouTube.

    Herda de BaseEnricher de propósito: assim o enriquecer() já dá isolamento
    de falha de graça — LLM fora do ar não derruba o atendimento do lead.
    """

    nome = "mensagem"

    def __init__(self, cliente: Any = None):
        # Costura para teste: em produção fica None e cria o cliente real.
        # Test seam: None in production, so a real client is created.
        self._cliente = cliente

    def buscar(self, pista: str) -> dict:
        """A 'pista' aqui é a própria mensagem do lead."""
        if not pista.strip():
            return self._vazio("mensagem vazia")

        cliente = self._cliente or anthropic.Anthropic(timeout=TIMEOUT_SEGUNDOS)

        resposta = cliente.messages.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            system=INSTRUCAO,
            messages=[{"role": "user", "content": pista}],
            # output_config ainda não é parâmetro tipado nesta versão do SDK;
            # extra_body entrega igual. Vira parâmetro direto quando subirmos.
            extra_body={
                "output_config": {
                    "effort": "low",
                    "format": {"type": "json_schema", "schema": ESQUEMA_SINAIS},
                }
            },
        )

        # O consumo já vinha na resposta e estava sendo descartado. Sem isto,
        # o custo de atender um lead não existe em lugar nenhum — e mensagem
        # gigante custa dez conversas normais sem deixar rastro.
        # The usage was already in the response and was being thrown away.
        _registrar_consumo(resposta)

        # O modelo pode recusar por segurança: vem HTTP 200 com content vazio.
        # Ler content[0] direto quebraria aqui.
        if resposta.stop_reason == "refusal":
            return self._vazio("o modelo recusou analisar esta mensagem")

        # A resposta pode trazer blocos que não são texto (pensamento, tools).
        # Pegar content[0] às cegas é como ler a primeira linha e chamar de resposta.
        texto = ""
        for bloco in resposta.content:
            if getattr(bloco, "type", "") == "text":
                texto = str(getattr(bloco, "text", ""))
                break

        if not texto:
            return self._vazio("o modelo não devolveu texto")

        return self._ok(_como_dicionario(texto))


def pontuar_sinais(resultado: dict, pesos: dict) -> tuple[int, list[str]]:
    """
    Transforma os sinais em pontos e observações, igual pontuar_enriquecimento.
    Turns signals into points and observations, like pontuar_enriquecimento.

    Os pesos vêm por parâmetro (config do tenant), nunca fixos no código.

    Devolve a soma CRUA, que pode ser negativa. É de propósito: o peso negativo
    do descadastro só cancela os pontos do enriquecimento se chegar negativo até
    o total. Zerar aqui deixaria "me tira do mailing" valendo os pontos do site.
    Returns the RAW sum, possibly negative — clamping happens at the total.
    """
    status = resultado.get("status")
    detalhe = resultado.get("detalhe")

    if status == "vazio":
        return 0, [f"mensagem: sem sinal de compra ({detalhe})"]

    if status == "falha":
        return 0, [f"mensagem: não consegui analisar ({detalhe})"]

    if status != "ok":
        return 0, [f"mensagem: resultado em formato inesperado ({status!r})"]

    sinais = resultado.get("dados") or {}

    pontos = 0
    observacoes = []

    if sinais.get("resumo"):
        observacoes.append(f"mensagem: {sinais['resumo']}")

    for nome, peso in pesos.items():
        if sinais.get(nome) is True:
            pontos += peso
            observacoes.append(f"sinal: {nome} ({peso:+d})")

    return pontos, observacoes


def _como_dicionario(texto: str) -> dict:
    """
    JSON válido não garante objeto: `[1,2]` e `"oi"` passam pelo json.loads e
    quebram no .get() lá na frente com AttributeError sem explicação.
    Valid JSON is not necessarily an object.
    """
    carregado = json.loads(texto)
    if not isinstance(carregado, dict):
        raise ValueError(f"esperava objeto JSON, veio {type(carregado).__name__}")
    return carregado


def _registrar_consumo(resposta: Any) -> None:
    """
    Emite tokens e custo de uma chamada. Nunca levanta exceção.
    Emits tokens and cost for one call. Never raises.

    Blindado de propósito: log de custo não pode derrubar o atendimento de um
    lead. Se `usage` não vier — dublê de teste, mudança de SDK — grava zero e
    segue. Falhar aqui trocaria um problema de contabilidade por um de produção.
    Deliberately defensive: cost logging must never break lead handling.
    """
    consumo = getattr(resposta, "usage", None)
    entrada = int(getattr(consumo, "input_tokens", 0) or 0)
    saida = int(getattr(consumo, "output_tokens", 0) or 0)

    custo = (
        entrada * PRECO_ENTRADA_POR_MILHAO + saida * PRECO_SAIDA_POR_MILHAO
    ) / 1_000_000

    LOGGER.info(
        "llm consultado",
        extra={
            "modelo": MODELO,
            "tokens_entrada": entrada,
            "tokens_saida": saida,
            "custo_usd": round(custo, 6),
            # O request_id é o que a Anthropic pede quando você abre suporte.
            # Sai de graça e só serve quando algo dá errado.
            "request_id": getattr(resposta, "_request_id", None),
        },
    )
