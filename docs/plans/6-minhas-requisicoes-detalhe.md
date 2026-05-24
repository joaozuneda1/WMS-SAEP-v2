# Plano: Minhas requisições e detalhe com timeline (#6)

## Scope

**Inclui:**
- Selector `requisicoes_visiveis_para(ator_id)` — fonte única da matriz de visibilidade por papel.
- Selector `minhas_requisicoes(ator_id)` — subconjunto (criador OR beneficiário, sem rascunhos de terceiros), ordenado por `-criado_em`.
- View `minhas_requisicoes_view` em `/requisicoes/minhas/` (GET only) — lista com badge de estado, número público (fallback "Rascunho"), beneficiário, data, link "Ver".
- View `detalhe_requisicao_view` em `/requisicoes/<int:pk>/` (GET only) — cabeçalho, itens, timeline. `404` se fora do escopo de visibilidade (ADR-0010).
- Templates: `lista_minhas.html`, `detalhe.html`, partials `_estado_badge.html` e `_timeline.html`.
- Testes: `test_selectors.py` (visibilidade por papel), `test_views.py` (GET sem login → 302; autorizado → 200; fora de escopo → 404).

**Não inclui:**
- Top nav, layout `base_auth.html`, redirect pós-login (issue separada).
- `fila_autorizacao` / `fila_atendimento` selectors e views (issues separadas).
- Componentes globais `button.html`, `form_field.html`, `status_badge.html`, `modal.html` (issues separadas).
- Ações de transição (autorizar, recusar, cancelar, enviar) e modais — fora do MVP desta issue.
- Página de atendimento (`/requisicoes/<pk>/atender/`).

## Files Touched

| Arquivo | Operação |
|---|---|
| `apps/requisicoes/selectors.py` | Adicionar `requisicoes_visiveis_para` e `minhas_requisicoes` |
| `apps/requisicoes/urls.py` | Rotas `minhas/` e `<int:pk>/` |
| `apps/requisicoes/views.py` | `minhas_requisicoes_view`, `detalhe_requisicao_view` |
| `apps/requisicoes/templates/requisicoes/lista_minhas.html` | Criar |
| `apps/requisicoes/templates/requisicoes/detalhe.html` | Criar |
| `apps/requisicoes/templates/requisicoes/partials/_estado_badge.html` | Criar |
| `apps/requisicoes/templates/requisicoes/partials/_timeline.html` | Criar |
| `apps/requisicoes/tests/test_selectors.py` | Adicionar cobertura de visibilidade |
| `apps/requisicoes/tests/test_views.py` | Adicionar testes de GET lista e detalhe |

## Implementation Order

1. `selectors.py` — `requisicoes_visiveis_para` + `minhas_requisicoes`.
2. `tests/test_selectors.py` — papéis × escopo × estado.
3. `urls.py` — registrar rotas.
4. `views.py` — `minhas_requisicoes_view`, `detalhe_requisicao_view`.
5. Templates + partials.
6. `tests/test_views.py` — sem login, autorizado, fora de escopo (404), beneficiário em rascunho de terceiro (404).

## Visibility Matrix (fonte: `docs/matriz-permissoes.md` §5)

- Criador → sempre vê.
- Beneficiário → vê fora de `rascunho`.
- Chefe de setor não-almox → vê requisições do setor chefiado, exceto rascunhos de terceiros.
- Auxiliar de setor não-almox → vê requisições do setor (a matriz cita "chefe de setor", mas a hierarquia da policy de criação já trata auxiliar como mesmo escopo de leitura — confirmar; conservador: aux NÃO vê setor inteiro, apenas próprias).
- Auxiliar/Chefe de almoxarifado → vê todas exceto rascunhos de terceiros.
- Superusuário → vê todas.

**Decisão:** auxiliar de setor lê apenas próprias (criador/beneficiário) — matriz §4 lista "Ver requisições do setor: Não" para aux. setor. Apenas chefe de setor enxerga setor inteiro.

## Test Strategy

### `test_selectors.py` — `requisicoes_visiveis_para`
- Solicitante puro: vê próprias como criador; vê próprias como beneficiário fora de rascunho; NÃO vê rascunho de terceiro onde é beneficiário; NÃO vê requisições de outros.
- Chefe de setor: vê requisições do setor (criador OU beneficiário no setor) exceto rascunhos de terceiros; NÃO vê outro setor.
- Aux de setor: mesmo comportamento de solicitante (apenas próprias).
- Aux/Chefe almoxarifado: vê todas exceto rascunhos de terceiros.
- Superusuário: vê todas, incluindo rascunhos de terceiros (decisão: superuser vê tudo).
- Inativo: queryset vazio.

### `test_selectors.py` — `minhas_requisicoes`
- Subconjunto de `requisicoes_visiveis_para` filtrado por `criador OR beneficiario`.
- Exclui rascunho de terceiro onde sou beneficiário.
- Ordenação `-criado_em`.

### `test_views.py` — `minhas_requisicoes_view`
- Sem login → 302 para login.
- Autenticado → 200; contexto contém apenas as próprias.
- Lista renderiza badge, número público (fallback "Rascunho"), beneficiário, data.

### `test_views.py` — `detalhe_requisicao_view`
- Sem login → 302 login.
- Visível (criador) → 200 com itens + timeline.
- Visível (beneficiário fora de rascunho) → 200.
- Beneficiário em rascunho de terceiro → 404 (não revelar).
- Outro setor sem papel → 404.
- Chefe de setor → 200 para requisição do setor não-rascunho-terceiro.
- Almox → 200 para qualquer requisição não-rascunho-terceiro.

## Invariants

- Visibilidade unificada em `selectors.py` — views não duplicam filtros (ADR-0004).
- Rascunho de terceiro = creator-only sempre, exceto superusuário.
- Detail view fora de escopo retorna 404, não 403 (ADR-0010 §exposição).
- Timeline segue visibilidade da requisição (matriz-permissoes §6: "Consultar histórico de movimentações: timeline da requisição segue visibilidade da requisição").

## Risks

- Auxiliar de setor: matriz §4 marca "Ver requisições do setor: Não" para aux.setor. Confirmar essa leitura — se aux.setor PODE ver setor, alterar selector.
- Performance: queryset com OR amplo + select_related para evitar N+1 no template.
- `setor_beneficiario` é snapshot — filtrar por `setor_beneficiario_id`, não `beneficiario__setor_id`.

## Out of Scope para UI rica

Esta issue entrega telas funcionais usando o `base.html` atual (sem top nav). Estilo seguindo `docs/design-system.md`: Tailwind utilitário, `<table>` semântico, badges com tokens slate/amber/blue/green/red/teal. Componentização global (`button.html`, etc.) é issue separada — aqui escrevo classes Tailwind inline.
