# Revisão dos 46 casos novos — campo `agente_indicado`

---

## O critério de arbitragem

**Classificar pelo agente que RESOLVE a dor, não pelo mecanismo que falha.**

O campo `agente_indicado` responde a uma pergunta só: *qual dos quatro agentes eu
implantaria neste cliente?* Não responde *onde o processo quebra*.

É por isso que `r6_amb_01` volta a ser `atendimento`: a consequência é venda perdida,
mas quem resolve o balcão sozinho sem responder o WhatsApp é o agente de atendimento.
E é por isso que `r6_amb_04` fica `marketing`: o gargalo é manual, mas quem assume a
montagem dos posts é o agente de marketing.

`indefinido` segue a mesma pergunta: se nenhum dos quatro seria implantado com o que
a mensagem traz, é `indefinido` — não o mais próximo.

Aplique este critério ao Bloco 3.

---

## Já arbitrados

| caso | decisão | nota |
|---|---|---|
| `r6_amb_01` | **atendimento** | revertido de `comercial` |
| `r6_amb_03` | **atendimento** | mantido |
| `r6_amb_04` | **marketing** | mantido |
| `r6_amb_05` | **indefinido** | mantido |
| `r6_ind_05` | **indefinido** | mantido; não descartado — ver nota |
| `ag_ind_05` | **indefinido** | reafirmado (caso do lote já aprovado) |

`r6_ind_05` não foi descartado: minha leitura é que ele e o `r6_ind_07` testam armadilhas
diferentes — um é checklist de requisitos que poderia virar `operacional`, o outro é sinal
comercial forte (verba, prazo, autoridade) que poderia vazar para `comercial`. Se discordar,
é um `descartar`.

---

## 🟠 Bloco 2 — contestados pela crítica (9) — PENDENTE

Duplicatas de casos que já existem, ou mecanismo de dor que não cabe nas quatro
categorias. Todos concordaram com o gabarito na medição — a decisão aqui é de custo,
não de rótulo.

### 1. `r6_amb_06` — gabarito proposto: **comercial**

> meu unico vendedor pediu as conta semana passada e levou tudo na cabeça dele. tem orçamento em aberto que eu nao sei de quem e nem se alguem respondeu o cliente. sinceramente nao sei se preciso contratar outro ou se e outra coisa

- 🔻 **Objeção da crítica:** mecanismo idêntico ao `r6_com_01` (vendedor sai, carteira fica órfã).
- **Justificativa do gerador:** A dor concreta e nao existir controle de quem esta no funil, com orcamento em aberto orfao e sem ninguem sabendo se o cliente foi respondido; a leitura indefinido (evento pontual de saida de funcionario, lead que admite nao saber o que quer) foi descartada porque, apesar da duvida dele, ha fato concreto de negociacao aberta sem dono declarado.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 2. `r6_atd_02` — gabarito proposto: **atendimento**

> queria contratar trafego pago pra encher a baixa temporada da pousada. so que fui olhar aqui e a maioria dos pedido de reserva cai entre 21h e meia noite, quando a recepção ja fechou, e a gente so vai responder as 10h do outro dia. ai a pessoa responde que ja acertou em outro lugar

- 🔻 **Objeção da crítica:** estrutura idêntica a `ag_arm_01`, que está gravado como `comercial`.
- **Justificativa do gerador:** A dor e a janela noturna sem ninguem para responder quem escreveu, e o produto pedido (trafego) vem sem nenhuma dor de marketing descrita.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 3. `r6_atd_07` — gabarito proposto: **atendimento**

> queria um sistema pra automatizar a planilha de controle de mensalidade da academia. mas te falar o que ta pegando fogo mesmo e o whats da recepção: aluno pergunta horario da aula de spinning, se tem vaga, como tranca o plano, sai umas 60 por dia e a menina responde quando da. tem mensagem de terça que ate hoje ninguem abriu

