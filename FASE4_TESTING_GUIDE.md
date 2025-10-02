# 🧪 FASE 4: TESTING & QA - GUIA PRÁTICO

**Data:** 01/10/2025
**Status:** 🔄 EM ANDAMENTO
**Branch:** `feature/frontend-phase2`
**Servidor:** http://127.0.0.1:8000

---

## 📋 CHECKLIST GERAL

### ✅ Preparação
- [x] Servidor Django iniciado (port 8000)
- [ ] Chrome DevTools aberto (F12)
- [ ] Lighthouse extension instalada (opcional)
- [ ] axe DevTools instalada (opcional)

---

## 🖥️ TESTES DESKTOP

### 1. Teste em 1920px (Full HD)

**Como testar:**
1. F12 → Device Toolbar (Ctrl+Shift+M)
2. Responsive → 1920 x 1080
3. Testar páginas principais

**Páginas a testar:**

#### **Home (http://127.0.0.1:8000/)**
- [ ] Hero section carrega corretamente
- [ ] Estatísticas animam ao scroll
- [ ] Cards "Como Funciona" com:
  - [ ] Border-top primária (4px gradiente no topo)
  - [ ] Icon circles grandes (100px) com gradiente
  - [ ] Espaçamento consistente (gap-5)
- [ ] Cards "Por que escolher" com:
  - [ ] Icon circles médios (80px) com fundo soft
  - [ ] 4 cards em linha
- [ ] Footer completo e alinhado

**Screenshot:** Capturar seção "Como Funciona" ✅

#### **Login (http://127.0.0.1:8000/login/)**
- [ ] Card centralizado (max-width: 500px)
- [ ] Logo e page-title (32px)
- [ ] Form labels visíveis acima dos inputs
- [ ] Password toggle button:
  - [ ] Inspecionar (F12 → Elements)
  - [ ] Verificar `aria-label="Mostrar senha"`
  - [ ] Verificar `aria-pressed="false"`
  - [ ] Clicar e verificar mudança para `aria-pressed="true"`
- [ ] Botão "Entrar" com largura completa
- [ ] Carrossel de dicas funcional

**Screenshot:** Password toggle com DevTools aberto mostrando ARIA ✅

#### **Register (http://127.0.0.1:8000/register/)**
- [ ] Card-unified com padding 3rem
- [ ] Icon header (80px) centralizado
- [ ] Benefits-quick section com 3 itens
- [ ] Forms com traditional labels
- [ ] Password strength indicator funcionando
- [ ] Password toggle em ambos campos
- [ ] Checkboxes com labels clicáveis

**Screenshot:** Password strength em ação ✅

---

### 2. Teste em 1366px (Laptop padrão)

**Como testar:**
1. Device Toolbar → 1366 x 768
2. Verificar adaptação responsiva

**Checklist:**
- [ ] Home: Cards "Como Funciona" mantêm layout 3 colunas
- [ ] Login: Card mantém centralização
- [ ] Navbar: Todos os itens visíveis (não hamburguer ainda)
- [ ] Footer: Distribuição 50/50
- [ ] Sem scroll horizontal

---

### 3. Teste em 1024px (Tablet Landscape)

**Como testar:**
1. Device Toolbar → 1024 x 768
2. Ponto de transição importante

**Checklist:**
- [ ] Home: Cards podem começar a empilhar
- [ ] Icon circles reduzem para 80px → 60px
- [ ] Padding dos cards reduz (3rem → 2rem)
- [ ] Typography reduz (32px → 28px para page-title)

---

## 📱 TESTES MOBILE

### 4. Teste em 768px (Tablet Portrait)

**Como testar:**
1. Device Toolbar → iPad (768 x 1024)
2. Modo portrait crítico

**Checklist:**
- [ ] **Navbar:**
  - [ ] Hamburguer menu aparece
  - [ ] Clicar abre menu
  - [ ] Itens empilhados verticalmente
  - [ ] Área clicável ≥ 44px
- [ ] **Cards:**
  - [ ] "Como Funciona" empilha (2 colunas → 1 coluna)
  - [ ] Padding reduzido (2rem)
  - [ ] Border-radius mantém (20px → 16px)
- [ ] **Forms:**
  - [ ] Inputs com altura adequada
  - [ ] Touch targets ≥ 44px
  - [ ] Labels legíveis

