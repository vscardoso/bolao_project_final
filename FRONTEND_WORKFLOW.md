# 🚀 WORKFLOW DE DESENVOLVIMENTO FRONTEND EFICIENTE

## 📋 SETUP INICIAL (Execute uma vez)

### 1. Configuração do Ambiente
```bash
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependências de desenvolvimento
pip install django-extensions
pip install django-debug-toolbar
```

### 2. Iniciar Servidor Django com Auto-reload
```bash
# Terminal 1: Django Server (Auto-reload ativo)
python manage.py runserver 8000 --settings=core.settings

# Terminal 2: Observação de arquivos estáticos (opcional)
python manage.py collectstatic --noinput --clear
```

## ⚡ WORKFLOW DIÁRIO DE DESENVOLVIMENTO

### PASSO 1: Preparar Ambiente
1. **Abrir VS Code** no diretório do projeto
2. **Ativar venv**: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. **Abrir terminais paralelos**:
   - Terminal 1: Django runserver
   - Terminal 2: Comandos git/collectstatic

### PASSO 2: Desenvolvimento com Feedback Instantâneo
1. **Editar templates** (`templates/`) - **Auto-save ativo**
2. **Modificar CSS** (`static/css/`) - **Refresh automático**
3. **Usar DevTools** (`F12`) para testes responsivos
4. **Preview instantâneo** em `http://127.0.0.1:8000`

### PASSO 3: Testes Responsivos Rápidos
1. **DevTools responsive mode** (`Ctrl+Shift+M`)
2. **Testar breakpoints**:
   - Mobile: 375px, 414px
   - Tablet: 768px, 1024px
   - Desktop: 1440px, 1920px

## 🔧 COMANDOS ÚTEIS

### Desenvolvimento Frontend
```bash
# Verificar template syntax
python manage.py check --deploy

# Collectstatic para testes
python manage.py collectstatic --noinput

# Limpar cache do Django
python manage.py clearcache

# Debug de templates
python manage.py shell
```

### Git Workflow Rápido
```bash
# Commit rápido de mudanças frontend
git add templates/ static/
git commit -m "feat: improve UI/UX design"
git push
```

## 📱 SHORTCUTS ESSENCIAIS

| Ação | Shortcut | Descrição |
|------|----------|-----------|
| **Auto-save** | Automático | Salva a cada 500ms |
| **DevTools** | `F12` | Abrir ferramentas de desenvolvedor |
| **Responsive Mode** | `Ctrl+Shift+M` | Modo responsivo |
| **Reload Page** | `Ctrl+R` | Recarregar página |
| **Hard Reload** | `Ctrl+Shift+R` | Reload forçado |
| **Zoom In/Out** | `Ctrl +/-` | Zoom para testar diferentes tamanhos |
| **Quick Open** | `Ctrl+P` | Abrir arquivo rapidamente |
| **Command Palette** | `Ctrl+Shift+P` | Paleta de comandos |

## 🎯 FLUXO OTIMIZADO PARA MUDANÇAS CSS

1. **Editar CSS** em `static/css/style.css`
2. **Auto-save** salva automaticamente
3. **Django auto-reload** detecta mudança
4. **Browser atualiza** automaticamente
5. **DevTools** mostra mudanças em tempo real

## 🔄 SINCRONIZAÇÃO AUTOMÁTICA

- ✅ **Auto-save**: 500ms delay
- ✅ **Django runserver**: Auto-reload ativo
- ✅ **Browser**: Refresh manual (F5)
- ✅ **DevTools**: Atualização em tempo real

## 📊 PERFORMANCE TIPS

1. **Use Django Debug Toolbar** para análise de performance
2. **Minimize requests** com collectstatic
3. **Otimize imagens** antes de adicionar
4. **Use CSS minificado** em produção
5. **Cache templates** para melhor performance

## 🚨 TROUBLESHOOTING

### Template não atualiza?
```bash
# Limpar cache
python manage.py clearcache
# Verificar syntax
python manage.py check
```

### CSS não carrega?
```bash
# Collectstatic
python manage.py collectstatic --clear --noinput
# Verificar STATIC_URL no settings.py
```

### Server muito lento?
```bash
# Usar runserver com thread único
python manage.py runserver --nothreading
```