- 🔻 **Objeção da crítica:** repete `ag_atd_01` quase palavra por palavra; só troca clínica por academia.
- **Justificativa do gerador:** A dor descrita e o volume de duvidas de aluno sem resposta, enquanto a planilha aparece so como produto desejado, sem trabalho manual descrito.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 4. `r6_com_05` — gabarito proposto: **comercial**

> escola de ingles aqui. metade de quem pede informação fala assim: 'me chama em janeiro que ai eu fecho'. ai janeiro chega, a gente abre turma nova e ninguem lembra de chamar essa gente, a anotação fica num papel na mesa da coordenadora e some. ano passado devia ter uns 60 nome nessa situação e acho que a gente chamou uns 5

- 🔻 **Objeção da crítica:** terceira variação do mesmo mecanismo do lote — ver `r6_com_04` e `r6_com_08`.
- **Justificativa do gerador:** A dor e o lead que pediu retorno em data futura e nunca e recontatado, uma oportunidade combinada que se perde por falta de acompanhamento.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 5. `r6_com_06` — gabarito proposto: **comercial**

> trabalho com distribuição de bebida pra bar e restaurante. semana passada fui olhar o faturamento e descobri que 3 cliente que pediam toda quinta feira pararam de comprar faz uns 3 mes e ninguem aqui tinha reparado. quando liguei, um ja tava com outro fornecedor ha bastante tempo. nao existe nada que me avise quando um cliente para de pedir

- 🔻 **Objeção da crítica:** repete `ag_com_03`; e o lead nomeia a solução (“nada que me avise”), o que puxa leitura operacional.
- **Justificativa do gerador:** A dor e o cliente recorrente que para de comprar sem ninguem perceber nem reagir, oportunidade de receita existente perdida em silencio.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 6. `r6_com_07` — gabarito proposto: **comercial**

> queria um robo pra responder no whats mais rapido. mas sendo sincero a gente ja responde em uns 5 minuto, isso ai ta ok. o buraco é depois: e serralheria, pedido de portão e grade, quando o cliente pede desconto o vendedor tem que me mandar por email pra eu aprovar, eu levo uns 3 ou 4 dia pra olhar isso e quando eu volto o cara ja mandou fazer em outro lugar

- 🔻 **Objeção da crítica:** gargalo de alçada não é nenhum dos quatro mecanismos; sustenta comercial e operacional.
- **Justificativa do gerador:** O produto pedido aponta atendimento e o proprio lead descarta a demora na resposta, a dor real e a negociacao travada na aprovacao de desconto que perde a venda no fechamento.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 7. `r6_mkt_03` — gabarito proposto: **marketing**

> somos uma metalurgica pequena de peça sob medida, 22 ano de mercado. um comprador de industria grande me contou outro dia que procurou fornecedor na internet e nem achou a gente, achou 3 concorrente. o que a gente tem é o catalogo em pdf que o representante leva na pasta, fora isso a empresa nao existe em canal nenhum

- 🔻 **Objeção da crítica:** mesmo mecanismo de `r6_mkt_07`.
- **Justificativa do gerador:** A dor e nao existir onde o comprador procura, entao a empresa nem entra na lista de opcoes.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 8. `r6_mkt_05` — gabarito proposto: **marketing**

> queria botar um robo de atendimento no whats da clinica veterinaria. chega umas 15 mensagem por dia e mais de 10 é gente perguntando se faço banho e tosa ou se vendo raçao, e a gente é clinica cirurgica, nao faz nada disso. dono de bicho que precisa de cirurgia mesmo quase nao aparece, acho que ninguem por aqui entende o que a gente faz

- 🔻 **Objeção da crítica:** mecanismo idêntico ao `r6_amb_02`.
- **Justificativa do gerador:** A dor e a comunicacao nao dizer o que a clinica faz, atraindo publico errado e nao o certo; o robo e so o produto pedido.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 9. `r6_ope_07` — gabarito proposto: **operacional**

