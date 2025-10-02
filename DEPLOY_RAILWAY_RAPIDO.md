# 🚀 DEPLOY RAILWAY - 5 MINUTOS

## ✅ PRÉ-REQUISITOS
- [x] Código commitado no Git
- [x] Conta GitHub ativa
- [x] FASE 0 e FASE 1 completas

---

## 📋 PASSO A PASSO

### **1. PUSH PARA GITHUB** (1 min)

```bash
# No seu terminal local
git add .
git commit -m "feat: preparar deploy Railway - FASE 0 e 1 completas"
git push origin main
# ou: git push origin feature/frontend-phase2
```

### **2. CRIAR PROJETO RAILWAY** (1 min)

1. Acesse: https://railway.app
2. Click **"Login"** → **"Login with GitHub"**
3. Autorize o Railway no GitHub
4. Click **"New Project"**
5. Selecione **"Deploy from GitHub repo"**
6. Escolha: **bolao_project** (seu repositório)
7. Click **"Deploy Now"**

### **3. ADICIONAR MYSQL** (1 min)

1. No projeto Railway, click **"New"** (canto superior direito)
2. Selecione **"Database"**
3. Click **"Add MySQL"**
4. Aguarde provisionar (~30 segundos)
5. Click no serviço **MySQL**
6. Aba **"Variables"** → Copie a **DATABASE_URL**

Exemplo:
```
mysql://root:senha123@containers-us-west-XX.railway.app:7XXX/railway
```

### **4. CONFIGURAR VARIÁVEIS DE AMBIENTE** (2 min)

1. Click no serviço **bolao-project** (web)
2. Aba **"Variables"**
3. Click **"New Variable"** e adicione:

```env
DJANGO_SETTINGS_MODULE=bolao_config.settings_production

SECRET_KEY=<GERAR NOVA - VER ABAIXO>

DEBUG=False

ALLOWED_HOSTS=.railway.app,.up.railway.app

DATABASE_URL=<COLAR DO MYSQL ACIMA>

DB_ENGINE=django.db.backends.mysql

# Email (console por enquanto)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### **GERAR SECRET_KEY**:
No seu terminal local:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copie a saída e cole em SECRET_KEY no Railway.

### **5. DEPLOY AUTOMÁTICO** (30 seg)

Railway detecta o **Procfile** e:
1. Instala dependências
2. Roda migrations (release command)
3. Inicia gunicorn
4. Gera URL pública

**Status**: Acompanhe em "Deployments"

### **6. OBTER URL** (10 seg)

1. Aba **"Settings"**
2. Seção **"Domains"**
3. Click **"Generate Domain"**
4. URL gerada: `https://seu-app.up.railway.app`

---

## ✅ TESTAR APLICAÇÃO

### Health Check
```bash
curl https://seu-app.up.railway.app/health/
```

**Resposta esperada**:
```json
{
  "status": "healthy",
  "python_version": "3.13.2",
  "checks": {
    "database": "ok"
  }
}
```

### Admin
```
https://seu-app.up.railway.app/admin/
```

### Home
```
https://seu-app.up.railway.app/
```

---

## 🛠️ CRIAR SUPERUSER

No Railway Dashboard:

1. Serviço **bolao-project** → Aba **"Deploy"**
2. Click nos **"..."** do último deploy
3. Selecione **"Shell"**
4. Execute:
```bash
python manage.py createsuperuser
```

---

## 🚨 TROUBLESHOOTING

### Erro: "Application failed to respond"
```bash
# Ver logs
Railway Dashboard → serviço web → Aba "Logs"
```

### Erro: "Database connection failed"
```bash
# Verificar DATABASE_URL
# Deve estar no formato:
mysql://user:pass@host:port/dbname
```

### Erro: "Static files 404"
```bash
# Verificar deploy logs
# WhiteNoise deve estar servindo os arquivos
```

### Redeploy Manual
```bash
# Railway Dashboard
Aba "Deployments" → Click "Redeploy"
```

---

## 📊 PÓS-DEPLOY

### ✅ Checklist
- [ ] /health/ retorna 200
- [ ] /admin/ acessível
- [ ] Login funcionando
- [ ] Static files OK
- [ ] Criar superuser
- [ ] Testar criar bolão
- [ ] Testar apostas

### 🔒 Segurança
- [ ] DEBUG=False confirmado
- [ ] SECRET_KEY única
- [ ] ALLOWED_HOSTS correto

### 📈 Próximos Passos
- [ ] Configurar domínio próprio (opcional)
- [ ] Adicionar monitoring (Sentry)
- [ ] FASE 2: Rate limiting
- [ ] FASE 3: Testes

---

## 💰 CUSTOS RAILWAY

**Free Trial**: $5 crédito grátis
**Uso estimado**:
- Web service: $5-10/mês
- MySQL: $5/mês
- **Total**: ~$10-15/mês

**Billing**: Settings → Billing

---

## 🎯 COMANDOS RAILWAY CLI (Opcional)

```bash
# Instalar
npm i -g @railway/cli

# Login
railway login

# Ver logs em tempo real
railway logs

# Abrir no browser
railway open

# Shell no servidor
railway run bash
```

---

## ✅ SUCESSO!

🎉 **Parabéns!** Seu bolão está no ar em produção!

**URL**: https://seu-app.up.railway.app

**Próximo**:
1. Testar tudo
2. Coletar feedback
3. Iterar melhorias
4. FASE 2-3 quando necessário

---

**By**: Claude Code
**Data**: 02/10/2025
