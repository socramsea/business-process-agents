"""
Casos de regressão da INSTRUCAO — o gabarito contra o qual toda mudança roda.
Regression cases for INSTRUCAO — the answer key every change runs against.

Cada caso declara só os campos que aquele cenário deve travar. O que não está
declarado não é cobrado: ninguém precisa opinar sobre 'urgencia' num caso que
existe pra testar autoridade.

Each case declares only the fields that scenario should pin down.
"""

from typing import Any

# categoria -> por que este grupo existe
CATEGORIAS = {
    "proprietario_explicito": "diz com todas as letras que é dono",
    "proprietario_implicito": "possessivo aplicado ao negócio, sem dizer 'sou dono'",
    "socio": "sociedade declarada",
    "fundador": "fundou o negócio",
    "gerente": "cargo de gestão, com ou sem poder de compra declarado",
    "compras": "responsável por compra/aprovação de orçamento",
    "funcionario": "trabalha lá, sem poder de decisão declarado",
    "agencia": "fala em nome de clientes de terceiros",
    "consultor": "presta serviço para quem decide",
    "estudante": "pesquisa acadêmica",
    "curioso": "quer informação, sem vínculo declarado",
    "spam": "mensagem que não é lead",
    "curta": "texto curto demais para sustentar sinal",
    "ambigua": "evidência insuficiente ou contraditória",
    "descadastro": "pede para sair",
    "sinais_combinados": "autoridade junto com orçamento/urgência",
    "agente_comercial": "dor de oportunidade perdida",
    "agente_atendimento": "dor no trato com quem já escreveu",
    "agente_marketing": "dor de não ser encontrado ou não ter o que mostrar",
    "agente_operacional": "dor de trabalho repetitivo que não é conversa",
    "agente_indefinido": "sem mecanismo de dor descrito — não chutar",
    "agente_armadilha": "produto aponta pra um time, dor aponta pra outro",
    "agente_ambiguo": "duas categorias competem de verdade — gabarito frágil por natureza",
}