> queria contratar uma social media pras 4 unidade da academia, ta tudo meio parado. mas confesso que o que me tira o sono e outra coisa: toda segunda eu peco no zap pra cada gerente o numero de matricula, cancelamento e inadimplencia, dai eu junto tudo num excel na mao pra levar na reuniao. sempre tem um que manda no formato errado e eu refaco do zero

- 🔻 **Objeção da crítica:** repete `ag_ope_01` + `ag_ope_03`.
- **Justificativa do gerador:** O produto pedido aponta marketing, mas a dor que o lead diz ser a pior e consolidar relatorio manual toda semana, tarefa interna repetitiva.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

## 🟢 Bloco 3 — sem objeção (32) — PENDENTE

### Comercial (5)

### 10. `r6_com_01` — gabarito proposto: **comercial**

> boa tarde. tenho uma distribuidora de peça agricola no interior. meu vendedor mais antigo pediu as conta semana retrasada e foi embora com tudo na agenda do celular dele. tinha uns 15 cliente negociando com ele, ninguem assumiu esse povo e ta tudo parado desde entao. dois ja compraram de outra distribuidora, fiquei sabendo por terceiro

- **Justificativa do gerador:** A dor e a carteira de negociacoes abertas que ficou orfa na saida do vendedor e ninguem repassou, entao a oportunidade que existia morre parada.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 11. `r6_com_02` — gabarito proposto: **comercial**

> tenho uma loja de material de construção com 4 vendedor no balcão e cada um anota o orçamento no bloquinho dele. semana passada dois ligaram pro mesmo cliente oferecendo coisa diferente, o cara ficou puto. e teve um pedido de orçamento de porcelanato que simplesmente nao era de ninguem, ficou 10 dia sem sair porque cada um achou que era do outro

- **Justificativa do gerador:** A dor e a ausencia de dono e de registro comum do funil, que gera contato duplicado de um lado e oportunidade sem responsavel do outro.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 12. `r6_com_03` — gabarito proposto: **comercial**

> queria contratar trafego pago pra trazer paciente novo pra clinica odontologica. mas assim, pensando aqui, tenho quase 2 mil paciente cadastrado no sistema, gente que fez tratamento em 2023, aprovou so a limpeza e o resto do plano ficou pela metade. nunca ninguem ligou pra nenhum desses pra oferecer o restante. e dinheiro parado ali dentro

- **Justificativa do gerador:** O produto pedido e midia paga, mas a dor descrita e a base de tratamentos aprovados pela metade que nunca foi retomada, ou seja, venda existente nao trabalhada.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 13. `r6_com_04` — gabarito proposto: **comercial**

> sou dono de uma corretora de seguro. a apolice vence e a gente so descobre quando o cliente liga falando que ja renovou com outro corretor. nao tem nada avisando que ta chegando o vencimento, é na memoria da minha secretaria mesmo. esse ano ja perdi umas 12 renovação assim, cliente antigo de 8 ano

- **Justificativa do gerador:** A dor e a renovacao com data conhecida que ninguem retoma a tempo, perdendo para o concorrente uma venda que ja estava na mao.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 14. `r6_com_08` — gabarito proposto: **comercial**

> loja de calçado. direto entra gente perguntando por numero que ta em falta e a menina responde certinho, fala que chega na semana seguinte, isso funciona bem. o problema e que quando a mercadoria chega ninguem avisa essas pessoa. a lista fica num caderno embaixo do balcão e vira mes com nome antigo. é venda na mao que passa batido toda semana

- **Justificativa do gerador:** A resposta ao contato ja acontece e e elogiada, o que falha e retomar o interessado quando o produto chega, perdendo uma venda ja qualificada.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### Atendimento (6)

### 15. `r6_atd_01` — gabarito proposto: **atendimento**

> tenho uma escola de ingles com 2 unidade. o aluno manda no whats da unidade, outro chama no instagram, tem o email da secretaria e ainda aquele chat do site. ninguem sabe o que ja foi respondido e o que nao foi, semana passada uma mae cobrou 3 vez a mesma coisa em lugar diferente e ninguem tinha visto nenhuma