**Screenshot:** Navbar hamburguer aberto ✅

---

### 5. Teste em 414px (iPhone Pro Max)

**Como testar:**
1. Device Toolbar → iPhone 12 Pro (414 x 896)
2. Dispositivo grande common

**Checklist:**
- [ ] **Home:**
  - [ ] Hero text legível (display-4 → menor)
  - [ ] Botões full-width empilhados
  - [ ] Icon circles 100px → 60px
- [ ] **Login:**
  - [ ] Card padding 1.5rem
  - [ ] Font-size inputs: 16px (sem zoom iOS)
  - [ ] Password toggle ≥ 44px × 44px
  - [ ] Botão "Entrar" fácil de clicar
- [ ] **Register:**
  - [ ] Benefits-quick empilha verticalmente
  - [ ] Password strength visível
  - [ ] Checkboxes ≥ 24px

**Touch Target Validation:**
```
DevTools → Ruler (Ctrl+Shift+P → "Show Rulers")
Medir elementos interativos:
- [ ] Password toggle: ≥ 44px
- [ ] Navbar items: ≥ 44px
- [ ] Buttons: ≥ 44px
- [ ] Checkboxes: ≥ 24px
```

---

### 6. Teste em 375px (iPhone SE) 🔴 CRÍTICO

**Como testar:**
1. Device Toolbar → iPhone SE (375 x 667)
2. Menor dispositivo comum

**Checklist:**
- [ ] **Tudo ainda legível:**
  - [ ] Page-title: 24px
  - [ ] Body text: 16px
  - [ ] Forms não quebram
- [ ] **Cards:**
  - [ ] Padding mínimo (1.5rem)
  - [ ] Sem overflow horizontal
- [ ] **Touch targets mantêm ≥ 44px**
- [ ] **Sem zoom ao focar inputs** (font-size ≥ 16px)

**Screenshot:** Home completa em 375px ✅

---

## ♿ TESTES DE ACESSIBILIDADE

### 7. Skip-to-Content Link

**Como testar:**
1. Abrir http://127.0.0.1:8000/
2. Pressionar **Tab** (primeira vez)
3. Link "Pular para o conteúdo" deve aparecer centralizado
4. Pressionar **Enter**
5. Foco deve pular direto para `<main id="main-content">`

**Checklist:**
- [ ] Link invisível por padrão
- [ ] Aparece ao receber foco (Tab)
- [ ] Centralizado horizontalmente
- [ ] Outline visível (3px amarelo)
- [ ] Enter funciona e pula navegação
- [ ] Link desaparece após Enter

**Screenshot:** Skip link visível (Tab pressionado) ✅

---

### 8. Password Toggle + ARIA

**Como testar:**
1. Abrir http://127.0.0.1:8000/login/
2. F12 → Elements
3. Inspecionar botão `.password-toggle-btn`

**Checklist:**
- [ ] **Estado inicial:**
  ```html
  aria-label="Mostrar senha"
  aria-pressed="false"
  ```
- [ ] **Ícone inicial:**
  ```html
  <i class="fas fa-eye" aria-hidden="true"></i>
  ```
- [ ] **Após clicar:**
  ```html
  aria-label="Ocultar senha"
  aria-pressed="true"
  <i class="fas fa-eye-slash" aria-hidden="true"></i>
  ```
- [ ] **Password input:**
  - [ ] type="password" → type="text"
  - [ ] Senha visível

**Repetir em:** http://127.0.0.1:8000/register/ (2 campos)

**Screenshot:** DevTools mostrando ARIA attributes ✅

---

### 9. Icon Circles (Utilities)

**Como testar:**
1. Abrir http://127.0.0.1:8000/
2. Inspecionar cards "Como Funciona"

**Checklist:**
- [ ] **Classes corretas:**
  ```html
  <div class="icon-circle icon-circle-xl icon-circle-primary">
  ```
- [ ] **Sem inline styles** (verificar no Elements)
- [ ] **Renderização:**
  - [ ] Desktop: 100px × 100px
  - [ ] Tablet: 60px × 60px
  - [ ] Mobile: 60px ou 50px
- [ ] **Background:** Gradiente primário
- [ ] **Ícone centralizado**

**Screenshot:** Inspecionar elemento com classes visíveis ✅

