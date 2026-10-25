"""
Lead triage agent — the first concrete agent built on the shared base.
Agente de triagem de lead — o primeiro agente concreto sobre a base compartilhada.
"""

from datetime import datetime, timezone
from typing import Any

from agents.lead_triage.acumulo import acumular, agentes_distintos
from agents.lead_triage.escalada import decidir_escalada
from agents.lead_triage.scoring import classificar_lead, pontuar_enriquecimento
from agents.lead_triage.signals import MensagemEnricher, pontuar_sinais
from core.base_agent import BaseAgent
from core.base_enricher import enriquecer
from core.log import LOGGER, registro_da_decisao
from core.memoria import MemoriaEmMemoria, MemoriaLead

# Régua e pesos ficam aqui por enquanto; vêm da config do tenant depois.
# Thresholds and weights live here for now; they'll come from tenant config.
REGUA_PADRAO = {"quente": 70, "morno": 40}

PESOS_PADRAO = {
    "empresa": {"site": 25, "youtube": 15, "github": 10},
    "pessoa": {"github": 25, "youtube": 20, "site": 10},
}

# Peso negativo é proposital: quem pede pra sair da lista não pode pontuar,
# por mais bonito que seja o site da empresa.
PESOS_SINAIS = {
    "orcamento": 25,
    "urgencia": 20,
    "autoridade": 15,
    "descadastro": -100,
}


class LeadTriageAgent(BaseAgent):
    """Recebe uma mensagem do lead e devolve a classificação quente/morno/frio."""

    def __init__(
        self,
        tenant_id: str,
        cliente: Any = None,
        memoria: MemoriaLead | None = None,
    ):
        super().__init__(tenant_id)
        # Costura para teste: repassada ao MensagemEnricher.
        # Test seam: handed down to MensagemEnricher.
        self._cliente = cliente
        # Sem memória explícita, guarda no processo. Some quando o processo
        # morre — o que é honesto: some, não finge que persistiu.
        self._memoria = memoria if memoria is not None else MemoriaEmMemoria()

    def handle(
        self,
        message: str,
        lead_id: str,
        enriquecimento: list[dict] | None = None,
        tipo_lead: str = "empresa",
        quando: str | None = None,
    ) -> dict:
        """
        Cumpre o contrato da base: entra mensagem + lead_id, sai resultado padronizado.
        Fulfills the base contract: message + lead_id in, standard result out.

        A nota soma duas origens: o que a pessoa DISSE (sinais acumulados de
        TODAS as mensagens dela) e o que ela É (enriquecimento).

        `quando` entra por parâmetro para o teste não depender do relógio da
        máquina. Em produção fica None e vale o instante da chamada.
        """
        agora = quando or datetime.now(timezone.utc).isoformat(timespec="seconds")

        pontos_ext, obs_ext = pontuar_enriquecimento(
            enriquecimento or [], tipo_lead, PESOS_PADRAO
        )

        # enriquecer() envolve a chamada em try/except: LLM fora do ar vira
        # status 'falha' e o lead continua sendo atendido.
        resultado_msg = enriquecer(message, [MensagemEnricher(cliente=self._cliente)])[0]

        # Funde com o que o lead já disse antes. A nota é do relacionamento:
        # sem isto, cada mensagem apagava a anterior e lead que conversa mais
        # era entendido pior.
        anterior = self._memoria.carregar(self.tenant_id, lead_id)
        estado = acumular(anterior, resultado_msg.get("dados") or {}, agora)
        self._memoria.salvar(self.tenant_id, lead_id, estado)

        # A nota vem do ACUMULADO, com o resumo desta mensagem junto — é ele
        # que o vendedor lê. Status forçado a 'ok' de propósito: sinal já
        # guardado é fato, e falha na extração de agora não apaga o que o lead
        # disse na semana passada.
        dados = dict(estado["sinais"])
        resumo = (resultado_msg.get("dados") or {}).get("resumo")
        if resumo:
            dados["resumo"] = resumo

        pontos_msg, obs_msg = pontuar_sinais(
            {"fonte": "mensagem", "status": "ok", "dados": dados, "detalhe": None},
            PESOS_SINAIS,
        )

        # Mas a falha desta mensagem ainda precisa aparecer para o vendedor.
        if resultado_msg["status"] != "ok":
            _, obs_falha = pontuar_sinais(resultado_msg, PESOS_SINAIS)
            obs_msg = obs_falha + obs_msg

        pontos = max(pontos_ext + pontos_msg, 0)

        resultado = {
            "lead_id": lead_id,
            "pontos": pontos,
            "classificacao": classificar_lead(pontos, REGUA_PADRAO),
            "observacoes": obs_msg + obs_ext,
            "mensagens": estado["mensagens"],
            "agente_indicado": estado["agente_indicado"],
            "agentes_vistos": agentes_distintos(estado),
        }

        escalar, motivo = decidir_escalada(resultado, estado, resultado_msg["status"])
        resultado["escalar"] = escalar
        resultado["motivo_escalada"] = motivo

        # Uma linha por decisão, com o status de cada fonte. Sem isto, falha às
        # 3h da manhã some: o lead é atendido, a observação é gerada, e ninguém
        # fica sabendo.
        fontes = [resultado_msg, *(enriquecimento or [])]
        LOGGER.info(
            "lead classificado",
            extra=registro_da_decisao(self.tenant_id, lead_id, resultado, fontes),
        )

        return resultado