- **Justificativa do gerador:** A dor e mensagem de quem ja escreveu se perdendo entre canais dispersos, sem ninguem saber o que ficou sem resposta.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 16. `r6_atd_03` — gabarito proposto: **atendimento**

> industria de embalagem plastica aqui. meu tecnico de aplicação, que e o cara que entende de verdade do produto, passa o dia inteiro no whats respondendo se tem no estoque, qual o prazo e qual o codigo da bobina. e sempre as mesmas 5 pergunta e ele nao consegue mais olhar o que e serio

- **Justificativa do gerador:** A dor e a mesma duvida basica repetida consumindo quem deveria estar em outra coisa, ou seja, carga de resposta a quem escreveu.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 17. `r6_atd_04` — gabarito proposto: **atendimento**

> clinica veterinaria. quem responde mensagem aqui e so a Fabi da recepção. ela tirou 15 dia de ferias em junho e quando voltou tinha mais de 400 mensagem sem ler, teve tutor que perguntou de reforço de vacina e nunca teve resposta nenhuma. se ela falta um dia ja acumula tudo de novo

- **Justificativa do gerador:** A dor e a fila de mensagens parar de andar porque a resposta depende de uma unica pessoa, deixando quem escreveu sem retorno.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 18. `r6_atd_05` — gabarito proposto: **atendimento**

> sou dono de uma distribuidora de autopeça. os mecanico mandam audio de 4, 5 minuto perguntando se a peça serve no carro tal, com barulho de oficina no fundo. ninguem aqui para pra ouvir aquilo no meio do expediente, ai acumula um monte de audio sem resposta e no outro dia o cara manda de novo perguntando se chegou a mensagem

- **Justificativa do gerador:** A dor e o custo de ouvir e responder audio fazendo a fila de contatos ficar sem retorno, o que e trato com quem escreveu.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 19. `r6_atd_06` — gabarito proposto: **atendimento**

> loja de movel planejado. tenho 3 pessoa revezando no numero da loja, cada dia responde uma. dai o cliente tem que contar a historia inteira de novo, o que comprou, qual e o problema da porta, quem foi que montou. ja ouvi 'mas eu expliquei isso ontem pra outra moça' umas 10 vez so esse mes

- **Justificativa do gerador:** A dor e o contexto da conversa se perder na troca de atendente, obrigando quem escreveu a repetir tudo.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 20. `r6_atd_08` — gabarito proposto: **atendimento**

> tenho um auto center com 4 elevador. a operadora manda um relatorio e semana passada deu 34 ligação perdida em 5 dia util. ninguem consegue largar o carro no meio pra atender telefone e o povo nao deixa recado, liga, liga de novo e desiste. quem insiste chega aqui reclamando que nunca atendem

- **Justificativa do gerador:** A dor e o contato entrante que nao encontra ninguem para atender, um problema de cobertura de atendimento e nao de acompanhamento de venda.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### Marketing (6)

### 21. `r6_mkt_01` — gabarito proposto: **marketing**

> boa tarde. tenho um restaurante japones em santo andre. semana passada chegaram dois cliente falando que achavam que a gente tinha fechado, pq quem procura na internet acha o telefone antigo e um cardapio de 2021 com preço de antes da pandemia. mudamos de ponto faz um ano e isso nunca foi atualizado em lugar nenhum

- **Justificativa do gerador:** A dor e a presenca digital defasada afastando quem procura o negocio antes de qualquer contato.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 22. `r6_mkt_02` — gabarito proposto: **marketing**

> tenho um estudio de pilates. eu me animo e posto todo dia por umas 3 semana, ai aparece gente perguntando, dai entra correria de aula e eu sumo 2, 3 mes. quando volto é do zero de novo, parece que ninguem lembra que existe. ja fiz esse liga desliga umas 4 vez so esse ano

- **Justificativa do gerador:** A dor e a campanha sem consistencia, que zera o alcance a cada parada, e nao a falta de conteudo em si.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 23. `r6_mkt_04` — gabarito proposto: **marketing**