CASOS: list[dict[str, Any]] = [
    # ---- proprietário explícito ----
    {
        "id": "prop_exp_01",
        "categoria": "proprietario_explicito",
        "mensagem": "sou dono de uma clínica odontológica e quero divulgar melhor",
        "esperado": {"autoridade": True, "descadastro": False},
    },
    {
        "id": "prop_exp_02",
        "categoria": "proprietario_explicito",
        "mensagem": "sou proprietário de um restaurante no Leblon, quero fotos do salão",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_exp_03",
        "categoria": "proprietario_explicito",
        "mensagem": "eu que sou o dono do negócio, então falo direto com vocês",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_exp_04",
        "categoria": "proprietario_explicito",
        "mensagem": "administro uma rede de academias e preciso padronizar a comunicação",
        "esperado": {"autoridade": True},
    },
    # ---- proprietário implícito (o alvo do marco: falso negativo) ----
    {
        "id": "prop_imp_01",
        "categoria": "proprietario_implicito",
        "mensagem": "tenho uma clínica em Botafogo, quero vídeo institucional",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_imp_02",
        "categoria": "proprietario_implicito",
        "mensagem": "minha empresa precisa de uma identidade visual nova",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_imp_03",
        "categoria": "proprietario_implicito",
        "mensagem": "meu consultório está sem site, dá pra resolver?",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_imp_04",
        "categoria": "proprietario_implicito",
        "mensagem": "abri uma clínica de estética mês passado e preciso aparecer",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_imp_05",
        "categoria": "proprietario_implicito",
        "mensagem": "nossa loja no centro precisa de vídeos pro Instagram",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_imp_06",
        "categoria": "proprietario_implicito",
        "mensagem": "quero implantar isso na minha empresa ainda esse ano",
        "esperado": {"autoridade": True, "urgencia": True},
    },
    {
        "id": "prop_imp_07",
        "categoria": "proprietario_implicito",
        "mensagem": "preciso para minha clínica, o que vocês oferecem?",
        "esperado": {"autoridade": True},
    },
    {
        "id": "prop_imp_08",
        "categoria": "proprietario_implicito",
        "mensagem": "montei um petshop e não sei por onde começar no marketing",
        "esperado": {"autoridade": True},
    },
    # ---- sócio ----
    {
        "id": "socio_01",
        "categoria": "socio",
        "mensagem": "sou sócio de uma corretora e queremos rebranding",
        "esperado": {"autoridade": True},
    },
    {
        "id": "socio_02",
        "categoria": "socio",
        "mensagem": "eu e meu sócio abrimos um escritório de arquitetura esse ano",
        "esperado": {"autoridade": True},
    },
    {
        "id": "socio_03",
        "categoria": "socio",
        "mensagem": "sou sócio-administrador da empresa, quem fecha contrato sou eu",
        "esperado": {"autoridade": True},
    },
    # ---- fundador ----
    {
        "id": "fund_01",
        "categoria": "fundador",
        "mensagem": "sou fundador de uma startup de saúde e preciso de posicionamento",
        "esperado": {"autoridade": True},
    },
    {
        "id": "fund_02",
        "categoria": "fundador",
        "mensagem": "fundei a empresa em 2019 e nunca investimos em marca",
        "esperado": {"autoridade": True},
    },
    {
        "id": "fund_03",
        "categoria": "fundador",
        "mensagem": "sou cofundadora e cuido de tudo de marketing aqui",
        "esperado": {"autoridade": True},
    },
    # ---- gerente ----
    {
        "id": "ger_01",
        "categoria": "gerente",
        "mensagem": "sou gerente de marketing da Acme e estamos avaliando fornecedores",
        "esperado": {"autoridade": False},
    },
    {
        "id": "ger_02",
        "categoria": "gerente",
        "mensagem": "sou gerente e eu que aprovo o orçamento de marketing aqui",
        "esperado": {"autoridade": True},
    },
    {
        "id": "ger_03",
        "categoria": "gerente",
        "mensagem": "trabalho como gerente comercial, meu diretor pediu pra buscar opções",
        "esperado": {"autoridade": False},
    },
    {
        "id": "ger_04",
        "categoria": "gerente",
        "mensagem": "gerencio a unidade da Barra, mas a decisão é da matriz",
        "esperado": {"autoridade": False},
    },
    # ---- responsável por compras ----
    {
        "id": "compras_01",
        "categoria": "compras",
        "mensagem": "sou responsável pelas compras da rede e preciso de proposta",
        "esperado": {"autoridade": True},
    },
    {
        "id": "compras_02",
        "categoria": "compras",
        "mensagem": "eu aprovo o orçamento, me manda os valores por favor",
        "esperado": {"autoridade": True},
    },
    {
        "id": "compras_03",
        "categoria": "compras",
        "mensagem": "sou eu que decido o fornecedor, mas quero comparar antes",
        "esperado": {"autoridade": True},
    },
    {
        "id": "compras_04",
        "categoria": "compras",
        "mensagem": "trabalho no setor de compras e coleto orçamentos pra diretoria decidir",
        "esperado": {"autoridade": False},
    },
    # ---- funcionário ----
    {
        "id": "func_01",
        "categoria": "funcionario",
        "mensagem": "sou analista de marketing na Acme, meu chefe pediu pra pesquisar preços",
        "esperado": {"autoridade": False},
    },
    {
        "id": "func_02",
        "categoria": "funcionario",
        "mensagem": "trabalho na recepção da clínica e me pediram pra entrar em contato",
        "esperado": {"autoridade": False},
    },
    {
        "id": "func_03",
        "categoria": "funcionario",
        "mensagem": "sou estagiária e estou levantando fornecedores pra equipe",
        "esperado": {"autoridade": False},
    },
    {
        "id": "func_04",
        "categoria": "funcionario",
        "mensagem": "faço parte do time de comunicação, quem decide é a diretoria",
        "esperado": {"autoridade": False},
    },
    # ---- agência ----
    {
        "id": "agencia_01",
        "categoria": "agencia",
        "mensagem": "somos uma agência e buscamos parceiro de vídeo para nossos clientes",
        "esperado": {"autoridade": False},
    },
    {
        "id": "agencia_02",
        "categoria": "agencia",
        "mensagem": "atendo vários clientes e preciso terceirizar a produção audiovisual",
        "esperado": {"autoridade": False},
    },
    {
        "id": "agencia_03",
        "categoria": "agencia",
        "mensagem": "minha agência tem um cliente que precisa de institucional em novembro",
        "esperado": {"autoridade": False, "urgencia": True},
    },
    # ---- consultor / prestador ----
    {
        "id": "cons_01",
        "categoria": "consultor",
        "mensagem": "sou consultor de marketing e recomendo fornecedores pros meus clientes",
        "esperado": {"autoridade": False},
    },
    {
        "id": "cons_02",
        "categoria": "consultor",
        "mensagem": "presto serviço pra uma rede de clínicas e me pediram indicações",
        "esperado": {"autoridade": False},
    },
    {
        "id": "cons_03",
        "categoria": "consultor",
        "mensagem": "sou freelancer de design e às vezes preciso de parceiro de vídeo",
        "esperado": {"autoridade": False},
    },
    # ---- estudante / pesquisador ----
    {
        "id": "est_01",
        "categoria": "estudante",
        "mensagem": "faço TCC sobre marketing digital, pode me explicar como funciona?",
        "esperado": {"autoridade": False},
    },
    {
        "id": "est_02",
        "categoria": "estudante",
        "mensagem": "sou pesquisador e estudo precificação no setor criativo",
        "esperado": {"autoridade": False},
    },
    {
        "id": "est_03",
        "categoria": "estudante",
        "mensagem": "estudo publicidade e queria entender como vocês cobram",
        "esperado": {"autoridade": False},
    },
    # ---- curioso ----
    {
        "id": "cur_01",
        "categoria": "curioso",
        "mensagem": "quanto custa um vídeo institucional?",
        "esperado": {"autoridade": False, "orcamento": False},
    },
    {
        "id": "cur_02",
        "categoria": "curioso",
        "mensagem": "vocês trabalham com que tipo de cliente?",
        "esperado": {"autoridade": False},
    },
    {
        "id": "cur_03",
        "categoria": "curioso",
        "mensagem": "vi o portfólio de vocês, ficou muito bom o trabalho",
        "esperado": {"autoridade": False},
    },
    {
        "id": "cur_04",
        "categoria": "curioso",
        "mensagem": "queria entender melhor como funciona o processo de vocês",
        "esperado": {"autoridade": False},
    },
    # ---- spam ----
    {
        "id": "spam_01",
        "categoria": "spam",
        "mensagem": "GANHE DINHEIRO EM CASA!!! CLIQUE AQUI bit.ly/xyz",
        "esperado": {"autoridade": False, "orcamento": False, "urgencia": False},
    },
    {
        "id": "spam_02",
        "categoria": "spam",
        "mensagem": "Promoção imperdível: 500 seguidores por R$ 19,90, só hoje!",
        "esperado": {"autoridade": False},
    },
    {
        "id": "spam_03",
        "categoria": "spam",
        "mensagem": "asdkjhasd 123 !!! ???",
        "esperado": {"autoridade": False, "orcamento": False, "urgencia": False},
    },
    # ---- muito curtas ----
    {
        "id": "curta_01",
        "categoria": "curta",
        "mensagem": "oi",
        "esperado": {"autoridade": False, "orcamento": False, "urgencia": False},
    },
    {
        "id": "curta_02",
        "categoria": "curta",
        "mensagem": "bom dia",
        "esperado": {"autoridade": False, "orcamento": False},
    },
    {
        "id": "curta_03",
        "categoria": "curta",
        "mensagem": "info",
        "esperado": {"autoridade": False},
    },
    {
        "id": "curta_04",
        "categoria": "curta",
        "mensagem": "orçamento",
        "esperado": {"autoridade": False, "orcamento": False},
    },
    # ---- ambíguas ----
    {
        "id": "amb_01",
        "categoria": "ambigua",
        "mensagem": "estamos precisando de vídeo institucional",
        "esperado": {"autoridade": False},
    },
    {
        "id": "amb_02",
        "categoria": "ambigua",
        "mensagem": "a empresa quer renovar a marca esse ano",
        "esperado": {"autoridade": False},
    },
    {
        "id": "amb_03",
        "categoria": "ambigua",
        "mensagem": "me pediram pra falar com vocês sobre o projeto novo",
        "esperado": {"autoridade": False},
    },
    {
        "id": "amb_04",
        "categoria": "ambigua",
        "mensagem": "trabalho com estética e queria melhorar minha divulgação",
        "esperado": {"autoridade": False},
    },
    # ---- descadastro ----
    {
        "id": "desc_01",
        "categoria": "descadastro",
        "mensagem": "me tira do mailing, não quero mais receber nada",
        "esperado": {"descadastro": True, "autoridade": False},
    },
    {
        "id": "desc_02",
        "categoria": "descadastro",
        "mensagem": "não tenho interesse, obrigado",
        "esperado": {"descadastro": True},
    },
    {
        "id": "desc_03",
        "categoria": "descadastro",
        "mensagem": "tenho uma clínica mas não quero mais receber mensagens de vocês",
        "esperado": {"descadastro": True, "autoridade": True},
    },
    # ---- sinais combinados ----
    {
        "id": "comb_01",
        "categoria": "sinais_combinados",
        "mensagem": (
            "oi, tenho uma clínica em Botafogo, quero vídeo institucional, "
            "orçamento até 8 mil, preciso pra outubro"
        ),
        "esperado": {
            "autoridade": True,
            "orcamento": True,
            "urgencia": True,
            "descadastro": False,
        },
    },
    {
        "id": "comb_02",
        "categoria": "sinais_combinados",
        "mensagem": "sou dono da empresa, tenho 50 mil de verba e preciso fechar até sexta",
        "esperado": {"autoridade": True, "orcamento": True, "urgencia": True},
    },
    {
        "id": "comb_03",
        "categoria": "sinais_combinados",
        "mensagem": "minha loja precisa de fotos, mas ainda não tenho verba definida",
        "esperado": {"autoridade": True, "orcamento": False},
    },
    {
        "id": "comb_04",
        "categoria": "sinais_combinados",
        "mensagem": "sou analista aqui, temos 30 mil aprovados pra esse projeto",
        "esperado": {"autoridade": False, "orcamento": True},
    },
    # ---- agente_indicado: quem manda é a dor descrita, não o produto pedido ----
    {
        "id": "ag_arm_01",
        "categoria": "agente_armadilha",
        # O produto pedido e midia paga, mas a dor descrita e perda por demora no retorno ao lead,
        # que e comercial.
        "mensagem": (
            "queria contratar trafego pago pra chegar mais lead. na verdade lead ja chega "
            "uns 40 por mes do google, o problema e que meu vendedor liga 3 dia depois e o "
            "cara ja fechou com o concorrente"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "ag_arm_02",
        "categoria": "agente_armadilha",
        # O produto pedido aponta atendimento, mas a dor descrita e documento repetitivo montado a
        # mao, que e operacional.
        "mensagem": (
            "queria um robo pra atender os cliente no whats. o que mata mesmo aqui e que "
            "pra cada pedido eu monto o orçamento na mao no word, copiando preco da tabela, "
            "umas 30 vez por dia"
        ),
        "esperado": {"agente_indicado": "operacional"},
        # fronteira: chatbot pedido compete com o orçamento montado à mão
        "atrito": True,
    },
    {
        "id": "ag_arm_03",
        "categoria": "agente_armadilha",
        # O produto pedido e ferramenta de vendas, mas a dor e ausencia total de demanda entrante
        # por desconhecimento da marca.
        "mensagem": (
            "me indicaram um crm pra organizar o funil de vendas. so que funil nao tem, faz "
            "uns 4 mes que nao entra um contato novo aqui, ninguem na regiao conhece a "
            "marca"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "ag_arm_04",
        "categoria": "agente_armadilha",
        # O produto pedido e social media, mas a dor e volume de mensagens sem resposta, que e
        # atendimento.
        "mensagem": (
            "queria contratar alguem pra cuidar das redes sociais da loja. seguidor a gente "
            "tem 20 mil, o buraco e que chega uns 100 direct por dia perguntando preco e "
            "prazo e a gente responde uns 10"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "ag_arm_05",
        "categoria": "agente_armadilha",
        # Ha produto pedido com nome de area, mas nenhuma dor descrita, entao rotular como
        # atendimento seria inferir do produto.
        "mensagem": (
            "quero contratar um chatbot de atendimento pro meu site, igual aquele que vi na "
            "empresa do meu primo. me passa como funciona e quanto custa?"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "ag_arm_06",
        "categoria": "agente_armadilha",
        # produto pedido e operacional; a dor descrita e lead sem follow-up
        "mensagem": (
            "queria automatizar minha planilha de clientes. o problema real e que a "
            "planilha tem 400 lead que pediram orcamento e ninguem nunca voltou pra eles"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "ag_atd_01",
        "categoria": "agente_atendimento",
        # A dor e volume de mensagens repetidas sem resposta em tempo, que e sobrecarga de
        # atendimento.
        "mensagem": (
            "tenho uma clinica de fisio, chega uns 80 whats por dia perguntando horario, "
            "convenio e valor da sessão. a menina da recepção nao da conta e as vez "
            "responde so no outro dia"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "ag_atd_02",
        "categoria": "agente_atendimento",
        # A dor e fila de mensagens recorrentes sem resposta, nao ausencia de publico ou de
        # conteudo.
        "mensagem": (
            "meu direct ta com umas 3 semana de acumulo. eu abro, olho, fecho e nao "
            "respondo pq e sempre a mesma pergunta e eu ja to cansado de digitar a mesma "
            "coisa"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "ag_atd_03",
        "categoria": "agente_atendimento",
        # A dor e o cliente ja comprado ficando sem resposta, o que e suporte e nao venda.
        "mensagem": (
            "vendemos equipamento de cozinha industrial e o pos venda ta um caos. cliente "
            "manda duvida de uso e a gente leva 2 dia pra retornar, ja apareceu reclamação "
            "no google por causa disso"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "ag_atd_04",
        "categoria": "agente_atendimento",
        # A dor e janela de silencio e acumulo de mensagens, um problema de cobertura de
        # atendimento.
        "mensagem": (
            "sabado e domingo nao tem ninguem aqui pra responder nada, ai na segunda tem "
            "umas 200 mensagem esperando. o pessoal ja fala que a gente some no fim de "
            "semana"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "ag_atd_05",
        "categoria": "agente_atendimento",
        # A dor e a demanda de resposta durante o pedido em curso, tipica de atendimento e nao de
        # processo interno.
        "mensagem": (
            "delivery aqui e por whats mesmo. o cliente manda o pedido, depois pergunta se "
            "ja saiu, ninguem responde pq ta todo mundo na cozinha, ai ele liga irritado no "
            "meio do movimento"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "ag_com_01",
        "categoria": "agente_comercial",
        # a dor e o follow-up que ninguem fez, nao o tempo de produzir a proposta
        "mensagem": (
            "tenho uma revenda de maquina de corte. mando a proposta na sexta e so lembro "
            "de cobrar resposta uma semana depois. quando ligo o cara ja comprou de outro"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "ag_com_02",
        "categoria": "agente_comercial",
        # A dor e o abandono do lead depois do interesse demonstrado, ou seja, perda por falta de
        # acompanhamento comercial.
        "mensagem": (
            "sou dona de imobiliaria. a pessoa visita o imovel, gosta, e depois disso "
            "ninguem liga de volta pra ela. mes passado escapou dois negocio desse jeito"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "ag_com_03",
        "categoria": "agente_comercial",
        # A dor e negociacao aberta esfriando sem que ninguem note, que e perda de oportunidade em
        # andamento.
        "mensagem": (
            "montei um time de 3 pra prospectar e ninguem sabe me dizer em que pe ta cada "
            "negociação. tem cliente que sumiu faz uns 2 mes e ninguem percebeu que ele "
            "tinha sumido"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "ag_com_04",
        "categoria": "agente_comercial",
        # A dor e a negociacao interrompida na objeacao de preco sem retomada, que e trabalho de
        # reengajamento comercial.
        "mensagem": (
            "quando o cliente fala que ta caro a conversa morre ali e ninguem volta a falar "
            "com ele nunca mais. deve ter uns 200 parado desse jeito no meu caderno"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "ag_com_05",
        "categoria": "agente_comercial",
        # A dor esta no avanco da venda ate o fechamento, e o proprio lead descarta atendimento
        # como problema.
        "mensagem": (
            "a gente atende bem, responde rapido, o pessoal elogia. so que na hora de puxar "
            "pro fechamento ninguem puxa, fica todo mundo esperando o cliente decidir "
            "sozinho"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "ag_ind_01",
        "categoria": "agente_indefinido",
        # Ha interesse declarado mas nenhuma dor descrita, entao qualquer rotulo seria chute.
        "mensagem": (
            "boa tarde! vi o trabalho de voces pelo linkedin de um amigo e achei bem "
            "interessante o que faz. queria entender melhor como funciona pra ver se faz "
            "sentido pra gente aqui"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "ag_ind_02",
        "categoria": "agente_indefinido",
        # Formulario preenchido com pedido generico de informacao, sem nenhum problema descrito.
        "mensagem": (
            "Nome: Ricardo Alves / Empresa: RC Distribuidora de Bebidas / Mensagem: "
            "gostaria de receber mais informações sobre os serviços prestados e a tabela de "
            "valores. Atenciosamente"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "ag_ind_03",
        "categoria": "agente_indefinido",
        # Sem operacao rodando nao existe dor concreta descrita, so intencao preventiva vaga.
        "mensagem": (
            "to abrindo uma empresa de importação, ainda nao comecei a operar. quero ja "
            "deixar tudo redondo desde o comeco pra nao ter dor de cabeca depois. como "
            "voces trabalham?"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "ag_ind_04",
        "categoria": "agente_indefinido",
        # O contato e por indicacao de terceiro e o proprio lead nao sabe qual e o problema, entao
        # nao ha sinal.
        "mensagem": (
            "meu socio falou que voces resolveram um problema serio na empresa do primo "
            "dele e mandou eu chamar aqui. sinceramente eu nem sei direito o que voces "
            "fazem, ele que entende disso"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "ag_ind_05",
        "categoria": "agente_indefinido",
        # ARBITRADO por Marcos: indefinido reafirmado, mesmo o modelo tendo lido
        # operacional numa rodada. Desorganizacao generica nao sustenta implantar
        # nenhum dos quatro agentes.
        "mensagem": (
            "a gente cresceu bastante nos ultimo 2 ano e ficou tudo meio desorganizado, "
            "sinto que da pra melhorar muita coisa. voces conseguem me ajudar nisso?"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "ag_mkt_01",
        "categoria": "agente_marketing",
        # A dor e ausencia de gente nova chegando por desconhecimento da marca, ou seja, falta de
        # presenca e conteudo.
        "mensagem": (
            "tenho um petshop no bairro ha 6 anos e gente que mora a 3 quadra daqui nao "
            "sabe que existe. so entra cliente antigo, novo mesmo nao aparece"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "ag_mkt_02",
        "categoria": "agente_marketing",
        # A dor e a producao de conteudo parada secando a entrada de contatos, causa tipicamente
        # de marketing.
        "mensagem": (
            "a gente parou de postar em fevereiro porque ninguem aqui tem tempo de sentar e "
            "produzir. de la pra ca nao chegou mais nenhum contato novo, so os de sempre"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "ag_mkt_03",
        "categoria": "agente_marketing",
        # A dor e a dependencia de boca a boca sem canal proprio de atracao, que e geracao de
        # demanda.
        "mensagem": (
            "meu escritorio de contabilidade so cresce por indicação. quando a indicação "
            "seca o mes morre, pq nao tem nada trazendo gente de fora pra dentro"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "ag_mkt_04",
        "categoria": "agente_marketing",
        # A dor e falta de reconhecimento em praca nova, resolvida por posicionamento e
        # divulgacao.
        "mensagem": (
            "abri a segunda unidade em outra cidade e la ninguem me conhece. na primeira "
            "era 10 ano de boca a boca, aqui to comecando do zero e o salão fica vazio de "
            "terça"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "ag_mkt_05",
        "categoria": "agente_marketing",
        # A dor e mensagem e conteudo que nao comunicam a oferta, nao volume de atendimento nem
        # processo interno.
        "mensagem": (
            "a gente ate tem foto boa dos produto, mas ninguem escreve nada junto. quem cai "
            "na pagina olha e vai embora sem entender o que a gente faz de verdade"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "ag_ope_01",
        "categoria": "agente_operacional",
        # A dor e tarefa repetitiva de transporte de dados feita a mao, sem envolver lead ou
        # cliente.
        "mensagem": (
            "toda segunda eu gasto umas 4h copiando as venda do sistema pra uma planilha "
            "pra mandar pro contador. e sempre a mesma coisa, todo santo mes"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "ag_ope_02",
        "categoria": "agente_operacional",
        # A dor e documento manual repetido com erro de digitacao, um gargalo de processo interno.
        "mensagem": (
            "meu juridico monta contrato um por um, muda so nome, cpf e valor. mes passado "
            "foi cpf trocado em dois e deu retrabalho pra caramba"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "ag_ope_03",
        "categoria": "agente_operacional",
        # A dor e montagem manual de documento consolidando fontes, tarefa operacional repetitiva.
        "mensagem": (
            "cada obra gera um relatorio que a engenheira monta na mao, juntando foto que "
            "chega no zap com a planilha de medição. leva o dia inteiro dela e ela deveria "
            "ta em campo"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "ag_ope_04",
        "categoria": "agente_operacional",
        # A dor e digitacao manual de documento em sistema, com erro decorrente do proprio
        # processo.
        "mensagem": (
            "recebo nota em pdf de uns 40 fornecedor por mes e alguem daqui digita item por "
            "item no erp. ja aconteceu de lançar quantidade errada e a gente so descobrir "
            "no inventario"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "ag_ope_05",
        "categoria": "agente_operacional",
        # A dor e retrabalho de cadastro duplicado entre sistemas, nao a venda em si que ja foi
        # fechada.
        "mensagem": (
            "toda vez que fecha um contrato alguem tem que cadastrar o mesmo cliente em 3 "
            "lugar diferente, e sempre esquecem um. dai o financeiro cobra errado"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    # ---- lote r6_: gabarito PENDENTE DE APROVAÇÃO HUMANA (ver # REVISAR) ----
    # Fora do portão de regressão até serem aprovados: gabarito não revisado
    # não serve de referência pra medir regressão.
    {
        "id": "r6_amb_01",
        "categoria": "agente_ambiguo",
        # ARBITRADO por Marcos: atendimento. Reverte a minha troca — o agente que RESOLVE a dor
        # e o de atendimento, ainda que a consequencia seja venda perdida.
        # regra
        # A dor descrita e mensagem que entra e fica sem resposta em tempo porque so uma pessoa
        # cobre o canal; a leitura comercial (lead perdido por demora) foi descartada porque nao
        # existe negociacao em andamento nem follow-up esquecido, a falha esta na primeira
        # resposta do canal, nao no acompanhamento da venda.
        "mensagem": (
            "sou eu sozinho no balcao da otica. chega uns 15 whats por dia perguntando "
            "preço de lente e eu so vou responder quando fecha a loja, as vez so no outro "
            "dia. metade ja nem responde mais quando eu volto"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_amb_02",
        "categoria": "agente_ambiguo",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A dor e a comunicacao que nao diz o que a empresa faz e por isso atrai o publico
        # errado, falha anterior ao contato; a leitura comercial (vendedor sem triagem, tempo de
        # funil desperdicado) foi descartada porque o vendedor esta atendendo todo mundo, o
        # defeito nasce na mensagem publicada e nao no processo de venda.
        "mensagem": (
            "invisto no insta e entra contato pra caramba, uns 30 por semana. so que 8 em "
            "cada 10 pergunta coisa que a gente nem faz, tipo conserto de celular, e aqui "
            "e montagem de computador. meu vendedor passa o dia inteiro conversando com "
            "quem nunca ia comprar"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "r6_amb_03",
        "categoria": "agente_ambiguo",
        # ARBITRADO por Marcos: atendimento mantido. Quem resolve o rastreio repetido e o agente
        # de atendimento.
        # A dor e a consulta manual recorrente em site e planilha que se repete a cada pedido; a
        # leitura de atendimento (mesma pergunta repetida, volume de mensagem) foi descartada
        # porque eles respondem todo mundo, o que trava e o trabalho de garimpar o dado, nao a
        # conversa em si.
        "mensagem": (
            "cliente manda msg perguntando onde ta o pedido umas 40 vez por dia. pra cada "
            "um a gente tem que abrir o site da transportadora, caçar o codigo na "
            "planilha de expedição e so dai voltar e responder. da uns 10 minuto cada um, "
            "ninguem aqui aguenta mais"
        ),
        "esperado": {"agente_indicado": "atendimento"},
        # fronteira: caçar código na planilha compete com a pergunta repetida
        "atrito": True,
    },
    {
        "id": "r6_amb_04",
        "categoria": "agente_ambiguo",
        # ARBITRADO por Marcos: marketing mantido. Quem resolve a montagem de post e o agente de
        # marketing.
        # regra
        # A dor e a montagem manual repetitiva de pecas a partir de dado que ja existe no
        # sistema; a leitura de marketing (postagem inconsistente, presenca fraca) foi
        # descartada porque parar de postar e consequencia do gargalo manual, e a regra manda
        # classificar pela causa, nao pelo efeito.
        "mensagem": (
            "sou de imobiliaria. todo mes eu pego as foto dos imovel novo, corto uma a "
            "uma, escrevo a legenda com metragem e valor copiando do sistema e monto uns "
            "40 post. some dois dia meu. mes que fica corrido eu simplesmente nao posto "
            "nada"
        ),
        "esperado": {"agente_indicado": "marketing"},
        # fronteira: montar 40 posts compete com a presença fraca
        "atrito": True,
    },
    {
        "id": "r6_amb_05",
        "categoria": "agente_ambiguo",
        # ARBITRADO por Marcos: indefinido mantido. Placar comparado sem prejuizo nao sustenta
        # implantar nenhum dos quatro.
        # O que ele traz e placar comparado com o concorrente e uma sensacao, sem nenhum
        # mecanismo de falha nem prejuizo descrito; a leitura de marketing (presenca digital
        # fraca) foi descartada porque numero de seguidor menor que o do vizinho e metrica, nao
        # dor, e ele mesmo diz que nao perdeu movimento.
        "mensagem": (
            "meu perfil da loja tem 312 seguidor e o do cara da esquina tem quase 9 mil. "
            "movimento aqui ta igual de sempre, nao caiu nada, mas fico com aquela "
            "sensação de que to ficando pra tras. voces olham isso?"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_amb_06",
        "categoria": "agente_ambiguo",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # critica: mecanismo identico a r6_com_01
        # A dor concreta e nao existir controle de quem esta no funil, com orcamento em aberto
        # orfao e sem ninguem sabendo se o cliente foi respondido; a leitura indefinido (evento
        # pontual de saida de funcionario, lead que admite nao saber o que quer) foi descartada
        # porque, apesar da duvida dele, ha fato concreto de negociacao aberta sem dono
        # declarado.
        "mensagem": (
            "meu unico vendedor pediu as conta semana passada e levou tudo na cabeça "
            "dele. tem orçamento em aberto que eu nao sei de quem e nem se alguem "
            "respondeu o cliente. sinceramente nao sei se preciso contratar outro ou se e "
            "outra coisa"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "r6_atd_01",
        "categoria": "agente_atendimento",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e mensagem de quem ja escreveu se perdendo entre canais dispersos, sem ninguem
        # saber o que ficou sem resposta.
        "mensagem": (
            "tenho uma escola de ingles com 2 unidade. o aluno manda no whats da unidade, "
            "outro chama no instagram, tem o email da secretaria e ainda aquele chat do "
            "site. ninguem sabe o que ja foi respondido e o que nao foi, semana passada "
            "uma mae cobrou 3 vez a mesma coisa em lugar diferente e ninguem tinha visto "
            "nenhuma"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_atd_02",
        "categoria": "agente_atendimento",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # critica: estrutura identica a ag_arm_01, que esta gravado como comercial
        # A dor e a janela noturna sem ninguem para responder quem escreveu, e o produto pedido
        # (trafego) vem sem nenhuma dor de marketing descrita.
        "mensagem": (
            "queria contratar trafego pago pra encher a baixa temporada da pousada. so "
            "que fui olhar aqui e a maioria dos pedido de reserva cai entre 21h e meia "
            "noite, quando a recepção ja fechou, e a gente so vai responder as 10h do "
            "outro dia. ai a pessoa responde que ja acertou em outro lugar"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_atd_03",
        "categoria": "agente_atendimento",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a mesma duvida basica repetida consumindo quem deveria estar em outra coisa,
        # ou seja, carga de resposta a quem escreveu.
        "mensagem": (
            "industria de embalagem plastica aqui. meu tecnico de aplicação, que e o cara "
            "que entende de verdade do produto, passa o dia inteiro no whats respondendo "
            "se tem no estoque, qual o prazo e qual o codigo da bobina. e sempre as "
            "mesmas 5 pergunta e ele nao consegue mais olhar o que e serio"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_atd_04",
        "categoria": "agente_atendimento",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a fila de mensagens parar de andar porque a resposta depende de uma unica
        # pessoa, deixando quem escreveu sem retorno.
        "mensagem": (
            "clinica veterinaria. quem responde mensagem aqui e so a Fabi da recepção. "
            "ela tirou 15 dia de ferias em junho e quando voltou tinha mais de 400 "
            "mensagem sem ler, teve tutor que perguntou de reforço de vacina e nunca teve "
            "resposta nenhuma. se ela falta um dia ja acumula tudo de novo"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_atd_05",
        "categoria": "agente_atendimento",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e o custo de ouvir e responder audio fazendo a fila de contatos ficar sem
        # retorno, o que e trato com quem escreveu.
        "mensagem": (
            "sou dono de uma distribuidora de autopeça. os mecanico mandam audio de 4, 5 "
            "minuto perguntando se a peça serve no carro tal, com barulho de oficina no "
            "fundo. ninguem aqui para pra ouvir aquilo no meio do expediente, ai acumula "
            "um monte de audio sem resposta e no outro dia o cara manda de novo "
            "perguntando se chegou a mensagem"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_atd_06",
        "categoria": "agente_atendimento",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A dor e o contexto da conversa se perder na troca de atendente, obrigando quem
        # escreveu a repetir tudo.
        "mensagem": (
            "loja de movel planejado. tenho 3 pessoa revezando no numero da loja, cada "
            "dia responde uma. dai o cliente tem que contar a historia inteira de novo, o "
            "que comprou, qual e o problema da porta, quem foi que montou. ja ouvi 'mas "
            "eu expliquei isso ontem pra outra moça' umas 10 vez so esse mes"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_atd_08",
        "categoria": "agente_atendimento",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A dor e o contato entrante que nao encontra ninguem para atender, um problema de
        # cobertura de atendimento e nao de acompanhamento de venda.
        "mensagem": (
            "tenho um auto center com 4 elevador. a operadora manda um relatorio e semana "
            "passada deu 34 ligação perdida em 5 dia util. ninguem consegue largar o "
            "carro no meio pra atender telefone e o povo nao deixa recado, liga, liga de "
            "novo e desiste. quem insiste chega aqui reclamando que nunca atendem"
        ),
        "esperado": {"agente_indicado": "atendimento"},
    },
    {
        "id": "r6_com_01",
        "categoria": "agente_comercial",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a carteira de negociacoes abertas que ficou orfa na saida do vendedor e
        # ninguem repassou, entao a oportunidade que existia morre parada.
        "mensagem": (
            "boa tarde. tenho uma distribuidora de peça agricola no interior. meu "
            "vendedor mais antigo pediu as conta semana retrasada e foi embora com tudo "
            "na agenda do celular dele. tinha uns 15 cliente negociando com ele, ninguem "
            "assumiu esse povo e ta tudo parado desde entao. dois ja compraram de outra "
            "distribuidora, fiquei sabendo por terceiro"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "r6_com_02",
        "categoria": "agente_comercial",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a ausencia de dono e de registro comum do funil, que gera contato duplicado de
        # um lado e oportunidade sem responsavel do outro.
        "mensagem": (
            "tenho uma loja de material de construção com 4 vendedor no balcão e cada um "
            "anota o orçamento no bloquinho dele. semana passada dois ligaram pro mesmo "
            "cliente oferecendo coisa diferente, o cara ficou puto. e teve um pedido de "
            "orçamento de porcelanato que simplesmente nao era de ninguem, ficou 10 dia "
            "sem sair porque cada um achou que era do outro"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "r6_com_03",
        "categoria": "agente_comercial",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # O produto pedido e midia paga, mas a dor descrita e a base de tratamentos aprovados
        # pela metade que nunca foi retomada, ou seja, venda existente nao trabalhada.
        "mensagem": (
            "queria contratar trafego pago pra trazer paciente novo pra clinica "
            "odontologica. mas assim, pensando aqui, tenho quase 2 mil paciente "
            "cadastrado no sistema, gente que fez tratamento em 2023, aprovou so a "
            "limpeza e o resto do plano ficou pela metade. nunca ninguem ligou pra nenhum "
            "desses pra oferecer o restante. e dinheiro parado ali dentro"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "r6_com_04",
        "categoria": "agente_comercial",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a renovacao com data conhecida que ninguem retoma a tempo, perdendo para o
        # concorrente uma venda que ja estava na mao.
        "mensagem": (
            "sou dono de uma corretora de seguro. a apolice vence e a gente so descobre "
            "quando o cliente liga falando que ja renovou com outro corretor. nao tem "
            "nada avisando que ta chegando o vencimento, é na memoria da minha secretaria "
            "mesmo. esse ano ja perdi umas 12 renovação assim, cliente antigo de 8 ano"
        ),
        "esperado": {"agente_indicado": "comercial"},
    },
    {
        "id": "r6_com_07",
        # ARBITRADO por Marcos: indefinido. O gargalo e a agenda do dono na
        # aprovacao de desconto — nenhum dos quatro agentes resolve isso.
        "categoria": "agente_comercial",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # critica: gargalo de alcada nao e nenhum dos quatro mecanismos
        # O produto pedido aponta atendimento e o proprio lead descarta a demora na resposta, a
        # dor real e a negociacao travada na aprovacao de desconto que perde a venda no
        # fechamento.
        "mensagem": (
            "queria um robo pra responder no whats mais rapido. mas sendo sincero a gente "
            "ja responde em uns 5 minuto, isso ai ta ok. o buraco é depois: e "
            "serralheria, pedido de portão e grade, quando o cliente pede desconto o "
            "vendedor tem que me mandar por email pra eu aprovar, eu levo uns 3 ou 4 dia "
            "pra olhar isso e quando eu volto o cara ja mandou fazer em outro lugar"
        ),
        "esperado": {"agente_indicado": "indefinido"},
        # fronteira: aprovação manual por e-mail compete com a venda travada
        "atrito": True,
    },
    {
        "id": "r6_com_08",
        "categoria": "agente_comercial",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A resposta ao contato ja acontece e e elogiada, o que falha e retomar o interessado
        # quando o produto chega, perdendo uma venda ja qualificada.
        "mensagem": (
            "loja de calçado. direto entra gente perguntando por numero que ta em falta e "
            "a menina responde certinho, fala que chega na semana seguinte, isso funciona "
            "bem. o problema e que quando a mercadoria chega ninguem avisa essas pessoa. "
            "a lista fica num caderno embaixo do balcão e vira mes com nome antigo. é "
            "venda na mao que passa batido toda semana"
        ),
        "esperado": {"agente_indicado": "comercial"},
        # fronteira: lista no caderno compete com a venda não retomada
        "atrito": True,
    },
    {
        "id": "r6_ind_01",
        "categoria": "agente_indefinido",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # Saudação com identificação de setor e agendamento de retorno, sem uma única frase
        # sobre o que está dando errado hoje.
        "mensagem": (
            "boa tarde, é aqui mesmo da empresa? achei o contato de vcs num grupo de "
            "whats de empresario aqui de campinas. tenho uma clinica veterinaria no "
            "cambui. tudo bem se eu chamar depois? agora to em consulta"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_ind_02",
        "categoria": "agente_indefinido",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # Só o placar (queda de 22%) e a cobrança do conselho, sem dizer onde o processo quebra
        # — resultado ruim não é mecanismo de dor.
        "mensagem": (
            "sou da diretoria de uma industria de embalagem plastica em joinville. "
            "fechamos o primeiro semestre 22% abaixo do mesmo periodo do ano passado e o "
            "conselho ta em cima de mim cobrando explicação. preciso de alguma coisa que "
            "vire esse jogo ainda esse ano. o que voces conseguem fazer?"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_ind_03",
        "categoria": "agente_indefinido",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # Nomeia um produto de comercial (CRM) por sugestão do contador e declara explicitamente
        # que não há nada dando errado, então rotular comercial seria inferir do produto.
        "mensagem": (
            "tenho uma transportadora pequena, 12 caminhão rodando entre sp e o sul. a "
            "coisa ta indo bem graças a deus, cliente fiel, agenda cheia o mes inteiro, "
            "nao tenho do que reclamar. meu contador comentou semana passada que empresa "
            "do meu porte ja devia ter um crm faz tempo e aquilo ficou na minha cabeça. "
            "voces mexem com isso? queria so entender o que muda na pratica"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_ind_04",
        "categoria": "agente_indefinido",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # Mensagem longa e cheia de contexto de negócio (histórico, porte, mix de canal,
        # sazonalidade, faturamento) que em nenhum momento descreve algo que se perde, se refaz
        # na mão ou não dá conta.
        "mensagem": (
            "boa noite. vou me apresentar direito pq acho que ajuda voces a entender. meu "
            "pai abriu a marcenaria em 1994 num galpão alugado em são bento do sul e hoje "
            "a gente tem 3 loja, 46 funcionario e fabrica propria de uns 2 mil metro. "
            "trabalhamos so com planejado sob medida, cozinha e dormitorio, ticket medio "
            "uns 38 mil, e nossa venda vem 70% de arquiteto que indica e 30% de quem "
            "entra na loja. dezembro e janeiro sao os mes forte, junho e o pior de todos, "
            "e ano passado a gente fechou 11 milhão de faturamento. to assumindo a "
            "empresa agora que meu pai se aposentou em marco e quero fazer as coisa do "
            "jeito certo desde o comeco. me falaram bem de voces. da pra marcar uma "
            "conversa pra voces me explicarem direitinho o que fazem?"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_ind_05",
        "categoria": "agente_indefinido",
        # ARBITRADO por Marcos: indefinido mantido. Nao descartado — r6_ind_07 testa outra
        # armadilha (sinal comercial forte sem dor), nao a mesma.
        # É um checklist de qualificação de fornecedor (case, LGPD, integração, prazo) — pedido
        # de informação puro, sem nenhuma falha operacional descrita.
        "mensagem": (
            "sou coordenadora pedagogica de uma escola de idiomas com 4 unidade. antes de "
            "eu levar isso pra mantenedora preciso saber algumas coisa: 1) voces ja "
            "atenderam instituição de ensino? tem case pra mostrar? 2) como fica a lgpd, "
            "a gente trabalha com dado de aluno menor de idade 3) integra com o sistema "
            "academico que usamos aqui, é o sponte 4) qual o prazo tipico de implantação. "
            "pode responder por aqui mesmo que eu compilo"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_ind_06",
        "categoria": "agente_indefinido",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # Desabafo sobre exaustão e horas trabalhadas sem nomear uma única tarefa, mensagem,
        # lead ou documento — não há mecanismo, só sintoma.
        "mensagem": (
            "cara vou ser sincero contigo, to no meu limite. abri o restaurante achando "
            "que ia ser uma coisa e é outra totalmente diferente. chego 7 da manha, saio "
            "meia noite, e mesmo assim tenho a sensação de que nada anda pra frente. "
            "minha esposa ja reclamou umas 3 vez esse mes. sei que preciso mudar alguma "
            "coisa aqui dentro mas nem sei te dizer por onde começar, so sei que do jeito "
            "que ta nao da mais"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_ind_07",
        "categoria": "agente_indefinido",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # Traz verba, prazo e poder de compra em detalhe, mas descreve apenas o rito de compra
        # da empresa — sinal comercial de qualificação não é dor descrita.
        "mensagem": (
            "Bom dia. Encaminho o contato conforme orientação da nossa diretoria. Somos "
            "uma rede de 14 farmácias no interior de Goiás, em operação desde 2007, hoje "
            "com aproximadamente 190 colaboradores e faturamento na casa dos 60 milhões "
            "ao ano. Fui designada responsável pela seleção de fornecedores do projeto "
            "previsto no orçamento de 2027, com verba já aprovada na ordem de 180 mil. O "
            "fluxo aqui funciona assim: recebo três propostas, monto o comparativo, levo "
            "ao comitê que se reúne toda última quinta-feira do mês e a decisão sai em "
            "até 45 dias. Preciso que a proposta venha com escopo detalhado, prazo de "
            "implantação e cláusula de SLA, e que chegue até o dia 20 para entrar nesta "
            "rodada. Fico à disposição."
        ),
        "esperado": {"agente_indicado": "indefinido"},
        # fronteira: montar o comparativo compete com o rito de compra
        "atrito": True,
    },
    {
        "id": "r6_ind_08",
        "categoria": "agente_indefinido",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A troca de fornecedor é por motivo pessoal do prestador e o lead nega explicitamente
        # insatisfação, então o serviço de marketing citado é só o produto em pauta, não uma
        # dor.
        "mensagem": (
            "meu contrato com a agencia que cuida da parte digital da otica vence em "
            "setembro e eu ja avisei que nao vou renovar. nao é que eles fizeram algo de "
            "errado nao, o socio de la mudou de cidade e ficou ruim pros dois lado. to "
            "pegando orçamento com umas 4 empresa pra ver quem assume dali pra frente. "
            "voces trabalham com esse tipo de contrato? como funciona o formato de voces?"
        ),
        "esperado": {"agente_indicado": "indefinido"},
    },
    {
        "id": "r6_mkt_01",
        "categoria": "agente_marketing",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a presenca digital defasada afastando quem procura o negocio antes de qualquer
        # contato.
        "mensagem": (
            "boa tarde. tenho um restaurante japones em santo andre. semana passada "
            "chegaram dois cliente falando que achavam que a gente tinha fechado, pq quem "
            "procura na internet acha o telefone antigo e um cardapio de 2021 com preço "
            "de antes da pandemia. mudamos de ponto faz um ano e isso nunca foi "
            "atualizado em lugar nenhum"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "r6_mkt_02",
        "categoria": "agente_marketing",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a campanha sem consistencia, que zera o alcance a cada parada, e nao a falta
        # de conteudo em si.
        "mensagem": (
            "tenho um estudio de pilates. eu me animo e posto todo dia por umas 3 semana, "
            "ai aparece gente perguntando, dai entra correria de aula e eu sumo 2, 3 mes. "
            "quando volto é do zero de novo, parece que ninguem lembra que existe. ja fiz "
            "esse liga desliga umas 4 vez so esse ano"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "r6_mkt_03",
        "categoria": "agente_marketing",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # critica: mesmo mecanismo de r6_mkt_07
        # A dor e nao existir onde o comprador procura, entao a empresa nem entra na lista de
        # opcoes.
        "mensagem": (
            "somos uma metalurgica pequena de peça sob medida, 22 ano de mercado. um "
            "comprador de industria grande me contou outro dia que procurou fornecedor na "
            "internet e nem achou a gente, achou 3 concorrente. o que a gente tem é o "
            "catalogo em pdf que o representante leva na pasta, fora isso a empresa nao "
            "existe em canal nenhum"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "r6_mkt_04",
        "categoria": "agente_marketing",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A dor e nao ter material de prova do proprio trabalho para circular, ou seja, nada a
        # mostrar.
        "mensagem": (
            "faço movel planejado ha 12 ano. termino a obra, entrego e vou embora, nunca "
            "parei pra registrar nada. ai quando alguem pede indicação no grupo do "
            "predio, meus cliente antigo falam bem mas nao tem uma foto pra mandar, e eu "
            "tbm nao tenho. quem mostra trabalho pronto leva o serviço"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "r6_mkt_06",
        "categoria": "agente_marketing",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A dor e o unico ativo digital do negocio estar vazio e afastar quem procura, mesmo o
        # produto pedido apontando para disparo comercial.
        "mensagem": (
            "queria um programa que dispara mensagem de revisão pros cliente antigo da "
            "oficina, pq de cliente novo eu ja desisti. meu sobrinho foi pesquisar aqui "
            "pra me mostrar e a auto center aparece no mapa com uma foto tremida de 2018, "
            "sem horario, sem serviço escrito, sem nada. ele falou que se fosse ele nem "
            "clicava"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "r6_mkt_07",
        "categoria": "agente_marketing",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e depender de um canal de terceiro sem nenhuma presenca propria por onde ser
        # encontrada.
        "mensagem": (
            "vendo roupa feminina, uns 90% do pedido vinha de um marketplace. esse mes "
            "eles mecheram em alguma coisa la e meu pedido caiu pela metade da noite pro "
            "dia. me toquei que fora daquele app eu nao existo: nao tenho perfil montado, "
            "nao tenho nada publicado, ninguem me acha se nao for por la"
        ),
        "esperado": {"agente_indicado": "marketing"},
    },
    {
        "id": "r6_ope_01",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # A dor e uma varredura de pesquisa recorrente feita a mao todo dia, nao falta de
        # demanda nem lead perdido.
        "mensagem": (
            "sou eng civil, tenho uma empresa pequena que faz obra pra prefeitura. todo "
            "dia de manha alguem aqui abre uns 12 portal de licitacao um por um, le "
            "edital por edital e anota numa planilha o que serve pra gente. isso come 3h "
            "por dia de uma pessoa e mesmo assim mes passado passou batido um que era a "
            "nossa cara"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "r6_ope_02",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e a montagem manual e semanal de um documento de escala, tarefa interna
        # repetitiva sem nenhuma conversa envolvida.
        "mensagem": (
            "tenho uma metalurgica com 62 operador em 3 turno. quem monta a escala sou "
            "eu, no papel mesmo, toda quinta a tarde, encaixando ferias, folga e quem ta "
            "de atestado. levo umas 5 hora e ainda sai errado, semana passada deixei o "
            "setor de solda sem ninguem no turno da noite"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "r6_ope_03",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e conferir duas fontes linha a linha na mao todo mes, trabalho administrativo
        # repetitivo e nao trato com quem escreveu pra empresa.
        "mensagem": (
            "clinica de oftalmo aqui. todo comeco de mes a menina do faturamento senta "
            "com o extrato do convenio de um lado e as guia do outro e vai batendo uma "
            "por uma pra ver o que eles cortaram. sao quase 900 guia, ela leva uns 4 dia "
            "nisso e sempre escapa alguma coisa"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "r6_ope_04",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e o recalculo manual em cascata de dezenas de fichas toda vez que um dado muda,
        # processo interno repetitivo.
        "mensagem": (
            "tenho 3 pizzaria. sempre que o fornecedor sobe o preco do queijo ou da "
            "farinha eu preciso refazer o custo de umas 80 ficha tecnica na calculadora "
            "pra saber se o preco do cardapio ainda se paga. faco isso num excel na mao e "
            "ja perdi domingo inteiro nessa brincadeira, e olha que preco sobe direto"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "r6_ope_05",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e triar e organizar arquivo por arquivo na mao, tarefa administrativa em volume,
        # com erro nascendo do proprio processo.
        "mensagem": (
            "laboratorio de analise clinica. os laudo saem do equipamento em pdf com nome "
            "tipo DOC00017, ai alguem tem que abrir um por um, ver de quem e, renomear e "
            "jogar na pasta certa. sao umas 400 por dia e ja aconteceu de laudo ir parar "
            "na pasta do paciente errado"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
    {
        "id": "r6_ope_06",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # O produto pedido e CRM, mas a dor descrita e a montagem manual de dossie documental
        # por venda, e o proprio lead descarta o esquecimento de cliente como problema.
        "mensagem": (
            "me falaram que eu precisava de um crm e vim atras. so que parando pra pensar "
            "o gargalo aqui nao e lembrar de cliente nao, isso a gente da conta. sou de "
            "uma concessionaria de maquina agricola e pra cada venda financiada alguem "
            "monta a pasta com 9 documento, escaneia tudo, preenche 2 formulario do banco "
            "e protocola. da quase 2h por venda, e a gente faz umas 30 no mes"
        ),
        "esperado": {"agente_indicado": "operacional"},
        # fronteira: CRM pedido compete com o dossiê montado à mão
        "atrito": True,
    },
    {
        "id": "r6_ope_07",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: media)
        # critica: repete ag_ope_01 + ag_ope_03
        # O produto pedido aponta marketing, mas a dor que o lead diz ser a pior e consolidar
        # relatorio manual toda semana, tarefa interna repetitiva.
        "mensagem": (
            "queria contratar uma social media pras 4 unidade da academia, ta tudo meio "
            "parado. mas confesso que o que me tira o sono e outra coisa: toda segunda eu "
            "peco no zap pra cada gerente o numero de matricula, cancelamento e "
            "inadimplencia, dai eu junto tudo num excel na mao pra levar na reuniao. "
            "sempre tem um que manda no formato errado e eu refaco do zero"
        ),
        "esperado": {"agente_indicado": "operacional"},
        # fronteira: social media pedida compete com o relatório manual
        "atrito": True,
    },
    {
        "id": "r6_ope_08",
        "categoria": "agente_operacional",
        # REVISAR — gabarito pendente de aprovacao humana (confianca do gerador: alta)
        # A dor e correcao e lancamento manual repetidos a cada ciclo, trabalho de processo
        # interno e nao conversa com aluno.
        "mensagem": (
            "tenho um cursinho pre vestibular. a cada 15 dia a gente aplica simulado de "
            "90 questao pra 400 aluno. os professor corrigem folha por folha com o "
            "gabarito na mao e depois alguem digita nota por nota no sistema pra sair o "
            "ranking. leva quase uma semana e quando o aluno ve o resultado ja nem lembra "
            "mais da prova"
        ),
        "esperado": {"agente_indicado": "operacional"},
    },
]