---

### 10. Border-Top Decorations

**Como testar:**
1. Inspecionar cards "Como Funciona"
2. Verificar elemento `.border-top-primary`

**Checklist:**
- [ ] **Classes corretas:**
  ```html
  <div class="border-top-primary"></div>
  ```
- [ ] **Sem inline styles**
- [ ] **CSS aplicado:**
  ```css
  position: absolute;
  top: 0;
  height: 4px;
  background: var(--gradient-primary);
  ```
- [ ] Visível no topo do card

---

## 🔍 LIGHTHOUSE AUDITS

### 11. Lighthouse - Home

**Como executar:**
1. F12 → Lighthouse tab
2. Selecionar:
   - [x] Performance
   - [x] Accessibility ⭐
   - [x] Best Practices
   - [x] SEO
3. Device: Desktop
4. **Generate report**

**Target Scores:**
- Performance: ≥ 80
- **Accessibility: ≥ 90** 🎯
- Best Practices: ≥ 90
- SEO: ≥ 90

**Checklist pós-audit:**
- [ ] Score Accessibility ≥ 90
- [ ] 0 erros críticos
- [ ] Capturar screenshot completo
- [ ] Verificar sugestões de melhoria

**Screenshot:** Relatório Lighthouse completo ✅

---

### 12. Lighthouse - Login

**Repetir processo acima para:**
http://127.0.0.1:8000/login/

**Foco especial em:**
- [ ] Form labels associados (for/id)
- [ ] ARIA labels em password toggle
- [ ] Heading hierarchy (h1 presente)
- [ ] Color contrast ≥ 4.5:1

**Screenshot:** Relatório Lighthouse ✅

---

### 13. Lighthouse - Register

**Repetir processo acima para:**
http://127.0.0.1:8000/register/

**Foco especial em:**
- [ ] Form validation
- [ ] Password strength não afeta acessibilidade
- [ ] Checkboxes acessíveis
- [ ] Error messages (se houver)

**Screenshot:** Relatório Lighthouse ✅

---

## ⌨️ KEYBOARD NAVIGATION

### 14. Teste Completo de Teclado

**Páginas:** Home, Login, Register

**Checklist geral:**
1. **Tab Order Lógico:**
   - [ ] Tab navega sequencialmente
   - [ ] Ordem faz sentido (top → bottom, left → right)
   - [ ] Nenhum elemento "preso"

2. **Focus Visível:**
   - [ ] Todos elementos têm outline visível
   - [ ] Outline adequado (≥ 2px)
   - [ ] Cor contrastante

3. **Elementos Interativos:**
   - [ ] Links: Enter abre
   - [ ] Botões: Enter/Space ativa
   - [ ] Inputs: Foco ativa cursor
   - [ ] Dropdowns: Enter abre, Arrow navega
   - [ ] Checkboxes: Space marca/desmarca

4. **Skip Link:**
   - [ ] Primeiro elemento ao Tab
   - [ ] Enter funciona

5. **Navbar Hamburguer (Mobile):**
   - [ ] Tab alcança toggle button
   - [ ] Enter abre menu
   - [ ] Tab navega dentro do menu
   - [ ] Escape fecha menu (se implementado)

**Screenshot:** Elemento focado com outline visível ✅

---

## 🐛 VALIDAÇÃO TÉCNICA

### 15. Validar CSS Removido

**Executar no terminal:**

```powershell
# Verificar que classes removidas NÃO são usadas
grep -r "register-card\"" templates/
# Esperado: Apenas register-card-simple

grep -r "benefits-panel" templates/
# Esperado: Nenhum resultado

grep -r "testimonial" templates/
# Esperado: Nenhum resultado

grep -r "slideInDown" static/css/
# Esperado: Nenhum resultado
```

**Checklist:**
- [ ] `.register-card` não encontrado
- [ ] `.benefits-panel` não encontrado
- [ ] `.testimonial` não encontrado
- [ ] `slideInDown` não encontrado

---

### 16. Validar Inline Styles Removidos

**Executar no terminal:**

```powershell
# Verificar home.html
grep "style=" templates/core/home.html
# Esperado: Apenas estilos dinâmicos (badges, progress bars)
```

**Checklist:**
- [ ] Sem `style="width: 100px; height: 100px"`
- [ ] Sem `style="background: var(--gradient-primary)"`
- [ ] Sem `style="height: 4px; background:"`

