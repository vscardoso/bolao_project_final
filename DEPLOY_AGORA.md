# 🚀 DEPLOY AGORA - RAILWAY EM 5 MINUTOS

## ✅ CÓDIGO JÁ ESTÁ NO GITHUB!

**Branch**: `feature/frontend-phase2`
**Commit**: Deploy Railway ready - FASE 0 e 1 completas
**Status**: ✅ Pronto para deploy

---

## 🎯 PRÓXIMOS 3 PASSOS (5 MINUTOS)

### **PASSO 1: RAILWAY.APP** (1 min)

1. Abra: https://railway.app
2. Click **"Login with GitHub"**
3. Autorize Railway
4. Click **"New Project"**
5. Click **"Deploy from GitHub repo"**
6. Selecione: **vscardoso/bolao_project_final**
7. Branch: **feature/frontend-phase2**
8. Click **"Deploy Now"**

### **PASSO 2: ADICIONAR MYSQL** (1 min)

1. No projeto Railway → Click **"New"**
2. **"Database"** → **"Add MySQL"**
3. Aguarde ~30 segundos
4. Click em **MySQL** → Aba **"Variables"**
5. **Copie** a variável **DATABASE_URL**

Exemplo:
```
mysql://root:XXX@containers-us-west-XX.railway.app:XXXX/railway
```

### **PASSO 3: CONFIGURAR VARIÁVEIS** (3 min)

1. Click em **bolao-project** (serviço web)
2. Aba **"Variables"** → Click **"Raw Editor"**
3. **Cole isto** (ajustar DATABASE_URL e SECRET_KEY):

```env
DJANGO_SETTINGS_MODULE=bolao_config.settings_production
DEBUG=False
ALLOWED_HOSTS=.railway.app,.up.railway.app
DATABASE_URL=<COLAR_AQUI_DO_MYSQL>
DB_ENGINE=django.db.backends.mysql
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SECRET_KEY=<GERAR_ABAIXO>
```

#### **GERAR SECRET_KEY**:
No seu terminal Windows:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie o resultado e substitua `<GERAR_ABAIXO>` acima.

4. Click **"Update Variables"**

---

## ⏳ AGUARDAR DEPLOY (30 seg)

Railway vai:
1. Detectar **Procfile**
2. Instalar deps (requirements.txt)
3. Rodar migrations
4. Iniciar gunicorn
5. Gerar URL

**Acompanhe**: Aba "Deployments"

---

## 🌐 OBTER URL

1. Aba **"Settings"**
2. Seção **"Domains"**
3. Click **"Generate Domain"**
4. URL: `https://bolao-project-production-XXXX.up.railway.app`

---

## ✅ TESTAR

### Health Check
```bash
curl https://SUA-URL.up.railway.app/health/
```

Resposta OK:
```json
{"status": "healthy", "checks": {"database": "ok"}}
```

### Abrir no Browser
```
https://SUA-URL.up.railway.app/
```

### Admin
```
https://SUA-URL.up.railway.app/admin/
```

---

## 👤 CRIAR SUPERUSER

1. Railway → Serviço **bolao-project**
2. Aba **"Deploy"** → Click **"..."** do último deploy
3. **"Shell"**
4. Execute:
```bash
python manage.py createsuperuser
```

Preencha: username, email, senha

---

## 📊 CHECKLIST PÓS-DEPLOY

- [ ] `/health/` retorna `{"status":"healthy"}`
- [ ] `/admin/` acessível
- [ ] Superuser criado
- [ ] Login funcionando
- [ ] Static files carregando
- [ ] Criar bolão de teste
- [ ] Fazer aposta de teste

---

## 🎉 SUCESSO!

**Parabéns!** Seu bolão está ONLINE em produção!

**URL**: https://sua-url.up.railway.app

**Próximos passos**:
1. Compartilhar com usuários beta
2. Coletar feedback
3. Iterar melhorias
4. FASE 2: Rate limiting, Sentry
5. FASE 3: Testes automatizados

---

## 💰 CUSTOS

**Railway Free Trial**: $5 crédito
**Estimativa mensal**:
- Web: $5-10
- MySQL: $5
- **Total**: ~$10-15/mês

---

## 🆘 PROBLEMAS?

### Deploy Failed
Ver: Aba "Logs" no Railway

### Database Error
Verificar: DATABASE_URL está correto?

### 404 Not Found
Verificar: ALLOWED_HOSTS inclui .railway.app?

### Guia completo
Ver: `DEPLOY_RAILWAY_RAPIDO.md`

---

**By**: Claude Code
**Data**: 02/10/2025