> faço movel planejado ha 12 ano. termino a obra, entrego e vou embora, nunca parei pra registrar nada. ai quando alguem pede indicação no grupo do predio, meus cliente antigo falam bem mas nao tem uma foto pra mandar, e eu tbm nao tenho. quem mostra trabalho pronto leva o serviço

- **Justificativa do gerador:** A dor e nao ter material de prova do proprio trabalho para circular, ou seja, nada a mostrar.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 24. `r6_mkt_06` — gabarito proposto: **marketing**

> queria um programa que dispara mensagem de revisão pros cliente antigo da oficina, pq de cliente novo eu ja desisti. meu sobrinho foi pesquisar aqui pra me mostrar e a auto center aparece no mapa com uma foto tremida de 2018, sem horario, sem serviço escrito, sem nada. ele falou que se fosse ele nem clicava

- **Justificativa do gerador:** A dor e o unico ativo digital do negocio estar vazio e afastar quem procura, mesmo o produto pedido apontando para disparo comercial.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 25. `r6_mkt_07` — gabarito proposto: **marketing**

> vendo roupa feminina, uns 90% do pedido vinha de um marketplace. esse mes eles mecheram em alguma coisa la e meu pedido caiu pela metade da noite pro dia. me toquei que fora daquele app eu nao existo: nao tenho perfil montado, nao tenho nada publicado, ninguem me acha se nao for por la

- **Justificativa do gerador:** A dor e depender de um canal de terceiro sem nenhuma presenca propria por onde ser encontrada.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 26. `r6_mkt_08` — gabarito proposto: **marketing**

> tenho uma escola tecnica no interior. abri o curso de eletricista predial faz 8 mes e nao tem uma linha escrita sobre ele em lugar nenhum, nem no site, nem no folder que a gente distribui na praça. quem descobre é quem pergunta na recepção por acaso. com o de refrigeração foi igual, so lotou depois de 2 ano

- **Justificativa do gerador:** A dor e a oferta nao ter conteudo nenhum que a comunique, entao o publico nem fica sabendo que ela existe.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### Operacional (7)

### 27. `r6_ope_01` — gabarito proposto: **operacional**

> sou eng civil, tenho uma empresa pequena que faz obra pra prefeitura. todo dia de manha alguem aqui abre uns 12 portal de licitacao um por um, le edital por edital e anota numa planilha o que serve pra gente. isso come 3h por dia de uma pessoa e mesmo assim mes passado passou batido um que era a nossa cara

- **Justificativa do gerador:** A dor e uma varredura de pesquisa recorrente feita a mao todo dia, nao falta de demanda nem lead perdido.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 28. `r6_ope_02` — gabarito proposto: **operacional**

> tenho uma metalurgica com 62 operador em 3 turno. quem monta a escala sou eu, no papel mesmo, toda quinta a tarde, encaixando ferias, folga e quem ta de atestado. levo umas 5 hora e ainda sai errado, semana passada deixei o setor de solda sem ninguem no turno da noite

- **Justificativa do gerador:** A dor e a montagem manual e semanal de um documento de escala, tarefa interna repetitiva sem nenhuma conversa envolvida.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 29. `r6_ope_03` — gabarito proposto: **operacional**

> clinica de oftalmo aqui. todo comeco de mes a menina do faturamento senta com o extrato do convenio de um lado e as guia do outro e vai batendo uma por uma pra ver o que eles cortaram. sao quase 900 guia, ela leva uns 4 dia nisso e sempre escapa alguma coisa

- **Justificativa do gerador:** A dor e conferir duas fontes linha a linha na mao todo mes, trabalho administrativo repetitivo e nao trato com quem escreveu pra empresa.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 30. `r6_ope_04` — gabarito proposto: **operacional**

> tenho 3 pizzaria. sempre que o fornecedor sobe o preco do queijo ou da farinha eu preciso refazer o custo de umas 80 ficha tecnica na calculadora pra saber se o preco do cardapio ainda se paga. faco isso num excel na mao e ja perdi domingo inteiro nessa brincadeira, e olha que preco sobe direto

