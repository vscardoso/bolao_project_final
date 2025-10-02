# 🚀 INÍCIO RÁPIDO - BOLÃO ONLINE

## ⚡ DESENVOLVIMENTO LOCAL (2 minutos)

```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Rodar servidor
python manage.py runserver

# 3. Acessar
http://localhost:8000
```

**Pronto!** ✅ Projeto rodando em desenvolvimento

---

## 🏭 DEPLOY EM PRODUÇÃO (Checklist)

### 📋 Antes de Começar

```bash
# 1. Verificar o que está faltando
bash deploy_checklist.sh
```

### 🔒 Configurar Segurança (OBRIGATÓRIO)

```bash
# 1. Copiar template de produção
cp .env.production.example .env

# 2. Gerar SECRET_KEY nova
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 3. Editar .env com:
# - SECRET_KEY gerada acima
# - ALLOWED_HOSTS=seu-dominio.com
# - Credenciais do banco
# - SMTP real para emails
nano .env  # ou vim/notepad
```

### 📦 Instalar Dependências de Produção

```bash
pip install whitenoise gunicorn
pip freeze > requirements.txt
```

### 🔧 Preparar Aplicação

```bash
# 1. Rodar migrations
python manage.py migrate --settings=bolao_config.settings_production

# 2. Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=bolao_config.settings_production

# 3. Criar admin
python manage.py createsuperuser --settings=bolao_config.settings_production
```

### ✅ Validar Configuração

```bash
# Deve retornar 0 erros
python manage.py check --deploy --settings=bolao_config.settings_production
```

### 🚀 Iniciar Servidor

```bash
gunicorn bolao_config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --env DJANGO_SETTINGS_MODULE=bolao_config.settings_production
```

---

## 📊 STATUS DO PROJETO

### ✅ O Que Está Pronto
- Backend completo (95%)
- Frontend moderno (93%)
- Funcionalidades principais (90%)
- Segurança configurada (FASE 0 ✅)

### ⏳ O Que Falta (Para Produção Robusta)
- [ ] Hosting configurado (FASE 1)
- [ ] Banco gerenciado (FASE 1)
- [ ] SSL/HTTPS (FASE 1)
- [ ] Rate limiting (FASE 2)
- [ ] Testes >60% coverage (FASE 3)

### 🎯 Prioridade AGORA
**FASE 1: Infraestrutura** (2-3 dias)

---

## 📚 DOCUMENTAÇÃO

| Arquivo | Descrição |
|---------|-----------|
| `ANALISE_ARQUITETURAL_COMPLETA_PRODUCAO.md` | Análise completa do projeto |
| `FASE0_SEGURANCA_COMPLETA.md` | Detalhes da FASE 0 |
| `RESUMO_FASE0.md` | Resumo executivo |
| `deploy_checklist.sh` | Script de verificação |
| `.env.example` | Template desenvolvimento |
| `.env.production.example` | Template produção |

---

## 🆘 COMANDOS ÚTEIS

### Desenvolvimento
```bash
# Rodar servidor
python manage.py runserver

# Criar migrations
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Criar superuser
python manage.py createsuperuser

# Shell Django
python manage.py shell
```

### Produção
```bash
# Usar settings de produção (adicionar a todos os comandos)
--settings=bolao_config.settings_production

# Exemplo
python manage.py migrate --settings=bolao_config.settings_production
```

### Testes
```bash
# Rodar testes
python manage.py test

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🐛 TROUBLESHOOTING

### Erro: "No module named X"
```bash
pip install -r requirements.txt
```

### Erro: "SECRET_KEY not set"
```bash
# Gerar nova
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Adicionar ao .env
```

### Erro: "ALLOWED_HOSTS"
```bash
# No .env:
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
```

### Erro: "Static files not found"
```bash
python manage.py collectstatic --noinput
```

---

## 📞 PRÓXIMOS PASSOS

1. **HOJE**: Ler `ANALISE_ARQUITETURAL_COMPLETA_PRODUCAO.md`
2. **ESTA SEMANA**: Executar FASE 1 (Infraestrutura)
3. **SEMANA QUE VEM**: FASE 2 (Segurança) + FASE 3 (Testes)
4. **DEPLOY**: 🚀

---

**Última atualização**: 02/10/2025
**By**: Claude Code
