# ADR-0007 — Auto-autorização de requisição é permitida, mas nunca automática

## Status

Aceita

## Contexto

Todo usuário ativo é solicitante (USR-02), inclusive o chefe de setor. Quando o chefe é o beneficiário da própria requisição, o autorizador — "chefe do setor do beneficiário" (PER-03, TR-008) — é ele mesmo.

A estrutura organizacional documentada é plana: setores com um chefe cada, o setor Almoxarifado, e o superusuário técnico. Não há hierarquia acima do chefe de setor, e o Almoxarifado não autoriza outros setores. Logo não existe um aprovador alternativo natural para a requisição do próprio chefe.

Proibir a auto-autorização criaria um beco sem saída para as requisições do chefe; escalar para o superusuário tornaria um papel técnico (ADR-0001) um ator operacional recorrente.

## Decisão

A auto-autorização é permitida: o chefe pode autorizar a requisição em que ele é o beneficiário.

A auto-autorização nunca é automática. O envio para autorização (TR-005) sempre deixa a requisição em `aguardando_autorizacao`. O chefe precisa executar explicitamente a transição de autorização (TR-008) para a requisição entrar na fila do Almoxarifado.

Envio e autorização são sempre eventos de timeline separados.

Quando, na autorização, `ator == beneficiario`, o evento de timeline de autorização registra `metadata["auto_autorizacao"] = true`.

## Consequências

Requisições do chefe de setor não ficam bloqueadas por falta de aprovador.

Não há transição que combine envio e autorização; mesmo na auto-autorização são dois passos explícitos e dois eventos.

A auto-autorização é auditável: o evento carrega `ator == beneficiario` e a flag `metadata.auto_autorizacao`. Relatórios e revisões de controle podem filtrar por essa flag.

A policy de autorização não rejeita `ator == beneficiario`; apenas exige que o ator seja o chefe do setor do beneficiário.

## Trade-off

Aceita-se uma fraqueza de segregação de funções — o chefe aprova o próprio pedido — porque a organização não tem um aprovador acima dele e inventar esse papel está fora de escopo. A mitigação é tornar a auto-autorização explícita (nunca automática) e auditável (flag na timeline), em vez de escondê-la.
