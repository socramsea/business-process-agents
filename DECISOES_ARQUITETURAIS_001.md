# Decisões Arquiteturais 001

**Complemento normativo de [`ARQUITETURA_EMPRESA_DIGITAL.md`](ARQUITETURA_EMPRESA_DIGITAL.md).**
Onde houver divergência, este documento prevalece — ele é mais novo e mais
específico.

| | |
|---|---|
| Versão | 1.2 |
| Data | 2026-08-01 |
| Estado | **Arquitetura fechada e aprovada · 10 de 12 critérios atendidos · restam 2 ações, nenhuma decisão** |
| Código | `2c68cf8`, 163 testes verdes, Fase 1 sem commit |

> **v1.1** — DE-1 e DE-2 respondidas pelo Marcos e incorporadas (§8). Delas
> derivam cinco normas novas: M-3.8 a M-3.11 (remoção e anonimização) e F-4.3
> (autonomia). As derivações estão marcadas como tais: elas aplicam a decisão,
> não a substituem, e podem ser revogadas por ele.
>
> **Arquitetura fechada. A implementação ainda não pode começar** — quatro
> critérios de aceite continuam abertos (§7), e nenhum deles é arquitetural.

---

## 1. O que é uma Pessoa

### Definição

> Uma **Pessoa** é um ser humano ou organização com quem uma Empresa Digital
> mantém relação. Ela existe independentemente de qualquer canal, de qualquer
> conversa e de qualquer Funcionário.

Uma Pessoa **não é** um lead, um contato, um registro nem um número de telefone.
Lead é um *estado* da relação num momento — não é o que a pessoa é.

### Identidade

Toda Pessoa tem um identificador **interno, opaco e permanente**, gerado pela
plataforma.

**Norma P-1.1 — o identificador de uma Pessoa nunca deriva de um valor de
canal.** Nem telefone, nem e-mail, nem `remoteJid`, nem `@usuario`.

*Justificativa, e ela é concreta:* hoje o código deriva identidade assim —

```python
# core/evolution.py
"telefone": str(remoto).split("@")[0]      # remoteJid → telefone → id da pessoa
```

Sete testes desse módulo se chamam `test_HIPOTESE_*` porque esse contrato nunca
foi observado rodando, e a issue #1916 do projeto Evolution se chama
*"remoteJid is different than the real whatsapp number"*. Se o id da Pessoa for
esse valor e ele estiver errado, **conversas de pessoas diferentes entram na
mesma Pessoa — e isso não tem conserto depois**, porque não há como saber de
quem era cada mensagem. Identificador interno torna esse erro reparável: corrige-se
a Identidade, a Pessoa continua a mesma.

### Identidades

Uma Pessoa é **alcançada** por Identidades. Cada Identidade é um par
canal + valor, com procedência:

```
Identidade
├── canal        whatsapp · email · instagram · telegram · site · voz · api
├── valor        o identificador naquele canal
├── verificada   a pessoa provou controlar isto?
├── origem       como soubemos (conversa, formulário, importação)
└── desde        quando
```

Uma Pessoa tem N Identidades. Uma Identidade pertence a **uma só** Pessoa,
dentro de uma Empresa Digital.

**Norma P-1.2 — `verificada` só é verdadeira quando a pessoa provou controlar o
identificador**: respondeu a um código, clicou num link enviado para ali,
autenticou. Ter chegado por um canal **não** verifica a identidade daquele
canal — prova que alguém usou aquele endereço, não quem.

### Unificação de identidade

Quando se descobre que duas Pessoas são a mesma, elas se **unificam**.

**Norma P-1.3 — unificação nunca destrói.** Não reescreve conversa, não apaga
Pessoa, não reatribui mensagem. Registra-se um vínculo — *"estas duas são a
mesma"* — com autor, momento e evidência. As leituras passam a enxergar as duas
como uma.

*Justificativa:* unificação é a operação mais perigosa do sistema, porque
unificar duas pessoas diferentes mistura vidas alheias. Se ela destruísse, o
erro seria permanente. Sendo um vínculo, desfaz-se.

**Norma P-1.4 — Identidade não verificada nunca unifica sozinha.** Só evidência
verificada autoriza unificação automática. O resto vira proposta.

Isto é o que contém, na arquitetura, o risco do `remoteJid`: mesmo que o valor
esteja errado, ele não consegue fundir duas Pessoas por conta própria.

### Isolamento entre Empresas Digitais

**Norma P-1.5 — a mesma pessoa do mundo real, em duas Empresas Digitais, são
duas Pessoas.** Sem exceção, sem correlação, sem "identidade global".

*Justificativa:* dois clientes da Forja podem ser concorrentes. Descobrir que
o mesmo comprador falou com os dois é vazamento comercial — o pior tipo de falha
que esta plataforma pode ter. A perda é real (não há visão global) e o preço de
não ter é aceitável.

### Responsabilidades

| Uma Pessoa **é** | Uma Pessoa **não é** |
|---|---|
| dona dos dados dela | dona da conversa (§2) |
| sujeito de direito à remoção | responsável por manter os próprios dados |
| alcançável por várias Identidades | um telefone |
| origem de observações | autora de aprendizados |

---

## 2. O que é uma Conversa

### Definição

> Uma **Conversa** é a sequência ordenada e imutável de tudo que foi dito entre
> uma Empresa Digital e uma Pessoa, independentemente de canal.