---

### 17. Validar ARIA Attributes

**Executar no terminal:**

```powershell
# Verificar aria-label
grep -r "aria-label" templates/
# Esperado: base.html, login.html, register.html

# Verificar aria-hidden
grep -r "aria-hidden" templates/
# Esperado: Múltiplas ocorrências em ícones

# Verificar skip-link
grep "skip-link" templates/base.html
# Esperado: 1 ocorrência
```

**Checklist:**
- [ ] `aria-label` em password toggle
- [ ] `aria-label` no navbar toggle
- [ ] `aria-hidden="true"` em ícones decorativos
- [ ] Skip link presente no base.html

---

## 📸 SCREENSHOTS OBRIGATÓRIOS

### Lista de Capturas:

1. **Home Desktop (1920px):**
   - [ ] Seção "Como Funciona" (icon circles + borders)
   - [ ] Seção "Por que escolher" (icon circles soft)

2. **Home Mobile (375px):**
   - [ ] Hero + primeira seção

3. **Login:**
   - [ ] DevTools mostrando password toggle com ARIA

4. **Register:**
   - [ ] Password strength indicator ativo

5. **Skip Link:**
   - [ ] Link visível após pressionar Tab

6. **Navbar Mobile:**
   - [ ] Hamburguer menu aberto (768px)

7. **Lighthouse Reports:**
   - [ ] Home (score completo)
   - [ ] Login (score completo)
   - [ ] Register (score completo)

---

## 🐛 TEMPLATE DE BUG REPORT

**Para cada bug encontrado:**

```markdown
## Bug #X: [Título curto]

**Severidade:** 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

**Página:** [URL ou template]

**Breakpoint:** [1920px / 768px / 375px / etc]

**Descrição:**
[Descrição clara do problema]

**Steps to Reproduce:**
1. Abrir [página]
2. [Ação]
3. [Resultado observado]

**Expected:**
[Comportamento esperado]

**Actual:**
[Comportamento atual]

**Screenshot:**
[Adicionar se relevante]

**Fix Proposto:**
[Como corrigir]

**Arquivo(s) Afetado(s):**
- [arquivo.html]
- [arquivo.css]
```

---

## ✅ CRITÉRIOS DE APROVAÇÃO

### Fase 4 está completa quando:

- [ ] **Desktop (3 resoluções)** testadas sem issues críticos
- [ ] **Mobile (3 resoluções)** testadas sem issues críticos
- [ ] **Lighthouse Accessibility ≥ 90** em todas as páginas
- [ ] **Skip link** funcional e visível
- [ ] **Password toggle** com ARIA completo
- [ ] **Icon circles** sem inline styles
- [ ] **Keyboard navigation** 100% funcional
- [ ] **CSS removido** validado (não usado)
- [ ] **Todos bugs críticos** corrigidos
- [ ] **Relatório final** (FASE4_TESTING_REPORT.md) criado

---

## 📝 NOTAS IMPORTANTES

### Ferramentas Recomendadas:

**Chrome DevTools:**
- Device Toolbar: Ctrl+Shift+M
- Inspect: Ctrl+Shift+C
- Lighthouse: F12 → Lighthouse tab

**Extensions (opcional):**
- axe DevTools: Accessibility audit detalhado
- WAVE: Visual accessibility feedback
- Lighthouse: Standalone extension

### Dicas de Teste:

1. **Cache:** Sempre fazer Hard Refresh (Ctrl+Shift+R)
2. **CSS:** Verificar que novo utilities.css está carregado
3. **JavaScript:** Console sem erros (F12 → Console)
4. **Images:** Todas carregam corretamente
5. **Forms:** Testar submit (mesmo sem backend completo)

---

## 🎯 PRÓXIMOS PASSOS APÓS FASE 4

1. **Merge para main:** Se todos os testes passarem
2. **Deploy staging:** Testar em ambiente real
3. **Documentação:** Atualizar README com mudanças
4. **Celebrar! 🎉**

---

**Documento criado por:** GitHub Copilot (Claude Sonnet 4.5)
**Data:** 01/10/2025
**Status:** 🔄 EM ANDAMENTO

**🚀 BORA TESTAR! LET'S GO! 🚀**
