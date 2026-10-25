# Histórico das medições

Cada arquivo aqui é o resumo de uma rodada da suíte, gravado com
`python3 -m evals.rodar --registrar`.

Existe por um motivo: sem ele, as taxas do portão viviam em `/tmp` e sumiam
com a sessão. O que restava era a palavra de quem reportou — exatamente o que
este projeto não aceita em nenhum outro lugar.

O nome do arquivo é `<data>-<instrucao_sha>.json`. O `instrucao_sha` são os 12
primeiros dígitos do SHA-256 do texto da `INSTRUCAO` que produziu aqueles
números. Não é o commit do git: instrução pode mudar sem commit, e aí o
registro mentiria. O hash do próprio texto é reproduzível por qualquer um:

```bash
python3 -c "
from agents.lead_triage.signals import INSTRUCAO
from evals.comparar import impressao_da_instrucao
print(impressao_da_instrucao(INSTRUCAO))"
```

Se o número bater com o do arquivo, aquelas taxas foram medidas com esta
instrução. Se não bater, o texto mudou desde então e as taxas são de outra
coisa.

Cada registro traz: data, provedor, total de casos, quantos passaram, taxa por
campo, taxa separada entre `atrito` e `demais`, e a lista completa de
divergências com id, campo, esperado e devolvido.