- **Justificativa do gerador:** A dor e o recalculo manual em cascata de dezenas de fichas toda vez que um dado muda, processo interno repetitivo.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 31. `r6_ope_05` — gabarito proposto: **operacional**

> laboratorio de analise clinica. os laudo saem do equipamento em pdf com nome tipo DOC00017, ai alguem tem que abrir um por um, ver de quem e, renomear e jogar na pasta certa. sao umas 400 por dia e ja aconteceu de laudo ir parar na pasta do paciente errado

- **Justificativa do gerador:** A dor e triar e organizar arquivo por arquivo na mao, tarefa administrativa em volume, com erro nascendo do proprio processo.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 32. `r6_ope_06` — gabarito proposto: **operacional**

> me falaram que eu precisava de um crm e vim atras. so que parando pra pensar o gargalo aqui nao e lembrar de cliente nao, isso a gente da conta. sou de uma concessionaria de maquina agricola e pra cada venda financiada alguem monta a pasta com 9 documento, escaneia tudo, preenche 2 formulario do banco e protocola. da quase 2h por venda, e a gente faz umas 30 no mes

- **Justificativa do gerador:** O produto pedido e CRM, mas a dor descrita e a montagem manual de dossie documental por venda, e o proprio lead descarta o esquecimento de cliente como problema.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 33. `r6_ope_08` — gabarito proposto: **operacional**

> tenho um cursinho pre vestibular. a cada 15 dia a gente aplica simulado de 90 questao pra 400 aluno. os professor corrigem folha por folha com o gabarito na mao e depois alguem digita nota por nota no sistema pra sair o ranking. leva quase uma semana e quando o aluno ve o resultado ja nem lembra mais da prova

- **Justificativa do gerador:** A dor e correcao e lancamento manual repetidos a cada ciclo, trabalho de processo interno e nao conversa com aluno.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### Indefinido (7)

### 34. `r6_ind_01` — gabarito proposto: **indefinido**

> boa tarde, é aqui mesmo da empresa? achei o contato de vcs num grupo de whats de empresario aqui de campinas. tenho uma clinica veterinaria no cambui. tudo bem se eu chamar depois? agora to em consulta

- **Justificativa do gerador:** Saudação com identificação de setor e agendamento de retorno, sem uma única frase sobre o que está dando errado hoje.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 35. `r6_ind_02` — gabarito proposto: **indefinido**

> sou da diretoria de uma industria de embalagem plastica em joinville. fechamos o primeiro semestre 22% abaixo do mesmo periodo do ano passado e o conselho ta em cima de mim cobrando explicação. preciso de alguma coisa que vire esse jogo ainda esse ano. o que voces conseguem fazer?

- **Justificativa do gerador:** Só o placar (queda de 22%) e a cobrança do conselho, sem dizer onde o processo quebra — resultado ruim não é mecanismo de dor.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 36. `r6_ind_03` — gabarito proposto: **indefinido**

> tenho uma transportadora pequena, 12 caminhão rodando entre sp e o sul. a coisa ta indo bem graças a deus, cliente fiel, agenda cheia o mes inteiro, nao tenho do que reclamar. meu contador comentou semana passada que empresa do meu porte ja devia ter um crm faz tempo e aquilo ficou na minha cabeça. voces mexem com isso? queria so entender o que muda na pratica

- **Justificativa do gerador:** Nomeia um produto de comercial (CRM) por sugestão do contador e declara explicitamente que não há nada dando errado, então rotular comercial seria inferir do produto.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 37. `r6_ind_04` — gabarito proposto: **indefinido**

