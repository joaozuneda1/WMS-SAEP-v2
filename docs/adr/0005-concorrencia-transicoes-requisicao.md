# ADR-0005 — Modelo de concorrência das transições de requisição

## Status

Aceita

## Contexto

A documentação de estados (`docs/estado-transicoes-requisicao.md` §2) exigia lock pessimista apenas para mudanças de saldo/reserva. As transições de estado sem estoque — envio para autorização, retorno para rascunho, recusa, cancelamento — não tinham regra de concorrência.

Isso permite corridas: dois atores transicionando a mesma requisição em paralelo leem o mesmo estado de origem, ambos validam e ambos gravam. Exemplo: autorizar e cancelar simultâneos deixam a requisição em estado inconsistente e a reserva criada pela autorização órfã numa requisição cancelada.

## Decisão

Toda transição de estado de `Requisicao` é executada por um service dentro de `transaction.atomic`.

O service recebe `requisicao_id` — não uma instância já carregada —, busca a `Requisicao` com `select_for_update` e revalida o estado de origem sob lock antes de aplicar qualquer efeito.

A regra vale para todas as transições, inclusive as que não tocam estoque.

Quando a transição também muda estoque, a ordem de aquisição de locks é:

1. `Requisicao`;
2. `SaldoEstoque` afetados, em ordem crescente de `(estoque_id, material_id, id)`.

Eventos de timeline e efeitos de estoque são persistidos na mesma transação da mudança de estado. Notificações são disparadas somente via `transaction.on_commit`.

Adota-se lock pessimista uniforme (`select_for_update`). Não há controle otimista com campo de versão nesta fase.

## Consequências

Nenhuma transição de estado lê ou grava `Requisicao` fora de `transaction.atomic` + `select_for_update`.

Services de transição não aceitam instância de `Requisicao` como entrada; recebem `requisicao_id` e recarregam sob lock.

A ordem fixa de locks (`Requisicao` antes de `SaldoEstoque`, e `SaldoEstoque` por `(estoque_id, material_id, id)`) previne deadlock entre transações concorrentes.

Timeline e movimentação de estoque nunca ficam dessincronizadas do estado: ou tudo commita, ou nada.

Notificação que falhe não desfaz a transição.

Não existe campo `versao` em `Requisicao`; reintroduzir controle otimista exigiria nova ADR.

## Trade-off

Lock pessimista serializa transições concorrentes sobre a mesma requisição e exige disciplina: sempre recarregar sob lock, nunca usar instância stale. Aceita-se isso em troca de consistência forte e uniforme com o modelo de estoque (EST-06), sem a complexidade de retry do controle otimista.
