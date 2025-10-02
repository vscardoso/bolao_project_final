# 🚀 GUIA COMPLETO DE DEPLOY - BOLÃO ONLINE

## 📋 PRÉ-REQUISITOS

Antes de deployar:
- [x] FASE 0 completa (segurança)
- [x] FASE 1 completa (infraestrutura)
- [x] .env configurado
- [x] Git atualizado

---

## 🎯 OPÇÕES DE DEPLOY

| Provedor | Dificuldade | Custo/mês | Recomendado Para |
|----------|-------------|-----------|------------------|
| **Railway** | Fácil | $5-20 | MVP rápido ⭐ |
| **Heroku** | Fácil | $7-25 | Startups |
| **Render** | Fácil | $7-25 | Alternativa moderna |
| **DigitalOcean** | Média | $12-50 | Profissional |
| **AWS** | Difícil | $20-100 | Enterprise |

---

## 🔵 RAILWAY (RECOMENDADO)

### Por que Railway?
✅ Deploy em 5 minutos
✅ MySQL incluído
✅ SSL automático
✅ $5 crédito grátis

### Passo a Passo

#### 1. Preparar Repositório
```bash
git add .
git commit -m "feat: preparar deploy"
git push
```

#### 2. Criar Projeto
1. Acesse https://railway.app
2. Login com GitHub
3. "New Project" → "Deploy from GitHub"
4. Selecione repositório

#### 3. Adicionar MySQL
1. "New" → "Database" → "MySQL"
2. Copie DATABASE_URL

#### 4. Variáveis de Ambiente
```env
DJANGO_SETTINGS_MODULE=bolao_config.settings_production
SECRET_KEY=<gerar nova>
DEBUG=False
ALLOWED_HOSTS=.railway.app
DATABASE_URL=<copiar do Railway>
```

#### 5. Deploy Automático
- Railway detecta Procfile
- Build automático
- URL: https://seu-app.railway.app

---

## 🟣 HEROKU

### Setup
```bash
# Instalar CLI
choco install heroku-cli  # Windows

# Login
heroku login

# Criar app
heroku create bolao-online

# Add MySQL
heroku addons:create jawsdb:kitefin

# Configurar
heroku config:set DJANGO_SETTINGS_MODULE=bolao_config.settings_production
heroku config:set SECRET_KEY=<nova>
heroku config:set DEBUG=False

# Deploy
git push heroku main
heroku run python manage.py migrate
heroku open
```

---

## 🟢 RENDER

### Setup
1. Acesse https://render.com
2. New → Web Service
3. Connect GitHub
4. Configure:
   - Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start: `gunicorn bolao_config.wsgi:application`

### Environment Variables
```env
DJANGO_SETTINGS_MODULE=bolao_config.settings_production
SECRET_KEY=<nova>
DEBUG=False
PYTHON_VERSION=3.13.2
```

---

## 🐳 DOCKER + VPS

### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    volumes:
      - mysql_data:/var/lib/mysql

  web:
    build: .
    command: gunicorn bolao_config.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db

volumes:
  mysql_data:
```

### Deploy
```bash
# SSH no VPS
ssh user@vps.com

# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Clonar e configurar
git clone repo.git
cd bolao_project
cp .env.production.example .env
nano .env

# Rodar
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## 🌐 DOMÍNIO PRÓPRIO

### Railway/Heroku/Render
1. Settings → Custom Domain
2. Adicionar: www.seudominio.com

### DNS (no provedor de domínio)
```
Tipo: CNAME
Nome: www
Valor: <url-provedor>
```

### Atualizar .env
```env
ALLOWED_HOSTS=seudominio.com,www.seudominio.com
```

---

## 🔒 SSL/HTTPS

**Automático**: Railway, Heroku, Render ✅

**Manual (VPS)**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seudominio.com
```

---

## 📊 MONITORAMENTO

### Ver Logs
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Docker
docker-compose logs -f web
```

### Health Check
```bash
curl https://seu-app.com/health/
```

Resposta:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok"
  }
}
```

---

## 🚨 TROUBLESHOOTING

### Application Error
```bash
# Ver logs
heroku logs --tail

# Verificar variáveis
heroku config
```

### Static files not found
```bash
python manage.py collectstatic --noinput
```

### Database error
```bash
# Verificar DATABASE_URL
echo $DATABASE_URL
```

---

## ✅ CHECKLIST PÓS-DEPLOY

- [ ] SSL/HTTPS OK
- [ ] /health/ retorna 200
- [ ] /admin/ acessível
- [ ] Static files OK
- [ ] Email funcionando
- [ ] Backup configurado
- [ ] Monitoring ativo

---

## 🎯 RECOMENDAÇÃO

**MVP Rápido**: 🔵 Railway
- Mais fácil
- MySQL incluído
- $5 grátis

**Produção**: 🔶 DigitalOcean/AWS
- Mais controle
- Escalável

**Aprendizado**: 🐳 Docker
- Controle total
- Mais barato

---

**By**: Claude Code
**Data**: 02/10/2025
