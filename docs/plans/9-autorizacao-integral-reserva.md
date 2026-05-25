# Plano: Autorizar integralmente e reservar estoque (#9)

## Scope

**Inclui:**
- Policy `pode_autorizar_requisicao(ator, requisicao)` + `exigir_pode_autorizar_requisicao` em `apps/requisicoes/policies.py`, seguindo o chefe do setor do beneficiário e `superuser` como atores permitidos.
- Transição declarativa em `apps/requisicoes/transitions.py`: `aguardando_autorizacao -> autorizada`.
- Service `autorizar_requisicao(*, ator_id, requisicao_id)` em `apps/requisicoes/services.py`:
  - trava `Requisicao` sob `select_for_update`;
  - revalida estado e permissão sob lock;
  - confirma autorização integral (`quantidade_autorizada = quantidade_solicitada` para todos os itens);
  - delega a reserva de saldo a `apps/estoque/services.py`;
  - registra `TimelineRequisicao` com evento `autorizacao_total`;
  - inclui `metadata["auto_autorizacao"] = true` quando `ator_id == beneficiario_id`.
- Helper de estoque em `apps/estoque/services.py` para reservar saldo sem baixa física, com lock determinístico em `SaldoEstoque` e falha sem efeitos parciais quando houver material inativo, divergência crítica ou saldo insuficiente.
- View POST `autorizar_requisicao_view` em `apps/requisicoes/views.py`, com PRG/HX-Redirect e tradução de `PermissaoNegada`, `EstadoInvalido`, `DadosInvalidos` e `ConflitoDominio`.
- URL nova `requisicoes/<int:pk>/autorizar/`.
- UI do detalhe:
  - botão `Autorizar` no bloco de decisão quando a ação é permitida;
  - botão da fila de autorização renomeado para `Analisar`, alinhado ao brief;
  - sem novos componentes globais nesta slice.
- Testes por camada:
  - `test_policies.py` para permissão de autorização e auto-autorização permitida;
  - `test_services.py` para caminho feliz, permissão negada, estado inválido, saldo insuficiente/estático e metadata de auto-autorização;
  - `test_views.py` para contrato HTTP, botão no detalhe e redirect/HTMX.

**Não inclui:**
- Cancelamento pós-autorização, separação para retirada, atendimento, devolução e estorno.
- Modal global de confirmação.
- Novos filtros, paginação ou polling nas filas.
- Mudanças de schema/model.

## Files Touched

| Arquivo | Operação |
|---|---|
| `apps/requisicoes/transitions.py` | Declarar `aguardando_autorizacao -> autorizada` |
| `apps/requisicoes/policies.py` | `pode_autorizar_requisicao` e `exigir_pode_autorizar_requisicao` |
| `apps/estoque/services.py` | Novo helper de reserva de saldo sob lock determinístico |
| `apps/requisicoes/services.py` | `autorizar_requisicao` e integração com reserva de estoque |
| `apps/requisicoes/views.py` | `autorizar_requisicao_view`, flags de contexto do detalhe |
| `apps/requisicoes/urls.py` | Rota `<int:pk>/autorizar/` |
| `apps/requisicoes/templates/requisicoes/detalhe.html` | Botão `Autorizar` no bloco de decisão |
| `apps/requisicoes/templates/requisicoes/fila_autorizacao.html` | Label da ação `Analisar` |
| `apps/requisicoes/tests/test_policies.py` | Cobertura de permissão e auto-autorização |
| `apps/requisicoes/tests/test_services.py` | Cobertura da transição, reserva, timeline e falhas |
| `apps/requisicoes/tests/test_views.py` | Cobertura do POST, HTMX, permissão e renderização do botão |

## UX Direction

Direção: **Pragmatic Minimal / Accessible & Ethical**. A tela segue o layout operacional já estabelecido.

Regras aplicadas:
- A ação primária no detalhe é explícita: `Autorizar`.
- A fila continua triagem; apenas o rótulo da ação muda para `Analisar`.
- Formulário de autorização é POST direto, sem modal e sem input extra.
- Estado de sucesso/erro volta pelo chrome padrão com `messages` e `HX-Redirect` quando aplicável.
- Contraste e foco seguem os padrões já usados no resto do módulo.

## Implementation Order

1. RED policies + transitions: permissão e nova transição declarativa.
2. RED services: autorização feliz, permissão negada, estado inválido, saldo insuficiente, auto-autorização auditável.
3. GREEN estoque + requisições services: reserva integral sem baixa física.
4. RED views/urls/templates: botão no detalhe, label da fila e POST da autorização.
5. GREEN views/templates.
6. Revisão a11y/UX.
7. `rtk make test`.

## Test Strategy

### Policies
- Chefe do setor do beneficiário pode autorizar.
- Chefe de setor de outro setor não pode autorizar.
- Chefe de Almoxarifado só autoriza setor Almoxarifado.
- `superuser` pode autorizar qualquer requisição visível.

### Services
- Autorização aplica `aguardando_autorizacao -> autorizada`.
- Todos os itens recebem `quantidade_autorizada = quantidade_solicitada`.
- Reserva aumenta `saldo_reservado` e mantém `saldo_fisico`.
- Timeline registra `autorizacao_total`.
- `metadata["auto_autorizacao"] = true` quando ator é beneficiário.
- Permissão negada lança `PermissaoNegada`.
- Estado inválido lança `EstadoInvalido`.
- Saldo insuficiente, material inativo ou divergência crítica lançam exceção de domínio sem escrita parcial.

### Views
- GET do detalhe sem login redireciona.
- POST de autorização sem login redireciona.
- POST por ator sem permissão retorna 403.
- POST válido redireciona para detalhe atualizado e mostra mensagem.
- HTMX devolve `204` com `HX-Redirect`.
- O detalhe renderiza o botão `Autorizar` apenas para quem pode agir.
- A fila de autorização renderiza a ação `Analisar`.

## Invariants

- ADR-0005: `Requisicao` travada com `select_for_update`; estoque travado depois, em ordem determinística.
- ADR-0006: autorização integral, sem parcialidade por item.
- ADR-0007: auto-autorização permitida e auditada com `metadata.auto_autorizacao`.
- ADR-0011: service keyword-only, IDs na borda, policies compartilhadas, exceções de domínio explícitas.
- EST-06: saldo só muda via `estoque.services`, com lock e transação.
- TR-008: autorização é integral, com reserva completa e sem baixa física.
- TR-010: autorização parcial, zero, material inativo, divergência crítica ou saldo insuficiente bloqueiam a transição.

## Risks

- **Reserva em múltiplos saldos do mesmo material:** o código atual opera com estoque principal único; se houver mais de um `SaldoEstoque` por material, a política de seleção precisa ficar determinística e documentada.
- **Sem efeitos parciais:** qualquer falha depois de travar saldo precisa abortar antes de persistir `quantidade_autorizada` ou `saldo_reservado`.
- **Auto-autorização:** a flag da timeline só vale quando `ator == beneficiario`; não confundir com criador.
- **UI sem modal:** botão direto precisa de texto claro e feedback visual pós-POST para manter a operação legível.