**Norma C-2.1 — a unidade armazenada é a Mensagem.** "Conversa" é a sequência,
não um objeto com começo e fim.

*Justificativa:* sessão exige uma regra de corte — silêncio de 24h? troca de
assunto? Toda regra dessas é arbitrária e vira dado errado. Fatiar em sessões,
quando alguém precisar, é derivável do que já está guardado. O contrário não é.

```
Mensagem
├── pessoa       de quem é a relação
├── quem falou   pessoa · funcionário · humano da empresa
├── texto        o que foi dito, íntegro
├── canal        por qual porta entrou ou saiu
├── quando
└── externo      o identificador no sistema de origem (deduplicação)
```

### Quem é o proprietário

**Norma C-2.2 — a Conversa pertence à Empresa Digital.**

Não ao Funcionário que atendeu: se pertencesse a ele, o Atendimento não poderia
continuar o que o SDR começou, e a inteligência coletiva morre no nascimento.

Não ao Canal: WhatsApp é porta, não dono.

Não à Pessoa: ela tem direitos sobre o conteúdo (§8, DE-1) — direito não é
propriedade.

### Relação com Canal

**Norma C-2.3 — o canal é atributo da Mensagem, nunca da Conversa nem do
Funcionário.** Uma conversa que começa no WhatsApp e continua por e-mail é a
mesma conversa. O Funcionário não sabe a diferença, e é essa ignorância que
permite trocar de canal sem tocar em Funcionário nenhum.

### Relação com Funcionários

Funcionários **leem** a Conversa e **acrescentam** ao fim. Nenhum edita, nenhum
apaga, nenhum reserva.

**Norma C-2.4 — a Mensagem é imutável depois de gravada.** Correção é mensagem
nova, não edição da anterior. Memória que se reescreve não é memória.

### Retenção

**Norma C-2.5 — retenção é parâmetro por Empresa Digital, e o mecanismo é
obrigatório desde o primeiro dia.** O valor é do cliente; a capacidade de
expurgar é da plataforma.

Construir sem o mecanismo significa descobrir que ele falta no dia em que um
cliente exigir — e nesse dia ele é retroativo, que é a pior hora.

**Norma C-2.7 — fim de retenção apaga, inclusive o que já é anônimo.** Estar
anonimizado permite permanecer; não permite permanecer para sempre. As duas
condições valem juntas (M-3.11).

### Histórico

**Norma C-2.6 — todo Fato aponta para a Mensagem que o originou.** Um
aprendizado sem caminho de volta até as conversas é boato. Isto é o que torna
verificável o P3 da Constituição.

---

## 3. O que é a Memória Corporativa

### Definição

> A **Memória Corporativa** é tudo que uma Empresa Digital sabe. Ela é uma só.
> Não existe memória privada de Funcionário.

### As três camadas

Toda informação da plataforma cai em exatamente uma:

#### Camada 1 — Nunca pode ser perdida

| O que | Por quê |
|---|---|
| Texto íntegro das Mensagens | é a evidência de tudo o mais |
| Decisões, com motivo e autor | P6: nada some em silêncio |
| Identidades e vínculos de unificação | perder isto é perder quem é quem |
| Aprendizados, com evidência | sem a evidência viram boato |
| Registro de remoção | provar que se apagou é parte de ter apagado |

**Norma M-3.1 — o que está na camada 1 só sai por pedido explícito da Pessoa ou
por fim de retenção. Nunca por conveniência técnica, nunca por espaço.**

#### Camada 2 — Pode ser resumida

Informação cuja forma completa perde valor com o tempo, mas cujo sentido não.
Mensagens antigas além da retenção operacional, conversas encerradas há muito.

**Norma M-3.2 — todo resumo registra o que substituiu**: quantas mensagens, que
período, quando foi resumido, por quem. Resumo que não diz o que apagou é perda
disfarçada de organização.

**Norma M-3.3 — resumir não é permitido enquanto o material for a única
evidência de um Aprendizado ativo.** Ou o aprendizado cai junto, ou o resumo
espera.

#### Camada 3 — Pode ser descartada

| O que | Por quê |
|---|---|
| Envelope bruto do canal | já foi traduzido; guardar é guardar o WhatsApp dentro da memória |
| Recibos de entrega e leitura | operacional, não é conhecimento |
| Tentativas repetidas de uma mesma chamada | o resultado já virou Fato |
| Estado derivado (pontuação, contagens) | recalculável a partir da camada 1 |

**Norma M-3.4 — nada da camada 3 pode ser a única fonte de um Fato.** Se for, é
camada 1 e foi classificado errado.

### Remoção — o que sai quando a Pessoa pede para sair

Decidido em DE-1: *a identidade pode ser removida; o conhecimento corporativo só
permanece se estiver **efetivamente** anonimizado e dentro da retenção.*

As quatro normas abaixo **derivam** dessa decisão. São minhas, não do Marcos —
ele decidiu o critério, eu apliquei. Se a aplicação estiver errada, é ela que
muda.

**Norma M-3.8 — texto livre não é anonimizável, portanto não permanece.**
Uma mensagem como *"oi, aqui é o Marcos da Forja Criativa, em Botafogo"*
continua identificando depois de qualquer varredura automática — nome, empresa e
bairro estão no meio da frase, e nenhum deles está num campo. O texto das
Mensagens é apagado junto com a identidade.

