# Plano — fix(topbar): drawer backdrop overlay + a11y (Issue #6)

## Scope

**O que muda:** `apps/core/templates/base_auth.html` — adicionar backdrop overlay ao drawer mobile e trap de foco.

**O que NÃO muda:** CSS (input.css / app.css), JS vendored, templates de subtelas, modelos, views.

## Acceptance criteria (da issue)

1. Backdrop `<div class="fixed inset-0 bg-slate-900/40">` com fade transition
2. Click no backdrop fecha drawer
3. ESC fecha drawer — **já existe** (`@keydown.escape.window` na linha 17)
4. Trap de foco via Alpine `x-trap.inert.noscroll="menuOpen"`

## Files touched

| Arquivo | Mudança |
|---------|---------|
| `apps/core/templates/base_auth.html` | +backdrop div + x-trap no drawer |
| `docs/plans/gh6-drawer-backdrop.md` | este arquivo |

## Implementação

### 1. Backdrop

Inserir imediatamente após `<header ...>`, antes de `<div class="app-bar__inner">`:

```html
<div
  class="fixed inset-0 z-30 bg-slate-900/40"
  x-show="menuOpen"
  x-cloak
  x-transition:enter="transition ease-out duration-150"
  x-transition:enter-start="opacity-0"
  x-transition:enter-end="opacity-100"
  x-transition:leave="transition ease-in duration-150"
  x-transition:leave-start="opacity-100"
  x-transition:leave-end="opacity-0"
  @click="menuOpen = false"
  aria-hidden="true"
></div>
```

**z-index:** backdrop usa `z-30` (30) — abaixo do drawer (`.app-bar__menu` tem z-index: 40 no CSS). Ambos dentro do stacking context do `.app-bar` (sticky + z-30), que já está acima do conteúdo principal (z: auto).

### 2. Focus trap

Adicionar `x-trap.inert.noscroll="menuOpen"` ao `<div id="app-bar-menu">`.

Plugin `@alpinejs/focus` (alpine-focus.min.js) já carregado em `base.html`.

## Test strategy

Issue é puramente frontend/template — sem lógica Python. Não há testes automatizados para templates HTML neste projeto.

QA manual (conforme acceptance criteria da issue):
- [ ] Mobile 390px: backdrop escurece conteúdo atrás
- [ ] Click no backdrop fecha drawer
- [ ] ESC fecha drawer
- [ ] Tab fica preso dentro do drawer enquanto aberto
- [ ] Validar nos 3 viewports: mobile / tablet / desktop

## Invariants

Nenhuma entrada na matriz de invariantes afetada — mudança é puramente de template/a11y.

## Risks

- `x-trap.inert` torna elementos externos inerts — botão toggle (fora do drawer) ficará inert enquanto drawer aberto. Usuário fecha via backdrop/ESC/item, não via re-click no toggle. Comportamento Material Design correto.
- `position: fixed` dentro de `position: sticky` com `z-index`: sem transform/filter no header, o containing block do fixed é o viewport. `inset-0` expande corretamente. ✓
