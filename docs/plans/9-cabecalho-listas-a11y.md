# Plano — Issue #9: Cabeçalho, Colunas de Data, Botão Primário, A11y Messages (Batch D)

## Scope

O que muda:
- `apps/requisicoes/selectors.py` — anotar `fila_autorizacao` com `enviada_em`, `fila_atendimento` com `autorizada_em`
- `apps/requisicoes/views.py` — `_detalhe_context` expõe `enviada_em`
- `apps/requisicoes/templates/requisicoes/detalhe.html` — título/h1 sem pk, campo "Enviada em" no cabeçalho, botão primário azul em `pronta_para_retirada`
- `apps/requisicoes/templates/requisicoes/fila_autorizacao.html` — coluna "Enviada em"
- `apps/requisicoes/templates/requisicoes/fila_atendimento.html` — coluna "Autorizada em"
- `apps/core/templates/core/partials/_messages.html` — `aria-live` em containers separados
- `apps/requisicoes/templates/requisicoes/atender_retirada.html` — indicador de obrigatório no campo Retirante
- `apps/requisicoes/tests/test_views.py` — novos testes

O que NÃO muda:
- models (sem campo novo; usa timeline existente)
- services, policies, forms (retirante já obrigatório)
- URLs

## Files Touched

| Arquivo | Mudança |
|---------|---------|
| `selectors.py` | Subquery `enviada_em` / `autorizada_em` nas filas |
| `views.py` | `_detalhe_context` adiciona `enviada_em` dos eventos carregados |
| `detalhe.html` | P3-01 (título sem pk), P2-03 (Enviada em), P2-10 (botão azul) |
| `fila_autorizacao.html` | P2-04 rótulo e dado |
| `fila_atendimento.html` | P2-04 rótulo e dado |
| `_messages.html` | dois containers `aria-live` |
| `atender_retirada.html` | asterisco obrigatório no Retirante |
| `test_views.py` | testes de regressão + novos |

## Test Strategy

- Detalhe "Enviada em" visível em `aguardando_autorizacao`; ausente em `rascunho`
- Fila autorização: label "Enviada em" presente no HTML
- Fila atendimento: label "Autorizada em" presente no HTML
- `_messages.html`: containers `aria-live="polite"` e `aria-live="assertive"` renderizados corretamente

## Invariants

Nenhuma transição de estado. Nenhuma mutação de saldo. Apenas leitura e apresentação.

## Risks

- Subquery `enviada_em` pode ser `None` se evento `ENVIO_AUTORIZACAO` não existe (estado `aguardando_autorizacao` sempre tem, mas defensive)
- Ordenação das filas: manter `atualizado_em` como critério primário de ordenação (não mudar para `enviada_em`)