*Consequência estrutural:* não existe "anonimizar mensagem". A anonimização
acontece **na extração**, não na remoção. O que sobrevive é o que já nasceu sem
dado identificável.

**Norma M-3.9 — sobrevive só o que nasceu não-identificável.**
Um Aprendizado — *"objeção recorrente: medo de erro da IA, 41 observações"* — não
nomeia ninguém e permanece. Uma Observação só permanece se tiver sido extraída
sem dado identificável.

*Consequência estrutural:* **isso é responsabilidade da instrução do
Funcionário**, e portanto verificável pela suíte de avaliação dele (P7). A
instrução que produz o resumo precisa ser explícita: o resumo descreve a dor,
nunca a pessoa. Hoje o campo `resumo` não tem essa regra, e isso vira item da
Fase A.

**Norma M-3.10 — a remoção deixa buraco visível, nunca silencioso.**
O Aprendizado que perdeu evidência registra quantas observações saíram e quando.

| | |
|---|---|
| ❌ continuar dizendo "41 observações" | mentira |
| ❌ passar a dizer "38" sem explicar | perda de rastro |
| ✅ "38 vigentes, 3 removidas a pedido em 2026-09-14" | verdade auditável |

É a mesma regra de M-3.2: o que substitui declara o que substituiu.

**Norma M-3.11 — permanecer exige as duas condições, sempre.** Não-identificável
**e** dentro da retenção. Anonimato não compra permanência eterna, e retenção
longa não legaliza dado identificável.

**Norma M-3.12 — a remoção é provável.** Fica registrado que houve remoção,
quando e sobre qual identidade — sem guardar a identidade removida. Apagar sem
poder demonstrar que apagou não satisfaz ninguém que pergunte.

### Como Funcionários compartilham conhecimento sem acoplamento

Eles não compartilham: **já é tudo da empresa.** Não há cópia, sincronização
nem pedido.

O desacoplamento vem de três regras mecânicas:

**Norma M-3.5 — Funcionário lê a Memória por domínio declarado, nunca por
consulta livre.** Ele declara "leio Pessoas e Conversas" e é isso que recebe.
Quem pode ler tudo acopla-se a tudo.

**Norma M-3.6 — Funcionário escreve na Memória apenas por Fato.** Nunca escrita
direta. O Fato tem autor, momento, motivo e evidência; escrita direta não tem
nada disso.

**Norma M-3.7 — Funcionário reage a Fato por tipo, jamais por autor.** O
Comercial reage a *"pessoa qualificada"*, não a *"o SDR qualificou"*. Reagir por
autor é conhecer o outro Funcionário pelo nome, que é a violação do P1.

O exemplo do Marcos, completo e sem uma seta ligando Funcionário a Funcionário:

```
SDR                  → Fato "objeção levantada: medo de erro da IA"   (×41)
Inteligência         → lê os 41 → Fato "aprendizado: objeção recorrente,
                                        41 observações, 90 dias, conversas [...]"
Conteúdo             → lê aprendizados → pauta que responde à objeção
Comercial            → lê aprendizados → garantia na proposta
Atendimento          → lê aprendizados → responde antes de perguntarem
```

Nenhum dos cinco importa, nomeia ou conhece qualquer um dos outros.

---

## 4. Modelo dos Funcionários

### O contrato

```
Funcionário
├── DECLARA
│   ├── função            uma frase: o que ele faz na empresa
│   ├── objetivo          o que é sucesso para ele
│   ├── fatos que lê      a que ele reage
│   ├── fatos que escreve o que ele registra
│   ├── domínios          o que da Memória ele consulta
│   ├── ferramentas       o que sabe usar
│   ├── instrução         versionada, com suíte de avaliação própria
│   └── métricas          como é avaliado
│
├── RECEBE               (e nada além disto)
│   ├── Empresa          identidade e configuração do cliente
│   ├── Gatilho          o Fato que o acordou
│   ├── Memória          leitura restrita aos domínios declarados
│   └── Ferramentas      instâncias já construídas, prontas
│
└── DEVOLVE
    └── lista de Fatos   pode ser vazia
```

### O que todo Funcionário recebe

**Norma F-4.1 — o Funcionário recebe tudo que precisa e nada que não declarou.**
Ele não constrói cliente HTTP, não abre conexão, não lê variável de ambiente,
não escolhe provedor de LLM. Recebe pronto.