> boa noite. vou me apresentar direito pq acho que ajuda voces a entender. meu pai abriu a marcenaria em 1994 num galpão alugado em são bento do sul e hoje a gente tem 3 loja, 46 funcionario e fabrica propria de uns 2 mil metro. trabalhamos so com planejado sob medida, cozinha e dormitorio, ticket medio uns 38 mil, e nossa venda vem 70% de arquiteto que indica e 30% de quem entra na loja. dezembro e janeiro sao os mes forte, junho e o pior de todos, e ano passado a gente fechou 11 milhão de faturamento. to assumindo a empresa agora que meu pai se aposentou em marco e quero fazer as coisa do jeito certo desde o comeco. me falaram bem de voces. da pra marcar uma conversa pra voces me explicarem direitinho o que fazem?

- **Justificativa do gerador:** Mensagem longa e cheia de contexto de negócio (histórico, porte, mix de canal, sazonalidade, faturamento) que em nenhum momento descreve algo que se perde, se refaz na mão ou não dá conta.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 38. `r6_ind_06` — gabarito proposto: **indefinido**

> cara vou ser sincero contigo, to no meu limite. abri o restaurante achando que ia ser uma coisa e é outra totalmente diferente. chego 7 da manha, saio meia noite, e mesmo assim tenho a sensação de que nada anda pra frente. minha esposa ja reclamou umas 3 vez esse mes. sei que preciso mudar alguma coisa aqui dentro mas nem sei te dizer por onde começar, so sei que do jeito que ta nao da mais

- **Justificativa do gerador:** Desabafo sobre exaustão e horas trabalhadas sem nomear uma única tarefa, mensagem, lead ou documento — não há mecanismo, só sintoma.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 39. `r6_ind_07` — gabarito proposto: **indefinido**

> Bom dia. Encaminho o contato conforme orientação da nossa diretoria. Somos uma rede de 14 farmácias no interior de Goiás, em operação desde 2007, hoje com aproximadamente 190 colaboradores e faturamento na casa dos 60 milhões ao ano. Fui designada responsável pela seleção de fornecedores do projeto previsto no orçamento de 2027, com verba já aprovada na ordem de 180 mil. O fluxo aqui funciona assim: recebo três propostas, monto o comparativo, levo ao comitê que se reúne toda última quinta-feira do mês e a decisão sai em até 45 dias. Preciso que a proposta venha com escopo detalhado, prazo de implantação e cláusula de SLA, e que chegue até o dia 20 para entrar nesta rodada. Fico à disposição.

- **Justificativa do gerador:** Traz verba, prazo e poder de compra em detalhe, mas descreve apenas o rito de compra da empresa — sinal comercial de qualificação não é dor descrita.
- Confiança declarada: `alta`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### 40. `r6_ind_08` — gabarito proposto: **indefinido**

> meu contrato com a agencia que cuida da parte digital da otica vence em setembro e eu ja avisei que nao vou renovar. nao é que eles fizeram algo de errado nao, o socio de la mudou de cidade e ficou ruim pros dois lado. to pegando orçamento com umas 4 empresa pra ver quem assume dali pra frente. voces trabalham com esse tipo de contrato? como funciona o formato de voces?

- **Justificativa do gerador:** A troca de fornecedor é por motivo pessoal do prestador e o lead nega explicitamente insatisfação, então o serviço de marketing citado é só o produto em pauta, não uma dor.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---

### Ambíguo (1)

### 41. `r6_amb_02` — gabarito proposto: **marketing**

> invisto no insta e entra contato pra caramba, uns 30 por semana. so que 8 em cada 10 pergunta coisa que a gente nem faz, tipo conserto de celular, e aqui e montagem de computador. meu vendedor passa o dia inteiro conversando com quem nunca ia comprar

- **Justificativa do gerador:** A dor e a comunicacao que nao diz o que a empresa faz e por isso atrai o publico errado, falha anterior ao contato; a leitura comercial (vendedor sem triagem, tempo de funil desperdicado) foi descartada porque o vendedor esta atendendo todo mundo, o defeito nasce na mensagem publicada e nao no processo de venda.
- Confiança declarada: `media`

**Decisão:** `[ ] manter`  `[ ] trocar para ____________`  `[ ] descartar`

---
