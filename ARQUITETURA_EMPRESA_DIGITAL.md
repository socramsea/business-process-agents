# Arquitetura da Empresa Digital

**Constituição da plataforma Forja Criativa.**
Toda implementação futura segue este documento. Quando o código e este documento
divergirem, um dos dois está errado — e a divergência tem que ser resolvida
explicitamente, nunca ignorada.

| | |
|---|---|
| Versão | 1.0 |
| Data | 2026-08-01 |
| Estado | **Proposta — aguarda aprovação do Marcos** |
| Código no momento da escrita | `2c68cf8`, 163 testes verdes, Fase 1 sem commit |

---

## Como ler este documento

As seções 1 a 4 dizem **o que é o produto**. As 5 a 11 dizem **como ele
funciona**. As 12 a 15 dizem **o que fazer com o que já existe**.

Cada princípio da seção 2 vem com um **teste de violação**: como saber, olhando
o código, que ele foi quebrado. Princípio sem teste de violação é frase de
parede.

---

## 1. Visão do produto

A Forja Criativa vende **Funcionários de IA**, não software.

O cliente não compra um CRM, uma automação ou um painel. Ele **monta uma
equipe**: instala um SDR, depois um Atendimento, depois um Conteúdo. Cada um
tem função, memória, ferramentas e métricas. Todos trabalham para a mesma
empresa e sabem o que os outros sabem.

O teste do produto é uma pergunta que o cliente responde sozinho:

> *"Eu estou administrando um software, ou eu tenho uma equipe trabalhando?"*

Se a resposta for "um software", o produto falhou — independentemente de a
tecnologia estar impecável.

### O que isso exclui

Não construímos: chatbot, CRM, help desk, painel de WhatsApp, automação de
mensagens, ferramenta de marketing. Esses recursos podem existir **dentro** da
plataforma como ferramenta de algum Funcionário. Nenhum deles é o produto, e
nenhum deles pode definir a arquitetura.

---

## 2. Princípios arquiteturais

Oito princípios. Cada um com o teste que prova a violação.

### P1 — Nenhum Funcionário conhece outro Funcionário

Funcionários não se chamam. Eles agem sobre a memória da empresa e registram
**Fatos**. Outro Funcionário reage ao Fato.

O motivo é aritmético: dez Funcionários que se chamam direto são até noventa
ligações para manter. Dez Funcionários que reagem a Fatos são dez.

> **Violação:** existe um `import` de um Funcionário dentro de outro, ou o nome
> de um Funcionário aparece escrito no código de outro.

### P2 — Nenhum Funcionário sabe por qual canal a pessoa chegou

WhatsApp, Instagram, e-mail, voz e site são **portas**. O que chega ao
Funcionário é sempre a mesma coisa: quem falou, o que disse, quando.

> **Violação:** a palavra `whatsapp`, `evolution`, `instagram` ou `remoteJid`
> aparece em qualquer arquivo dentro de `funcionarios/`.

### P3 — Conhecimento sem evidência não entra na memória

"Os clientes têm medo de IA" não é conhecimento. **"41 pessoas em 90 dias
levantaram medo de erro da IA, aqui estão as conversas"** é conhecimento.
Todo aprendizado carrega: a afirmação, quantas observações a sustentam, o
período, e o caminho de volta até as conversas de origem.

Aprendizado sem evidência é boato, e boato em escala é como uma equipe inteira
passa a repetir uma coisa errada com convicção.

> **Violação:** existe um registro de aprendizado sem contagem, sem período ou
> sem referência às observações que o originaram.

### P4 — Toda regra que muda por cliente vem de configuração

Uma clínica e uma construtora não qualificam lead pelo mesmo critério. Régua,
pesos, tom, objetivos e limites são **do cliente**, nunca do código.

