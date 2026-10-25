"""
Signal extraction via OpenAI — same job, same output shape, other provider.
Extração de sinais via OpenAI — mesmo trabalho, mesmo formato, outro provedor.

Prova prática do contrato de interface: troca-se o provedor por baixo e nada
acima precisa saber. O LeadTriageAgent não muda uma linha.
Proof of the interface contract: swap the provider underneath and nothing
above needs to know.

Reaproveita a INSTRUCAO e o ESQUEMA_SINAIS da versão Anthropic de propósito —
prompt diferente compararia prompts, não provedores.
"""

from typing import Any

import openai

from agents.lead_triage.signals import ESQUEMA_SINAIS, INSTRUCAO, _como_dicionario
from core.base_enricher import BaseEnricher

# Structured outputs em modo estrito exige um modelo que suporte json_schema.
MODELO = "gpt-4o"

MAX_TOKENS = 1024

# Teto por tentativa; ver a mesma constante em signals.py.
TIMEOUT_SEGUNDOS = 30.0


class MensagemEnricherOpenAI(BaseEnricher):
    """
    A mensagem do lead tratada como fonte, igual ao MensagemEnricher da Anthropic.
    Mesmo 'nome' de propósito: são intercambiáveis, e a régua de pesos do tenant
    não precisa saber qual provedor respondeu.
    """

    nome = "mensagem"

    def __init__(self, cliente: Any = None):
        # Costura para teste: em produção fica None e o SDK lê OPENAI_API_KEY
        # do ambiente sozinho. A chave nunca entra no código.
        # Test seam: None in production; the SDK reads OPENAI_API_KEY itself.
        self._cliente = cliente

    def buscar(self, pista: str) -> dict:
        """A 'pista' aqui é a própria mensagem do lead."""
        if not pista.strip():
            return self._vazio("mensagem vazia")

        cliente = self._cliente or openai.OpenAI(timeout=TIMEOUT_SEGUNDOS)

        resposta = cliente.chat.completions.create(
            model=MODELO,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": INSTRUCAO},
                {"role": "user", "content": pista},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "sinais_do_lead",
                    "strict": True,
                    "schema": ESQUEMA_SINAIS,
                },
            },
        )

        escolha = resposta.choices[0]
        mensagem = escolha.message

        # A recusa vem num campo próprio, não como erro. Ler .content direto
        # devolveria None e quebraria no json.loads uma linha abaixo.
        # The refusal arrives in its own field, not as an error.
        recusa = getattr(mensagem, "refusal", None)
        if recusa:
            return self._vazio(f"o modelo recusou analisar esta mensagem: {recusa}")

        # Resposta cortada no meio produz JSON inválido — melhor dizer isso
        # do que estourar um JSONDecodeError sem explicação.
        if escolha.finish_reason == "length":
            return self._vazio("a resposta passou do teto de tokens e veio cortada")

        conteudo = mensagem.content
        if not conteudo:
            return self._vazio(f"o modelo não devolveu conteúdo ({escolha.finish_reason})")

        return self._ok(_como_dicionario(conteudo))
