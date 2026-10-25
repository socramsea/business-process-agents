"""
Evolution API client — reads WhatsApp messages. Does not classify anything.
Cliente da Evolution API — lê mensagens do WhatsApp. Não classifica nada.

ESTE MÓDULO NÃO FOI VALIDADO CONTRA INSTÂNCIA REAL. O contrato abaixo vem da
documentação e de SDK de terceiro, não de observação:
  POST /chat/findMessages/{instancia}   header `apikey`
  corpo   {"where": {"key": {"remoteJid": "..."}}}
  registro  key.remoteJid · key.fromMe · key.id · pushName
            message.conversation · messageTimestamp
Fontes: doc.evolution-api.com, github.com/gusnips/evolution-api-sdk

THIS MODULE HAS NOT BEEN VALIDATED AGAINST A LIVE INSTANCE. Contract from docs.

Duas incertezas conhecidas, e por isso o código tolera as duas:
1. O envelope da resposta. As fontes divergem entre lista nua e
   {"messages": {"records": [...]}}. `_registros` aceita as duas formas.
2. Se `where` pode ser omitido para trazer todas as conversas. A issue #1632
   relata o filtro remoteJid falhando em algumas versões.

Use `bruto()` na primeira chamada com credencial real: ele devolve o JSON sem
interpretação. É assim que o formato de verdade aparece, em vez de eu adivinhar.
Use `bruto()` on the first real call — it returns raw JSON, no interpretation.
"""

from typing import Any

import httpx

from core import config

TIMEOUT_SEGUNDOS = 15.0


class Evolution:
    """Leitura apenas. Enviar mensagem não faz parte desta etapa."""

    def __init__(
        self,
        url: str | None = None,
        chave: str | None = None,
        instancia: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ):
        # Config vem do ambiente por core.config, igual a todo o resto: nada no
        # código, e um lugar só que sabe ler variável.
        self._url: str = (url or config.ler("EVOLUTION_URL")).rstrip("/")
        self._chave: str = chave or config.ler("EVOLUTION_API_KEY")
        self._instancia: str = instancia or config.ler("EVOLUTION_INSTANCE")
        # Costura para teste, mesmo padrão do SiteEnricher.
        self._transport = transport

    def _cliente(self) -> httpx.Client:
        # Reclama de tudo que falta de uma vez, e antes de abrir socket: erro de
        # configuração não deve chegar disfarçado de erro de rede.
        config.exigir(
            EVOLUTION_URL=self._url,
            EVOLUTION_API_KEY=self._chave,
            EVOLUTION_INSTANCE=self._instancia,
        )
        return httpx.Client(
            base_url=self._url,
            headers={"apikey": self._chave, "Content-Type": "application/json"},
            timeout=TIMEOUT_SEGUNDOS,
            transport=self._transport,
        )

    def bruto(self, remote_jid: str | None = None) -> Any:
        """
        Devolve o JSON como veio, sem interpretar. Existe para descobrir o
        formato real na primeira chamada com credencial.
        Returns raw JSON — exists to discover the real shape.
        """
        corpo: dict[str, Any] = {"where": {}}
        if remote_jid:
            corpo = {"where": {"key": {"remoteJid": remote_jid}}}

        with self._cliente() as c:
            resposta = c.post(f"/chat/findMessages/{self._instancia}", json=corpo)
            resposta.raise_for_status()
            return resposta.json()

    def mensagens(self, remote_jid: str | None = None) -> list[dict[str, Any]]:
        """
        Mensagens recebidas, já normalizadas. Ignora as que a própria conta
        enviou — `fromMe` verdadeiro é resposta nossa, não mensagem de lead.
        Incoming messages, normalized. Skips our own (`fromMe`).
        """
        recebidas = []

        for registro in _registros(self.bruto(remote_jid)):
            normalizada = _normalizar(registro)
            if normalizada is not None:
                recebidas.append(normalizada)

        return recebidas


def _registros(carga: Any) -> list[dict[str, Any]]:
    """
    Extrai a lista de registros. Aceita lista nua e envelope aninhado porque
    as fontes divergem e eu não pude verificar qual é a desta versão.
    Accepts both bare list and nested envelope — sources disagree.
    """
    if isinstance(carga, list):
        return [r for r in carga if isinstance(r, dict)]

    if isinstance(carga, dict):
        for caminho in (("messages", "records"), ("messages",), ("records",)):
            no: Any = carga
            for chave in caminho:
                no = no.get(chave) if isinstance(no, dict) else None
            if isinstance(no, list):
                return [r for r in no if isinstance(r, dict)]

    return []


def _normalizar(registro: dict[str, Any]) -> dict[str, Any] | None:
    """
    Um registro da Evolution vira o mínimo que o pipeline usa.
    Devolve None quando o registro não é mensagem de texto recebida.
    Returns None when the record is not an incoming text message.
    """
    chave = registro.get("key")
    if not isinstance(chave, dict) or chave.get("fromMe"):
        return None

    conteudo = registro.get("message")
    texto = conteudo.get("conversation") if isinstance(conteudo, dict) else None
    if not isinstance(texto, str) or not texto.strip():
        # Áudio, imagem e figurinha caem aqui. O pipeline hoje só lê texto;
        # descartar é honesto, inventar transcrição não seria.
        return None

    remoto = chave.get("remoteJid")
    return {
        "id": chave.get("id"),
        # remoteJid vem como "5511999990000@s.whatsapp.net"; o telefone é a
        # parte antes da arroba, e é ele que vira lead_id.
        "telefone": str(remoto).split("@")[0] if remoto else None,
        "remote_jid": remoto,
        "texto": texto,
        "nome": registro.get("pushName"),
        "quando": registro.get("messageTimestamp"),
    }
