"""
Dublês da Claude API — para os testes rodarem offline, de graça e sempre igual.
Claude API stand-ins — so tests run offline, free, and identical every time.
"""

import json
import logging


class BlocoTexto:
    type = "text"

    def __init__(self, text: str):
        self.text = text


class RespostaFalsa:
    def __init__(self, sinais: dict | None = None, stop_reason: str = "end_turn"):
        self.stop_reason = stop_reason
        self.content = [BlocoTexto(json.dumps(sinais))] if sinais is not None else []


class ClienteFalso:
    """Imita o anthropic.Anthropic() só no pedaço que usamos."""

    def __init__(
        self,
        resposta: RespostaFalsa | None = None,
        estoura: Exception | None = None,
    ):
        self._resposta = resposta
        self._estoura = estoura
        self.chamadas: list[dict] = []
        self.messages = self

    def create(self, **kwargs: object) -> RespostaFalsa | None:
        self.chamadas.append(kwargs)
        if self._estoura is not None:
            raise self._estoura
        return self._resposta


class MensagemOpenAIFalsa:
    def __init__(
        self,
        sinais: dict | None = None,
        refusal: str | None = None,
    ):
        self.content = json.dumps(sinais) if sinais is not None else None
        self.refusal = refusal


class EscolhaFalsa:
    def __init__(self, mensagem: MensagemOpenAIFalsa, finish_reason: str = "stop"):
        self.message = mensagem
        self.finish_reason = finish_reason


class RespostaOpenAIFalsa:
    def __init__(
        self,
        sinais: dict | None = None,
        refusal: str | None = None,
        finish_reason: str = "stop",
    ):
        self.choices = [EscolhaFalsa(MensagemOpenAIFalsa(sinais, refusal), finish_reason)]


class ClienteOpenAIFalso:
    """Imita o openai.OpenAI() só no pedaço que usamos: chat.completions.create."""

    def __init__(
        self,
        resposta: RespostaOpenAIFalsa | None = None,
        estoura: Exception | None = None,
    ):
        self._resposta = resposta
        self._estoura = estoura
        self.chamadas: list[dict] = []
        self.chat = self
        self.completions = self

    def create(self, **kwargs: object) -> RespostaOpenAIFalsa | None:
        self.chamadas.append(kwargs)
        if self._estoura is not None:
            raise self._estoura
        return self._resposta


# Sinais de exemplo, como a API os devolveria.
COMPRADOR = {
    "orcamento": True,
    "urgencia": True,
    "autoridade": False,
    "descadastro": False,
    "agente_indicado": "comercial",
    "resumo": "quer fechar identidade visual esta semana",
}
SAINDO = {
    "orcamento": False,
    "urgencia": False,
    "autoridade": False,
    "descadastro": True,
    "agente_indicado": "indefinido",
    "resumo": "pediu para sair da lista",
}
NEUTRO = {
    "orcamento": False,
    "urgencia": False,
    "autoridade": False,
    "descadastro": False,
    "agente_indicado": "indefinido",
    "resumo": "só perguntou o que a empresa faz",
}


def cliente_com(sinais: dict | None = None, estoura: Exception | None = None) -> ClienteFalso:
    return ClienteFalso(RespostaFalsa(sinais), estoura=estoura)


class CapturaDeLog:
    """
    Captura registros do LOGGER anexando um handler direto nele.
    Captures LOGGER records by attaching a handler to it directly.

    O `caplog` do pytest não serve aqui: ele depende de propagação para o root,
    e `core/log.py` define `propagate = False` de propósito, para a linha não
    sair duplicada quando a aplicação já configurou logging. A propagação
    desligada está certa em produção; quem se adapta é o teste.
    pytest's caplog relies on propagation, which production disables on purpose.
    """

    class _Coletor(logging.Handler):
        def __init__(self, destino: list[logging.LogRecord]) -> None:
            super().__init__()
            self._destino = destino

        def emit(self, record: logging.LogRecord) -> None:
            self._destino.append(record)

    def __init__(self) -> None:
        self.registros: list[logging.LogRecord] = []
        self._handler = self._Coletor(self.registros)

    def __enter__(self) -> "CapturaDeLog":
        from core.log import LOGGER

        LOGGER.addHandler(self._handler)
        LOGGER.setLevel(logging.INFO)
        return self

    def __exit__(self, *_: object) -> None:
        from core.log import LOGGER

        LOGGER.removeHandler(self._handler)

    def evento(self, nome: str) -> list[logging.LogRecord]:
        return [r for r in self.registros if r.getMessage() == nome]
