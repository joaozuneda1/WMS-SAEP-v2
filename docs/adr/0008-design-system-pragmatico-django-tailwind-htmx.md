# ADR-0008: Design System Pragmático — Django Templates + Tailwind + HTMX + Alpine

**Status**: Accepted

**Data**: 2026-05-20

**Decisores**: João

## Contexto

WMS-SAEP vai renderizar telas web para usuários do almoxarifado (requisições, autorização, atendimento, estoque). Precisa de coesão visual, acessibilidade, reutilização de componentes e padrões de interação consistentes.

Alternativas consideradas:
1. **SPA com React/Vue** — full client-side, estado JS, complexidade alta
2. **Django templates + Bootstrap** — pesado, genericista, pouca flexibilidade com Tailwind
3. **Django templates + Tailwind + componentes customizados** — pragmático, incremental, reutilizável

## Decisão

Adotar **design system pragmático** baseado em:
- **Django templates** para renderização e reutilização
- **Tailwind CSS** para tokens e componentes visuais
- **HTMX** para interação sem página inteira
- **Alpine.js** para estado efêmero (dropdowns, modais, loading)

O design system cobre:
- **Tokens** (paleta, tipografia, espaçamento, estados)
- **Componentes globais** em `apps/core/templates/components/` (button, form_field, card, alert, badge, etc)
- **Partials de domínio** em `apps/<app>/templates/<app>/partials/` (mapeamento de estados, combinações negócio-específicas)
- **Padrões de interação** (loading states, HTMX swaps, validação, confirmação)

### O que NÃO fazer

- Não criar SPA — renderização server-side mantém simples
- Não criar biblioteca JS própria — Alpine.js é suficiente
- Não antecipar — componentes nascem de necessidade real, não design abstrato
- Não duplicar semântica — componentes globais desconhecem domínio (requisição, estoque, etc)

### Granularidade

**Componente global** (core):
- Conhece: variante visual, estados, ARIA
- Não conhece: semântica de negócio

**Partial de domínio** (app):
- Conhece: semântica de requisição, estoque, autorização
- Usa: componentes globais internamente

Exemplo:
- `components/status_badge.html` → global, genérico, recebe `variant="blue"` e `label="..."`
- `requisicoes/partials/_estado_badge.html` → domínio, mapeia `EstadoRequisicao.AUTORIZADA → variant="blue"`

## Consequências

### Positivas

1. **Reutilização clara**: componentes global em core, domínio em app. Sem mistura.
2. **Manutenção centralizada**: mudanças visuais em um componente afetam todas as telas.
3. **Acessibilidade por padrão**: componentes nascem com ARIA, foco, contraste. Telas herdam.
4. **Incremental**: codar só quando há necessidade real. Componentes não-usados não existem.
5. **Sem lock-in pesado**: Tailwind + templates são simples de refatorar; não há framework JS rígido.
6. **Testes simples**: componentes são templates; testáveis como HTML.

### Negativas

1. **Menos DX que React SPA**: não há hot reload per-component. Refresh necessário.
2. **Estado distribuído**: Alpine.js é client-side efêmero; estado de domínio fica backend.
3. **Sem type-safe components**: templates são strings; sem TypeScript/JSDoc automático.
4. **Documentação manual**: não há Storybook automático; documentação em markdown.

### Mitigação de negatividades

- **Documentação clara** em `docs/design-system.md` compensate falta de Storybook.
- **Code review checklist** garante padrões (acessibilidade, foco, ARIA).
- **Ordem de implementação** (button → form_field → card → alert → badge) usa padrões já testados.

## Implementação

### Fase 1: Documentação e setup (agora)

- Criar `docs/design-system.md` com tokens, componentes, acessibilidade
- Estrutura de pastas em `apps/core/templates/components/` (flat)
- Estrutura de partials de domínio em `apps/<app>/templates/<app>/partials/`

### Fase 2: Componentes globais iniciais

Ordem de impacto:
1. `button.html` — usado em tudo
2. `form_field.html` — usado em tudo
3. `card.html` — layout base
4. `alert.html` — mensagens
5. `status_badge.html` — status visual
6. `page_header.html` — tela headers
7. `modal.html` (adiar até HTMX modal concreto)
8. Tables/dropdowns (adiar até listagem real)

### Fase 3: Partials de domínio

Quando primeira tela de requisição/estoque aparecer:
- `requisicoes/partials/_estado_badge.html` — mapeia estado → cor
- `requisicoes/partials/_acoes_requisicao.html` — botões + permissões + HTMX
- `requisicoes/partials/_filtros_fila.html` — filtros + busca

### Fase 4: Iteração e refinamento

Depois de primeiras 3-5 telas:
- Identificar padrões repetidos; extrair se necessário
- Feedback de usuário em acessibilidade/usabilidade
- Ajustar tokens/componentes conforme aprendizado

## Alternativas consideradas e rejeitadas

### React/Vue SPA

**Razão de rejeição**: WMS não precisa de estado cliente complexo. HTMX é suficiente para requisições parciais. Overhead de build/tooling/state management não justificado agora. Pode migrar depois se necessário.

### Bootstrap

**Razão de rejeição**: Tailwind dá mais controle, footprint menor, menos opiniões impostas. Bootstrap é genérico demais pra domínio específico.

### Storybook

**Razão de rejeição**: Overhead de setup/manutenção. Documentação em markdown + code review é suficiente agora. Adicionar se equipe crescer ou componentes ultrapassarem 50.

## Referências

- `docs/design-system.md` — guia operacional de tokens, componentes, acessibilidade
- `docs/CONVENTIONS.md` — arquitetura em camadas (ADR-0004)
- `CONTEXT.md` — glossário de domínio

## Próximas decisões

- **Quando usar `<dialog>` nativo vs. `<div role="dialog">` em modais (foco trap, Escape, etc)
- **Quando dark mode virar requisito** — CSS custom properties vs. Tailwind dark mode
- **Se componentes crescerem muito** — quando/como hierarquizar components/ (ex: forms/, buttons/, etc)