*Justificativa:* Funcionário que constrói a própria dependência não pode ser
testado sem ela, não pode ser reconfigurado por cliente, e amarra a plataforma
a uma escolha técnica. Hoje isto está violado —
[`agent.py:80`](agents/lead_triage/agent.py#L80) escreve o provedor no código.

### O que todo Funcionário devolve

**Norma F-4.2 — um Funcionário devolve Fatos. Só. Nunca efeito colateral.**

Enviar mensagem, publicar conteúdo e emitir proposta **não** são coisas que o
Funcionário faz — são coisas que ele **decide**, e a decisão é um Fato. Quem
executa é um adaptador que reage àquele Fato.

*Justificativa:* é isto que torna possível o nível de autonomia (§8, DE-2). Um
Funcionário em modo "propõe" produz exatamente os mesmos Fatos de um em modo
"age" — muda só quem reage a eles. Se o Funcionário publicasse direto, autonomia
exigiria um `if` dentro de cada Funcionário, e um esquecido é um post não
autorizado no Instagram do cliente.

### Autonomia

Decidido em DE-2: *a autonomia pertence ao Funcionário; a Empresa apenas
restringe o teto; nenhuma configuração concede o que o Funcionário não tem por
projeto.*

Três níveis, declarados pelo Funcionário no seu contrato:

| Nível | O que faz |
|---|---|
| **observa** | registra Fatos e nada mais |
| **propõe** | prepara a ação e espera aprovação humana |
| **age** | executa e avisa |

**Norma F-4.3 — a autonomia efetiva é o menor dos dois.**

```
nivel_efetivo = min(declarado_pelo_funcionário, teto_da_empresa)
```

Um Funcionário que declara `propõe` **não passa a agir** porque um cliente marcou
uma caixinha. A configuração só desce.

**Norma F-4.4 — configuração que pede mais do que o Funcionário tem é rejeitada
na carga, não silenciada em execução.**

Duas linhas de defesa de propósito, e elas fazem coisas diferentes: rejeitar na
carga **avisa** que a expectativa do cliente está errada; limitar em execução
**protege** caso a rejeição falhe. Só limitar em silêncio deixaria o cliente
achando que contratou uma coisa e recebendo outra.

### O que nunca pode conhecer

| Não conhece | Consequência de conhecer |
|---|---|
| Outro Funcionário | dez Funcionários viram noventa ligações |
| O canal | trocar WhatsApp por outro vira reescrita de todos |
| Onde a Memória mora | trocar de banco vira reescrita de todos |
| Outra Empresa Digital | vazamento entre clientes |
| Qual provedor de LLM responde | tenant não pode escolher, custo não pode ser negociado |
| A régua do cliente como constante | segundo cliente exige deploy |

### Dependências proibidas

Verificáveis por leitura mecânica de `import`, dentro de `funcionarios/`:

```
PROIBIDO   from funcionarios.<outro>          →  viola P1
PROIBIDO   import httpx | psycopg | sqlite3   →  viola P2/P8 (infra crua)
PROIBIDO   import anthropic | openai          →  provedor é injetado
PROIBIDO   import os  (para ler ambiente)     →  configuração é injetada
PROIBIDO   qualquer nome de canal no código   →  viola P2

PERMITIDO  from nucleo.contratos import ...   →  os contratos
PERMITIDO  from nucleo.memoria import ...     →  as interfaces, não as implementações
PERMITIDO  stdlib pura                        →  datetime, typing, dataclasses
```

---

## 5. Empresa Digital — modelo conceitual

### Os dez domínios fundamentais

```
                          EMPRESA DIGITAL
                       (fronteira de isolamento)
                                 │
     ┌───────────┬───────────────┼───────────────┬───────────┐
     │           │               │               │           │
  PESSOA     CONVERSA        FUNCIONÁRIO      CANAL      PROCESSO
     │           │               │               │           │
     │           │               │               │           │
     └─────┬─────┴───────┬───────┴───────┬───────┘           │
           │             │               │                   │
        EVENTO       DECISÃO       CONHECIMENTO               │
       (o Fato)                                               │
           │             │               │                   │
           └─────────────┴───────┬───────┴───────────────────┘
                                 │
                              MEMÓRIA
                     (contém tudo acima, no tempo)
```

| Domínio | Uma frase |
|---|---|
| **Empresa** | O cliente. Fronteira de isolamento absoluta |
| **Pessoa** | Com quem a empresa se relaciona |
| **Conversa** | Tudo que foi dito, em ordem, imutável |
| **Funcionário** | Quem trabalha |
| **Canal** | Por onde entra e sai. Fora do alcance do Funcionário |
| **Evento (Fato)** | O que aconteceu ou passou a ser sabido |
| **Decisão** | Um Fato com motivo e alternativa descartada |
| **Conhecimento** | O que a empresa sabe. Observação (uma) ou Aprendizado (padrão) |
| **Processo** | Como esta empresa faz as coisas |
| **Memória** | O conjunto de tudo acima, ao longo do tempo |

### Como se relacionam

```
Empresa  1 ──── N  Pessoa                    Pessoa não atravessa Empresa (P-1.5)
Pessoa   1 ──── N  Identidade                única por (empresa, canal, valor)
Pessoa   1 ──── N  Mensagem                  a Conversa é a sequência (C-2.1)
Mensagem N ──── 1  Canal                     canal é da mensagem (C-2.3)

Funcionário  → lê →      domínios declarados        (M-3.5)
Funcionário  → escreve → Fato, e só Fato            (M-3.6, F-4.2)
Funcionário  → reage a → tipo de Fato               (M-3.7)
Funcionário  ✗ conhece ✗ Funcionário                (P1)

Fato        → aponta → Mensagem que o originou      (C-2.6)
Decisão     → é um →   Fato com motivo
Observação  → é um →   Fato sobre uma Pessoa
Aprendizado → deriva → N Observações + contagem + período   (P3)
```

**Decisão é um Fato especial**, e a especialidade é o que foi descartado. *"Não
escalei porque o acumulado já sustentava a classificação"* vale mais que
*"não escalei"* — só a primeira permite discordar depois.

---

## 6. Constituição — forma normativa

Oito princípios. Cada um com teste executável. Princípio sem teste é frase de
parede, e este projeto já estabeleceu que portão que nunca fica vermelho não é
portão.

---

### P1 — Nenhum Funcionário conhece outro Funcionário

**Definição.** Funcionários não se importam, não se nomeiam e não se chamam.
Coordenam-se exclusivamente por Fatos.

**Justificativa.** N Funcionários que se chamam direto são até N×(N−1) ligações
para manter. Por Fatos são N. Com 9 Funcionários no roteiro, a diferença é 72
relações contra 9.

**Correto**
```python
return [Fato("pessoa_qualificada", pessoa=p, motivo="tem verba e decide")]
```

**Incorreto**
```python
from funcionarios.comercial import FuncionarioComercial
FuncionarioComercial().assumir(pessoa)
```

**Teste.** Para cada módulo em `funcionarios/X/`, a AST não contém `import` de
`funcionarios.Y` com `Y != X`. Nem o nome de outro Funcionário em literal string.

---

### P2 — Nenhum Funcionário sabe por qual canal a pessoa chegou

**Definição.** Canais traduzem mundo → Fato e Fato → mundo. O Funcionário vê
sempre a mesma forma: quem, o quê, quando.

**Justificativa.** É a diferença entre "o mesmo Funcionário atende por e-mail
amanhã" e "reescrever nove Funcionários".

**Correto**
```python
def agir(self, gatilho: Fato, empresa: Empresa, memoria: Leitura) -> list[Fato]:
```

**Incorreto**
```python
if mensagem.remote_jid.endswith("@s.whatsapp.net"): ...
```

**Teste.** `grep -riE "whatsapp|evolution|remotejid|instagram|telegram|apikey" funcionarios/`
não retorna nada.

---

### P3 — Conhecimento sem evidência não entra na memória

**Definição.** Todo Aprendizado carrega afirmação, contagem, período e caminho
de volta às Observações.

**Justificativa.** Um aprendizado falso contamina Conteúdo, Comercial e
Atendimento ao mesmo tempo — a empresa inteira passa a errar junto e com
convicção. Evidência navegável é o que permite derrubá-lo.

**Correto**
```python
Aprendizado("objeção: medo de erro", observacoes=[...41 ids...],
            periodo=("2026-05-01", "2026-07-30"))
```

**Incorreto**
```python
Aprendizado("os clientes têm medo de IA")
```

**Teste.** Nenhum Aprendizado persistido com `observacoes` vazia, ou sem
período, ou com contagem divergente do número de referências.

---

### P4 — Toda regra que muda por cliente vem de configuração

**Definição.** Régua, pesos, tom, objetivos, limites e autonomia são da Empresa
Digital, nunca do código.

**Justificativa.** Uma clínica e uma construtora não qualificam igual. Regra no
código significa deploy para cada cliente novo.

**Correto**
```python
def agir(self, ..., empresa: Empresa): regua = empresa.config.regua
```

**Incorreto** — e é o código de hoje, [`agent.py:20`](agents/lead_triage/agent.py#L20)
```python
REGUA_PADRAO = {"quente": 70, "morno": 40}
```

**Teste (a).** Nenhum `dict` ou número declarado no escopo de módulo dentro de
`funcionarios/` cujo nome contenha `regua|peso|limiar|corte|score`.

**Teste (b) — autonomia (F-4.3).** Para todo par (nível declarado, teto da
empresa), o nível efetivo é o menor dos dois. Em particular: Funcionário que
declara `propõe` com empresa pedindo `age` resulta em `propõe`.

**Teste (c) — autonomia (F-4.4).** Configuração que pede nível acima do
declarado é **rejeitada na carga**, com mensagem nomeando o Funcionário e os
dois níveis.

---

### P5 — O Funcionário falha sozinho

**Definição.** Ferramenta quebrada vira Fato de falha, não exceção que sobe. Um
Funcionário fora do ar não derruba a empresa.

**Justificativa.** Já implementado e provado em
[`core/base_enricher.py:56`](core/base_enricher.py#L56): LLM fora do ar não
derruba o atendimento. É a única promessa de resiliência que este projeto já
cumpre — preservar é mais barato que reconstruir.

**Correto**
```python
except Exception as erro:
    return [Fato("ferramenta_falhou", ferramenta=f.nome, detalhe=f"{type(erro).__name__}: {erro}")]
```

**Incorreto** — deixar a exceção atravessar a fronteira do Funcionário.

**Teste.** Com toda ferramenta programada para lançar exceção, `agir()` retorna
Fatos de falha e não levanta. Um teste por Funcionário.

---

### P6 — Nada some em silêncio, e o que tem que sumir some de verdade

**Definição.** Toda decisão fica registrada com motivo. Toda Pessoa tem caminho
de remoção que funciona.

**Justificativa.** Hoje o `descadastro` trava em `true` e **nunca volta**
([`acumulo.py:49`](agents/lead_triage/acumulo.py#L49)): quem pediu para sair
fica congelado em 0/frio para sempre e dispara escalada errada a cada mensagem.
Não é bug de lógica — é uma pessoa que pediu para sair e continua na base.

**Correto** — remoção executada, com registro de que foi executada.

**Incorreto** — bandeira booleana que congela o estado e chama isso de saída.

**Teste (a).** Todo Fato persistido tem `motivo` não vazio.

**Teste (b).** Depois da remoção de uma Pessoa: nenhuma consulta em nenhum
domínio a devolve, nenhuma Identidade dela sobrevive, e nenhum texto de Mensagem
dela sobrevive (M-3.8).

**Teste (c).** Depois da remoção, os Aprendizados que dependiam dela continuam
existindo, com a contagem corrigida **e** o registro de quantas observações
saíram (M-3.10). Uma contagem que não mudou é regressão; uma que mudou sem
registro também.

**Teste (d).** Existe registro de que a remoção ocorreu, e ele não contém a
identidade removida (M-3.12).

---

### P7 — A instrução de um Funcionário é artefato de produção

**Definição.** O texto que define como um Funcionário pensa tem versão, suíte de
avaliação e portão de regressão por campo.

**Justificativa.** Já existe para um Funcionário (`evals/`), e foi essa suíte que
revelou 19 pontos de regressão escondidos dentro de uma taxa global. Taxa média
mente por agregação.

**Teste.** Todo Funcionário registrado tem suíte de avaliação. Alteração de
instrução sem execução da suíte correspondente falha no CI.

---

### P8 — Persistência é consequência

**Definição.** Modela-se comportamento; descobre-se a memória necessária; só
então escolhe-se armazenamento.

**Justificativa.** Este projeto já produziu uma migração `0001` criando uma
tabela `lead` — modelo de registro para um domínio que a Constituição define
como relação viva. Ela **não foi commitada**, e é por isso que ainda dá para
corrigir de graça.

**Teste.** Nenhum domínio novo entra em migração sem um Funcionário registrado
que o declare em `domínios`.

---

## 7. Critérios de aceite

Verificáveis. Sem opinião. A Fase A começa quando **todos** estiverem
satisfeitos.

### Decisões

| # | Critério | Estado |
|---|---|---|
| A1 | DE-1 respondida por escrito (§8) | ✅ **2026-08-01** |
| A2 | DE-2 respondida por escrito (§8) | ✅ **2026-08-01** |
| A3 | Parâmetros de §9 preenchidos com valor | ✅ **2026-08-01** — 6 de 6 |
| A4 | Este documento (v1.1) aprovado sem ressalva | ✅ **2026-08-01** |

### Arquitetura

| # | Critério | Como verificar |
|---|---|---|
| A5 | Todo domínio da Fase A tem Funcionário que o declara | Pessoa e Conversa aparecem em `domínios` do SDR ✅ |
| A6 | Os 8 princípios têm teste escrito e executável | 8 princípios, 13 testes especificados ✅ |
| A7 | As violações atuais estão registradas e nomeadas | P4 e P6 marcadas como violação conhecida, com fase de correção ✅ |
| A8 | Nenhum princípio sem teste | 8 de 8 cobertos ✅ |

### Terreno

| # | Critério | Como verificar | Estado |
|---|---|---|---|
| A9 | Suíte verde antes de começar | `pytest` → 163 passed | ✅ |
| A10 | `ruff` e `mypy` limpos | ambos sem erro | ✅ |
| A11 | Fase 1 resolvida: commitada ou revertida, **sem a migração `0001` atual** | `git status` limpo | ❌ |
| A12 | Ramo publicado — o remoto está 4 commits atrás | `git status` sem "à frente de" | ❌ |

**A12 não é burocracia.** Enquanto o remoto estiver 4 commits atrás e a Fase 1
sem commit, qualquer revisão feita a partir do GitHub analisa um repositório que
não existe — sem config central, sem migrações, sem Postgres, com os testes da
Evolution ainda afirmando hipótese como fato.

### Explicitamente FORA dos critérios

| Não é critério | Por quê |
|---|---|
| Contrato da Evolution verificado | A Fase A roda pelo CLI. O canal não participa. Vira critério da Fase C |
| Camada HTTP | Fase C |
| Os outros 8 domínios | Nascem com o Funcionário que precisar |

---

## 8. Decisões estruturais — RESOLVIDAS

As duas foram respondidas pelo Marcos em 2026-08-01. Nenhuma decisão estrutural
permanece aberta.

---

### DE-1 · O que "sair da base" apaga — **RESOLVIDA**

> **Decisão do Marcos, textual:** *"A identidade da Pessoa pode ser removida. O
> conhecimento corporativo pode permanecer apenas se estiver efetivamente
> anonimizado e em conformidade com a política de retenção definida pela
> empresa."*

A palavra que decide é **"efetivamente"**. Ela põe o ônus na plataforma: não
basta chamar de anônimo, tem que ser.

**Normas derivadas:** M-3.8 a M-3.12 (§3) e C-2.7 (§2).

**A consequência estrutural que sai daqui** — e é a razão de eu ter derivado em
vez de só registrar a decisão:

Texto livre não é anonimizável depois do fato. *"Oi, aqui é o Marcos da Forja
Criativa, em Botafogo"* continua identificando após qualquer varredura, porque
nome, empresa e bairro estão no meio da frase e nenhum deles está num campo.

Portanto **a anonimização acontece na extração, não na remoção**. O que
sobrevive a um pedido de saída é apenas o que já nasceu sem dado identificável.
Isso muda duas coisas concretas:

| | |
|---|---|
| **No schema** | O texto da Mensagem é apagável em cascata a partir da Pessoa. Não existe campo "texto anonimizado" — ele não seria confiável |
| **Na instrução do Funcionário** | O `resumo` extraído passa a ter regra explícita: **descreve a dor, nunca a pessoa**. Isso vira caso na suíte de avaliação (P7), e entra no escopo da Fase A |

O segundo item é trabalho novo que esta decisão criou. Está registrado aqui para
não aparecer como surpresa no meio da Fase A.

**A colisão que originou o bloqueio está resolvida assim:** M-3.1 (evidência
nunca se perde) cede para o direito de remoção, e M-3.10 garante que a cessão
seja visível — o Aprendizado sobrevive com a contagem corrigida e o registro de
quantas observações saíram. A evidência degrada com registro, em vez de sumir
em silêncio.

---

### DE-2 · Autonomia — **RESOLVIDA**

> **Decisão do Marcos, textual:** *"A autonomia pertence ao Funcionário. A
> Empresa apenas restringe o nível máximo permitido. Nenhuma configuração pode
> conceder capacidades que o Funcionário não possui por projeto."*

**Normas derivadas:** F-4.3 e F-4.4 (§4).

A decisão é mais forte que a minha recomendação, e melhor: eu propus teto no
Funcionário com ajuste na Empresa; ele fechou que a configuração **só desce,
nunca sobe**, e que capacidade inexistente não se concede por configuração.

O invariante fica em uma linha, e é testável:

```
nivel_efetivo = min(declarado_pelo_funcionário, teto_da_empresa)
```

**Consequência estrutural:** o modelo de Empresa carrega teto por Funcionário
desde a Fase A. É um campo, não uma tabela — barato agora, e evita que a
capacidade de restringir chegue depois de um cliente já ter um Funcionário
publicando sozinho.

E resolve, sem `if` espalhado, o problema que F-4.2 já preparava: um Funcionário
em `propõe` e um em `age` produzem **os mesmos Fatos**. Muda só quem reage a
eles. Nenhum Funcionário precisa saber em que nível está operando.

---

## 9. Parâmetros que precisam de valor (não bloqueiam a arquitetura)

Definem operação, não estrutura. **Valores fixados em 2026-08-01** pelo despacho
*"segue a lógica"* — ou seja, o Marcos delegou os padrões que eu havia defendido
em vez de arbitrar um a um. **Qualquer um pode ser trocado por ele a qualquer
momento; nenhum exige mudança de arquitetura para mudar de valor.**

| # | Parâmetro | **Valor** | Por que este |
|---|---|---|---|
| PA-1 ⚠ | Retenção de conversa | **24 meses** | Cobre o ciclo comercial inteiro com folga e não vira arquivo morto. É por Empresa Digital: o cliente sobe ou desce |
| PA-2 | Observações mínimas para virar Aprendizado | **10** | Abaixo disso o "padrão" é ruído com nome bonito. Acima, a empresa demora demais para aprender |
| PA-3 | Aprendizado novo nasce | **proposto** | Um falso contamina Conteúdo, Comercial e Atendimento de uma vez. Nasce esperando alguém olhar |
| PA-4 | Validade sem confirmação | **12 meses** | "Medo de IA" em 2026 não é o mesmo em 2029. Vencido não some: volta para proposto |
| PA-5 | Autonomia inicial do SDR | **propõe** | Ele fala com gente que ainda não é cliente. Errar aqui é caro e público |
| PA-6 | Segundo Funcionário | **Atendimento** | Ele é o primeiro que depende inteiramente do trabalho de outro. Se retomar uma conversa do SDR sem conhecer o SDR, a arquitetura está provada — e se não, é melhor descobrir no segundo Funcionário que no décimo |

> **PA-6 é o mais provável de você querer trocar.** Você descreveu muito mais o
> Funcionário de Conteúdo, e ele entrega valor visível. Mantive Atendimento
> porque a lógica que você mandou seguir era essa: o segundo Funcionário existe
> para testar a arquitetura, não para impressionar. Uma palavra sua inverte.

⚠ **PA-1 subiu de categoria com a DE-1.** A decisão diz que conhecimento só
permanece *"em conformidade com a política de retenção definida pela empresa"* —
ou seja, sem um valor de retenção, a permanência não tem base. Continua não
bloqueando a **arquitetura** (o mecanismo é obrigatório desde C-2.5,
independentemente do número), mas passa a bloquear a **primeira Empresa Digital
real**. Precisa de valor antes do primeiro cliente, não antes da Fase A.

---

## 10. O que este documento fechou

| Antes | Agora |
|---|---|
| "Lead" indefinido | **Pessoa**, com id interno e Identidades por canal (§1) |
| Identidade vinda do `remoteJid` | Norma P-1.1: id nunca deriva de canal. Não verificada nunca unifica (P-1.4) |
| "Conversa" sem forma | Mensagem imutável, canal como atributo, sem sessão inventada (§2) |
| "Memória compartilhada" vago | Três camadas com norma de perda para cada (§3) |
| Contrato de Funcionário informal | Recebe 4, devolve Fatos, 6 proibições, imports vetados (§4) |
| Princípios sem teste | 8 princípios, 13 testes especificados (§6) |
| "Quando começar?" | 12 critérios verificáveis (§7) |
| Remoção colidindo com evidência | DE-1: identidade sai, conhecimento não-identificável fica, o buraco é registrado (M-3.8 a M-3.12) |
| Autonomia sem dono | DE-2: do Funcionário; a Empresa só desce (F-4.3, F-4.4) |

**Nenhuma decisão estrutural pendente.**

### O que ainda separa este documento do primeiro commit da Fase A

**Dois** critérios de §7, e nenhum deles é decisão — os dois são ação:

| | O que falta | Natureza |
|---|---|---|
| A11 | Fase 1 resolvida — commitada ou revertida, **sem a migração `0001` atual** | alterar arquivos e commitar |
| A12 | Ramo publicado (remoto está 4 commits atrás) | `git push` |

Os dois estão parados por uma razão só: a última ordem explícita foi *"ainda não
altere nenhum código"*, e três palavras de despacho não revogam isso — sobretudo
o A12, que publica trabalho para fora e é onde outro arquiteto vai ler.

**Caminho recomendado para o A11**, e ele não antecipa nada da Fase A: commitar a
Fase 1 **sem** `migrations/versions/0001_criar_tabela_lead.py`. A maquinaria de
migração fica versionada e funcionando; o schema nasce na Fase A, com os nomes
certos, como migração `0001` de verdade. Nada é revertido, nada é jogado fora, e
a tabela `lead` nunca chega a existir.

### Trabalho que a DE-1 acrescentou à Fase A

A instrução do SDR passa a precisar da regra *"o resumo descreve a dor, nunca a
pessoa"* (M-3.9), com casos na suíte de avaliação. Não estava no escopo original
da Fase A e está registrado aqui para não virar surpresa no meio dela.

---

## 11. Decisões tomadas durante a Fase A

Registradas aqui porque decisão que existe só numa conversa não é ativo da
empresa — é lembrança de alguém.

---

### DE-3 · Remoção da `MemoriaPostgres` — **RESOLVIDA (2026-08-02)**

**O conflito.** A `MemoriaPostgres`, versionada na Fase 1, implementava o
contrato `MemoriaLead`: `(tenant_id, lead_id) → blob`, sobre uma tabela `lead`.
A migração `0001` da Fase A não cria `lead` — modelar a pessoa como registro é
o que §1 proíbe. Resultado medido: 6 erros,
`psycopg.errors.UndefinedTable: relation "lead" does not exist`.

**Decisão do Marcos:** remover a `MemoriaPostgres`.

**Razões, na ordem em que pesam:**

1. Ela implementa o modelo de registro que a constituição rejeita.
2. **Zero consumidores de produção** — só o preparo dos testes a construía.
3. O estado acumulado do SDR é **Camada 3** por §3: derivado e recalculável a
   partir das Mensagens. Não merece persistência corporativa.
4. Manter classe sem tabela, sem uso e sem teste seria infraestrutura órfã —
   e o projeto já classificou isso como dívida ao encontrá-la em outros lugares.

**O que NÃO foi feito, e é parte da decisão:** não se recriou `lead`, não se
criou tabela substituta para o blob, e o estado do SDR não foi migrado para a
memória corporativa. `MemoriaLead`, `MemoriaEmMemoria` e `MemoriaSQLite`
continuam intactos servindo o fluxo legado.

**Alternativas descartadas:** manter a classe órfã (dívida por definição);
migrar o blob para um domínio novo (fora de escopo, e §3 diz que estado
derivado não vira domínio); criar tabela para o blob (proibido).

---

### DE-4 · Menção a canal dentro da instrução do SDR — **RESOLVIDA (2026-08-02)**

**O caso.** `agents/lead_triage/signals.py` contém, dentro do texto da
instrução: *"(WhatsApp e Instagram são onde a dor aparece, não qual ela é)."*
Isso casa com o teste literal do P2 e **não** viola o P2 em substância — a
frase ensina o modelo a NÃO usar o canal como significado do problema.

**Decisão do Marcos:** não é violação nesta rodada. A frase permanece.

**Como o portão fica, e por que não foi afrouxado:** a ocorrência está
declarada como `EXCECAO_CONHECIDA` em `tests/test_arquitetura.py`, com arquivo
e linha exatos. Consequências:

- a ocorrência conhecida passa;
- **qualquer ocorrência nova falha** — a exceção não generaliza;
- se a frase sumir da instrução, um teste próprio acusa que a exceção ficou
  obsoleta e precisa ser removida. Portão que carrega exceção morta ensina a
  ignorar exceções.

---

### Dívida registrada · Forja Engineering Guardian

Existe uma GitHub App chamada **forja Engineering Guardian**, instalada com
escopo restrito a um único repositório (`socramsea/business-process-agents`),
com chave privada guardada **fora** deste repositório. Autenticação, JWT,
Installation ID e Installation Token foram provados funcionando.

**As permissões atuais são deliberadamente mais amplas do que o desenho final
precisa. Isto é dívida de segurança conhecida.**

Nada foi construído para o Guardian na Fase A: sem integração, sem webhook,
sem workflow, sem credencial no repositório. A redução de privilégios acontece
em fase própria, **antes** de qualquer operação automática.

Identificadores numéricos da App e da instalação não estão registrados aqui de
propósito — eles não são segredo, mas também não são necessários para o
registro arquitetural, e repositório não é lugar de guardar o que não precisa
estar nele.

---

*Documento normativo. Onde o código divergir dele, um dos dois está errado — e
resolver qual, explicitamente, faz parte do trabalho.*