> **Violação:** um `dict` de pesos, nota de corte ou limiar declarado como
> constante de módulo. Hoje isto está violado em
> [`agents/lead_triage/agent.py:20-34`](agents/lead_triage/agent.py#L20-L34).

### P5 — O Funcionário falha sozinho

Um Funcionário fora do ar não derruba a empresa. Uma ferramenta quebrada não
derruba o Funcionário. A falha vira Fato registrado, com motivo, e a operação
continua.

> **Violação:** uma exceção de ferramenta atravessa a fronteira do Funcionário
> sem virar Fato. Este princípio **já está implementado** em
> [`core/base_enricher.py:56-71`](core/base_enricher.py#L56-L71) e deve ser
> preservado na migração.

### P6 — Nada some em silêncio, e o que tem que sumir some de verdade

Toda decisão de Funcionário fica registrada com o motivo. E quando uma pessoa
pede para sair, a memória dela é **efetivamente removida** — não marcada com
uma bandeira que a congela para sempre.

> **Violação (a):** uma decisão sem registro do porquê.
> **Violação (b):** existe estado de pessoa que não tem caminho de remoção.
> Hoje isto está violado: `descadastro` trava em `true` e nunca volta
> ([`acumulo.py:49`](agents/lead_triage/acumulo.py#L49)), e não existe remoção.

### P7 — A instrução de um Funcionário é artefato de produção

O texto que define como um Funcionário pensa é código: tem versão, tem teste de
regressão e não muda sem passar pelo portão. Já fazemos isso para um Funcionário
(`evals/`, com taxa por campo e por fronteira). Vale para todos.

> **Violação:** uma instrução mudou sem rodar a suíte de avaliação daquele
> Funcionário.

### P8 — Persistência é consequência

Modela-se o comportamento do Funcionário. Descobre-se o que ele precisa
lembrar. **Só então** se escolhe tabela, coluna e banco. Nunca o contrário.

> **Violação:** uma discussão de arquitetura que começa por schema, ou uma
> tabela criada antes de existir um Funcionário que precise dela.

---

## 3. O conceito de Empresa Digital

Uma **Empresa Digital** é a instância que um cliente contrata. Ela contém tudo
que uma empresa de verdade contém, e os Funcionários trabalham dentro dela.

```
                        EMPRESA DIGITAL
                     (o cliente da Forja)
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   FUNCIONÁRIOS          MEMÓRIA DA            FERRAMENTAS
                          EMPRESA
   SDR                    Pessoas              enviar mensagem
   Atendimento            Conversas            ler um site
   Comercial              Conhecimento         publicar conteúdo
   Conteúdo               Conteúdos            emitir proposta
   Financeiro             Propostas            consultar agenda
   ...                    Tarefas              ...
                          Indicadores
                          ...

        └──────────── FATOS ────────────┘
          o que aconteceu, quem soube,
             o que foi decidido
```

Três coisas e só três:

- **Funcionários** — quem trabalha.
- **Memória da Empresa** — o que a empresa sabe. Uma só, com domínios dentro.
  Não existe memória privada de Funcionário: o que o SDR aprende, o Conteúdo lê.
- **Ferramentas** — o que os Funcionários usam para agir no mundo.

E o que liga tudo: os **Fatos**. Um Fato é algo que aconteceu ou passou a ser
sabido. Fatos são o único jeito de um Funcionário afetar outro.

### Fronteiras rígidas

| | |
|---|---|
| Empresa Digital | Isolamento total. Conhecimento de uma nunca vaza para outra. É a fronteira de segurança mais importante da plataforma |
| Funcionário | Não conhece outro Funcionário (P1) |
| Canal | Fica fora. Traduz mundo → Fato e Entrega → mundo (P2) |

---

## 4. Os domínios da memória

A memória da empresa tem domínios. Cada um existe porque **algum Funcionário
precisa dele** — nunca porque o organograma ficaria bonito.

| Domínio | O que guarda | Quem escreve | Quem lê | Existe hoje |
|---|---|---|---|---|
| **Pessoas** | quem é, o que quer, dores, decisões, estado da relação | SDR, Atendimento, Comercial | todos | parcial (um blob) |
| **Conversas** | o que foi dito, por qual porta, quando | quem conversa | todos | **não** |
| **Conhecimento** | o que a empresa sabe de si: posicionamento, tom, produtos, objeções, FAQ | Conteúdo, Processos | todos | não |
| **Conteúdos** | o que foi publicado, onde, e como performou | Conteúdo | Conteúdo, Comercial | não |
| **Propostas** | o que foi oferecido, a quem, com que resultado | Comercial | Comercial, Financeiro | não |
| **Tarefas** | o que precisa ser feito, por quem, até quando | todos | todos | não |
| **Indicadores** | números da operação e de cada Funcionário | plataforma | todos | não |
| **Documentos** | contratos, briefings, material | Administrativo | conforme | não |
| **Campanhas** | esforço coordenado com objetivo e prazo | Marketing | Conteúdo, Comercial | não |
| **Produtos e Serviços** | o que a empresa vende | Administrativo | Comercial, Conteúdo | não |
| **Processos** | como esta empresa faz as coisas | Processos | todos | não |
| **Agenda** | compromissos e disponibilidade | Atendimento, Comercial | todos | não |
| **Funcionários** | quem está contratado, com que instrução e que métricas | plataforma | plataforma | não |

**Onze dos treze não existem, e não devem ser construídos agora.** Domínio
nasce quando um Funcionário precisa dele. Construir os treze com um Funcionário
e meio no ar é o exemplo mais puro de infraestrutura pela infraestrutura.

### Os dois primeiros

**Pessoas** e **Conversas** — porque são os dois que os Funcionários existentes
alimentam e que todos os futuros consomem.

Os domínios não têm o mesmo formato, e isso importa:

- **Pessoas** é um registro por pessoa, que se atualiza. Estado vivo.
- **Conversas** só cresce, em ordem de tempo, e nunca se reescreve.

Tratar os treze como "chave → blob" seria voltar ao modelo de registro com
nome novo.

---

## 5. Os Funcionários que existem hoje

Um, e ele não sabe que é um.

### Funcionário SDR

Hoje se chama `LeadTriageAgent`. Faz: recebe uma pessoa, entende o que ela
disse, qualifica, e indica qual colega assume.

**O que já funciona e deve ser preservado:**

| | |
|---|---|
| Isolamento de falha | LLM fora do ar não derruba o atendimento ([`base_enricher.py:56`](core/base_enricher.py#L56)) |
| Nota do relacionamento | Sinais somam entre mensagens; quem conversa mais é entendido melhor, não pior ([`acumulo.py`](agents/lead_triage/acumulo.py)) |
| Encaminhamento | Já indica o colega, e guarda **todos** os indicados, não só o último |
| Handoff para humano | Sabe dizer "isto não é comigo" ([`escalada.py`](agents/lead_triage/escalada.py)) |
| Instrução como artefato | Suíte de avaliação com portão de regressão por campo (`evals/`) |
| Registro de custo | Tokens e US$ por chamada ([`signals.py:349`](agents/lead_triage/signals.py#L349)) |

**O que falta para ele ser um Funcionário de verdade:**

- **Não guarda a conversa.** Guarda um placar de sinais e um contador. O que a
  pessoa escreveu é usado e descartado. Consequência direta: nenhum outro
  Funcionário consegue "continuar da última conversa", porque não existe última
  conversa. **Este é o buraco mais caro do sistema hoje.**
- Não tem objetivo nem métrica próprios.
- Não aprende: não há caminho para o que ele ouve virar conhecimento da empresa.
- A régua dele é a mesma para todo cliente (viola P4).

---

## 6. Os Funcionários futuros

Ordem sugerida, com o motivo. Não é cronograma — é dependência.

| # | Funcionário | Por que nesta posição |
|---|---|---|
| 1 | **SDR** | Já existe pela metade. É a porta de entrada: sem ele, nenhum outro tem sobre quem trabalhar |
| 2 | **Atendimento** | Prova a colaboração de verdade: só funciona se conseguir continuar de onde o SDR parou. Se este funcionar, o modelo está certo |
| 3 | **Conteúdo (Síntese)** | O pilar que o Marcos mais descreveu. Prova a inteligência coletiva: consome objeção que o SDR ouviu |
| 4 | **Comercial** | Precisa de Propostas, que precisa de Produtos e Serviços |
| 5 | **Processos / Inteligência** | Quem transforma observação em aprendizado (seção 9). Vale a partir de volume, não antes |
| 6+ | Financeiro, RH, Operações, Marketing, Relatórios | Cada um traz domínio novo; nenhum muda a arquitetura |

**O Atendimento é o teste da arquitetura, não o Conteúdo.** Ele é o primeiro que
depende inteiramente do trabalho de outro. Se ele conseguir retomar uma conversa
que o SDR começou, sem conhecer o SDR, os princípios P1 e P2 valem. Se não
conseguir, a arquitetura está errada e é melhor descobrir no segundo Funcionário
que no décimo.

---

## 7. Como os Funcionários colaboram

**Por Fatos. Nunca por chamada direta.**

Um **Fato** é algo que aconteceu ou passou a ser sabido, com autor e momento:

```
Fato
├── o que aconteceu      "pessoa qualificada como quente"
├── sobre quem/o quê     a pessoa, o conteúdo, a proposta
├── quem registrou       Funcionário SDR
├── quando
├── por quê              o motivo da decisão (P6)
└── evidência            de onde veio (P3)
```

O SDR não chama o Comercial. Ele registra: *"esta pessoa está pronta para
proposta, porque tem verba e é quem decide."* O Comercial trabalha sobre os
Fatos que lhe interessam.

### O trajeto, inteiro

```
  porta (WhatsApp)          Fato: pessoa falou
        │                          │
        ▼                          ▼
   [ adaptador ] ──────────► MEMÓRIA DA EMPRESA ◄──── todos leem
   traduz para                Pessoas · Conversas
   linguagem da                       │
     empresa                          ▼
                             Fato: pessoa qualificada
                                     │
                          ┌──────────┴──────────┐
                          ▼                     ▼
                    Funcionário            Funcionário
                     Comercial              Conteúdo
                   (prepara proposta)    (vira pauta)
```

Nenhuma seta liga um Funcionário a outro. É essa ausência que permite o décimo
Funcionário entrar sem tocar nos nove.

### O que isso custa, honestamente

Fatos são mais indiretos que chamada direta. Depurar "por que o Comercial não
agiu" exige olhar o Fato, não uma pilha de chamadas. **Mitigação:** todo Fato é
registrado com motivo e evidência, e a linha do tempo da pessoa mostra a
sequência inteira. Fica mais fácil de auditar do que uma pilha de chamadas — e
auditar é o que o cliente vai querer fazer quando desconfiar da equipe.

---

## 8. Como compartilham conhecimento

Não compartilham: **é tudo da empresa desde o começo.**

Não existe "memória do SDR". Existe a memória da empresa, e o SDR escreve nela.
O Conteúdo lê a mesma memória. Nada é copiado, nada é sincronizado, nada é
pedido.

Duas camadas, e a diferença entre elas é o que separa a plataforma de um banco
de dados com IA em cima:

| | **Observação** | **Aprendizado** |
|---|---|---|
| O que é | o que uma pessoa disse | um padrão em muitas observações |
| Exemplo | *"tenho medo de a IA errar com meu cliente"* | *"41 pessoas em 90 dias levantaram medo de erro"* |
| Quem cria | quem conversou | o Funcionário de Inteligência (§9) |
| Escopo | uma pessoa | a empresa |
| Evidência | a conversa | as 41 conversas, o período, a contagem |

O exemplo do Marcos, completo:

1. SDR conversa. Registra observação em Conversas: *"medo de a IA errar."* 41 vezes, com pessoas diferentes.
2. Alguém percebe o padrão e registra em Conhecimento: *"objeção recorrente — medo de erro. 41 observações, 90 dias, conversas [...]"*
3. **Conteúdo** lê Conhecimento e cria pauta que responde à objeção.
4. **Comercial** lê Conhecimento e inclui garantia na proposta.
5. **Atendimento** lê Conhecimento e responde antes de perguntarem.

Nenhum dos quatro conhece os outros três.

---

## 9. Como aprendem

Transformar 41 observações em um aprendizado é **trabalho**, e trabalho na
Forja Criativa é feito por Funcionário. Não por rotina de fundo.

### O Funcionário de Inteligência

Função: ler as observações acumuladas, encontrar padrão, e registrar o
aprendizado **com a evidência junto** (P3).

Não é o primeiro a ser construído. Com 20 conversas, o padrão se vê a olho nu.
Ele passa a valer a pena com volume — e a decisão de quando é do cliente, não
nossa.

### Aprendizado é revisável

Um aprendizado é a melhor leitura **até agora**. Ele pode:

- **envelhecer** — "medo de IA" em 2026 não é o mesmo em 2029;
- **ser contestado** por observações novas;
- **ser corrigido pelo dono da empresa**, que sabe coisa que nenhuma conversa
  revelou.

Por isso todo aprendizado guarda período e contagem. Sem isso não há como saber
que ele venceu.

### Duas coisas que este Funcionário pode quebrar

**Ele pode inventar padrão.** Um modelo pedindo padrão encontra padrão até no
ruído. **Mitigação:** número mínimo de observações; a evidência sempre
navegável; e o dono da empresa podendo derrubar um aprendizado.

**Ele pode ensinar errado a empresa inteira.** Um aprendizado falso contamina
Conteúdo, Comercial e Atendimento ao mesmo tempo. **Mitigação:** aprendizado
novo nasce **proposto**, não ativo. Alguém aprova. Quanto disso é automático é
decisão do Marcos (§15).

---

## 10. Como evoluem

Um Funcionário evolui em quatro eixos. Os quatro precisam de portão.

| Eixo | O que muda | Portão |
|---|---|---|
| **Instrução** | como ele pensa | Suíte de avaliação daquele Funcionário, com taxa por campo. **Já existe** para o SDR e é o modelo para os outros |
| **Ferramentas** | o que ele consegue fazer | Cada ferramenta falha isolada (P5) |
| **Conhecimento** | o que a empresa sabe | Aprendizado com evidência (P3) |
| **Configuração** | régua e objetivo daquele cliente | Do cliente, nunca do código (P4) |

O eixo de instrução é o mais delicado e o único que já sabemos operar: a suíte
atual mostra **taxa por campo e por fronteira**, porque uma taxa global esconde
regressão — foi assim que descobrimos 19 pontos escondidos numa média.

### Métricas por Funcionário

Cada Funcionário responde por números próprios: quantas pessoas atendeu, quanto
custou, quantas vezes precisou de humano, qual a taxa de acerto no que dá para
medir. **O cliente contratou um profissional; ele tem direito à avaliação de
desempenho.**

Hoje medimos custo em um caminho só e não medimos desempenho por Funcionário.

---

## 11. Como adicionar um Funcionário sem mudar a arquitetura

A promessa é fácil de escrever e difícil de manter. Então ela vem com uma
definição verificável.

### O que um Funcionário declara

```
Funcionário
├── função           "atender clientes existentes"
├── objetivo         o que é sucesso para ele
├── fatos que lê     a que ele reage
├── fatos que escreve o que ele registra
├── domínios         o que da memória ele consulta
├── ferramentas      o que sabe usar
├── instrução        versionada, com suíte própria
└── métricas         como é avaliado
```

### O teste da promessa

Adicionar um Funcionário **não pode** exigir mudança em:

- ✗ nenhum outro Funcionário
- ✗ a memória da empresa (salvo domínio novo, que é aditivo)
- ✗ os adaptadores de canal
- ✗ o mecanismo de Fatos
- ✗ o painel

Se qualquer um desses precisar mudar, **a arquitetura falhou e o documento é que
está errado** — não o Funcionário.

Esse teste é executável: no dia em que o Atendimento nascer, o diff mostra quais
arquivos foram tocados. Se aparecer arquivo fora de `funcionarios/atendimento/`
e do registro, a promessa quebrou naquele dia, e a gente conserta ali em vez de
descobrir no décimo.

---

## 12. O que precisa mudar na arquitetura atual

Onze itens, com o princípio que cada um viola. **Nada disso foi alterado.**

| # | O que está errado | Onde | Viola | Gravidade |
|---|---|---|---|---|
| 1 | **A conversa não é guardada.** Só um placar de sinais e um contador | [`acumulo.py:70`](agents/lead_triage/acumulo.py#L70) | §8 | **Crítica** — sem isso a inteligência coletiva não existe |
| 2 | **`descadastro` trava para sempre** e não há remoção de dados | [`acumulo.py:49`](agents/lead_triage/acumulo.py#L49) | P6 | **Crítica** — vira risco jurídico no dia que a landing subir |
| 3 | **Régua e pesos fixos no código** | [`agent.py:20-34`](agents/lead_triage/agent.py#L20-L34) | P4 | Alta — o segundo cliente exige deploy |
| 4 | **Canal dentro do núcleo** (`core/evolution.py`) | [`core/evolution.py`](core/evolution.py) | P2 | Alta |
| 5 | **`MemoriaLead` / tabela `lead`** — memória pertencendo ao lead | [`core/memoria.py`](core/memoria.py) | §3 | Alta — congela ao commitar |
| 6 | **Provedor de LLM escrito no Funcionário** | [`agent.py:80`](agents/lead_triage/agent.py#L80) | P4 | Média |
| 7 | **`enrichers/` importa de `agents/lead_triage/`**, e um símbolo privado | [`mensagem_openai.py:18`](enrichers/mensagem_openai.py#L18) | — | Média |
| 8 | **Contrato de saída é `dict` cru** | [`base_agent.py:16`](core/base_agent.py#L16) | — | Média |
| 9 | **Sem métrica por Funcionário**; custo medido só no caminho Anthropic | [`signals.py:349`](agents/lead_triage/signals.py#L349) | §10 | Média |
| 10 | **`MAX_TOKENS` 8192 contra 1024** entre provedores ditos intercambiáveis | `signals.py` / `mensagem_openai.py` | P7 | Média — invalida comparação de provedor |
| 11 | **Nomenclatura técnica** (`BaseAgent`, `LeadTriageAgent`, `enrichers`) | vários | §1 | Baixa tecnicamente, **alta no produto** |

### Sobre a Fase 1, que está na árvore sem commit

| O que | Veredito |
|---|---|
| `core/config.py` | **Fica.** Configuração central serve a P4 |
| Alembic e migrações | **Fica.** Sem versionamento de schema não há evolução segura |
| `MemoriaPostgres`, pool, backup nos dois caminhos, CI com Postgres | **Fica.** É a máquina que preserva a memória |
| **A migração `0001` criando a tabela `lead`** | **Não fica.** É o item 5 desta tabela, e é o único que congela ao commitar |

Recomendação: **não commitar como está.** Reescrever `0001` antes.

---

## 13. Plano de migração

Cinco fases. Cada uma termina com testes verdes e valor entregue. Nenhuma
depende de aprovar as seguintes.

### Fase A — A memória vira da empresa · 2 a 3 dias

Reescreve `0001` para os domínios **Pessoas** e **Conversas**. `MemoriaLead`
sai. O SDR passa a **gravar o que ouviu**, não só o placar.

Resolve os itens 1 e 5. Sem isto, nenhum segundo Funcionário é possível.

*Risco:* mexe no coração do único Funcionário que funciona. Mitigado por 163
testes e pela lógica de acumulação não mudar — ela ganha destino.

### Fase B — O Funcionário vira Funcionário · 1 a 2 dias

`LeadTriageAgent` → `FuncionarioSDR`. `BaseAgent` → `Funcionario`. Régua e
pesos saem para a configuração da Empresa Digital. Provedor de LLM idem.

Resolve 3, 6, 11. **Aqui o segundo cliente passa a ser possível sem deploy.**

### Fase C — Fatos e canais · 3 a 4 dias

O mecanismo de Fatos. O canal sai do núcleo e vira adaptador. Contrato de saída
tipado.

Resolve 4, 7, 8. **Aqui a arquitetura passa a comportar o segundo Funcionário.**

### Fase D — O segundo Funcionário · 4 a 6 dias

**Atendimento.** Ele existe para provar a arquitetura: precisa continuar de onde
o SDR parou sem conhecer o SDR.

Se ele exigir mudança fora do próprio pacote, o teste da §11 falhou e a gente
corrige a arquitetura antes de seguir. Melhor descobrir aqui.

### Fase E — Conhecimento e aprendizado · 5 a 8 dias

Domínio Conhecimento. Aprendizado com evidência. O Conteúdo puxando objeção que
o SDR ouviu.

**Aqui a inteligência coletiva sai do papel.**

### O que fica de fora, e por quê

| | |
|---|---|
| Landing, painel, dashboard | Precisam de camada HTTP. Nada disso torna um Funcionário melhor hoje |
| Os outros 11 domínios | Nascem com o Funcionário que precisar deles |
| Funcionário de Inteligência | Precisa de volume que ainda não existe |

**Total A–E: 15 a 23 dias** até dois Funcionários colaborando sobre uma memória
compartilhada, com aprendizado coletivo funcionando.

---

## 14. Riscos

| Risco | Consequência | Mitigação |
|---|---|---|
| **LGPD.** Guardar conversa é dado pessoal em repouso; `lead_id` é telefone | Exposição jurídica real, e o produto vende para empresas que também respondem | Retenção definida (§15), remoção efetiva no descadastro, telefone fora do log |
| **Custo por Funcionário.** Hoje US$ 0,0209 por mensagem, entrada dominando 47:1. Cinco Funcionários é cinco vezes | Margem some sem ninguém ver | Métrica de custo por Funcionário e por Empresa Digital; teto por cliente |
| **Aprendizado falso.** Um padrão inventado contamina quatro Funcionários de uma vez | A equipe inteira erra junto e com convicção | Mínimo de observações, evidência navegável, aprovação humana |
| **Abstração cedo demais.** Fatos e domínios com um Funcionário no ar | Meses de arquitetura sem produto | O teste da §11 é executável, e a Fase D o executa |
| **A promessa da §11 é fácil de escrever** | Vira frase de parede | O diff do segundo Funcionário decide |
| **Um Funcionário mal calibrado fala com cliente do cliente** | Dano à marca de quem nos contratou | Handoff já existe. Nenhum Funcionário novo entra sem limite de autonomia definido |
| **A Fase A mexe no que funciona** | Regressão no único Funcionário que existe | 163 testes, e o portão de avaliação da instrução |

---

## 15. Decisões que precisam da sua aprovação

Sete. Nada anda sem elas, e nenhuma é técnica.

### D1 — Aprovar esta arquitetura

Sim, não, ou com correções. Nada da §13 começa antes.

### D2 — A migração `0001` sem commit

**Recomendo reescrever antes de commitar.** É a única coisa que fica cara se
esperar.

### D3 — Como chamar uma pessoa

`Lead` sai. Candidatos: **Pessoa** (recomendo — é o que ela é), Contato,
Relacionamento. Vai virar o nome mais repetido da plataforma pelos próximos dez
anos.

### D4 — Retenção de conversa

Guardar para sempre, ou por prazo? A pergunta não é técnica: é **por quanto
tempo a memória da sua empresa deve durar**, e o que sobra quando alguém pede
para sair. Sem resposta, a Fase A não sobe.

### D5 — Autonomia de cada Funcionário

Onde fica a linha entre agir sozinho e trazer para aprovação? Um profissional de
conteúdo não publica sem o dono da marca ver, mas também não pergunta a cada
frase.

Proponho três níveis por Funcionário — **observa** (só registra), **propõe**
(prepara e espera aprovação), **age** (executa e avisa) — configuráveis por
Empresa Digital. Preciso do seu aval no conceito, e do padrão de cada um.

### D6 — Aprovação de aprendizado

Um aprendizado novo entra ativo ou proposto? **Recomendo proposto** até o
Funcionário de Inteligência ter histórico que justifique confiança.

### D7 — Qual é o segundo Funcionário

Eu recomendo **Atendimento**, porque ele testa a arquitetura. Você descreveu
mais o **Conteúdo**, que entrega mais valor visível. Os dois são defensáveis e a
escolha é sua.

---

## Anexo — vocabulário

| Antes | Agora | Por quê |
|---|---|---|
| `BaseAgent` | `Funcionario` | Um agente é uma abstração técnica. Um funcionário é alguém que trabalha |
| `LeadTriageAgent` | `FuncionarioSDR` | Ele não faz triagem; ele recebe pessoas |
| `Lead` | **decisão D3** | Uma pessoa não é um registro |
| `MemoriaLead` | Memória da Empresa | A memória não é do lead. É da empresa |
| `enricher` | Ferramenta | É o que o Funcionário usa para saber mais |
| Resultado do agente | **Fato** | O que aconteceu, quem soube, por quê |
| tenant | Empresa Digital | O cliente não é um inquilino. É uma empresa |

---

*Este documento vale mais que o código. Quando divergirem, resolve-se
explicitamente — e a resposta pode muito bem ser corrigir o documento.*
