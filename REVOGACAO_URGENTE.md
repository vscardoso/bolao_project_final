# INSTRUÇÕES URGENTES - REVOGAÇÃO MANUAL

## 🚨 EXECUTAR IMEDIATAMENTE

### 1. **GMAIL - REVOGAR SENHA DE APP**
1. Acesse: https://myaccount.google.com/apppasswords
2. Faça login em: `jogador.lastshelter@gmail.com`
3. Encontre e REVOGUE a senha: `***SENHA_COMPROMETIDA***`
4. Gere nova senha de app para "Bolão Django"
5. Atualize o .env com a nova senha

### 2. **FOOTBALL-DATA.ORG - REVOGAR API KEY**
1. Acesse: https://www.football-data.org/client/register
2. Faça login na sua conta
3. REVOGUE a chave: `***CHAVE_COMPROMETIDA***`
4. Gere nova API key
5. Atualize o .env com a nova chave

### 3. **MYSQL - ALTERAR SENHA (Se possível)**
Execute no MySQL Workbench ou terminal:
```sql
ALTER USER 'bolao_user'@'localhost' IDENTIFIED BY '>3@L1sU,?k[FJv+[';
FLUSH PRIVILEGES;
```

## ✅ STATUS ATUAL
- SECRET_KEY: CORRIGIDA ✅
- EMAIL: DESABILITADO (Seguro temporariamente) ✅  
- BANCO: Nova senha no .env ✅
- SISTEMA: Funcionando ✅

## 🔄 APÓS REVOGAÇÕES
Atualize o .env com as novas credenciais:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=jogador.lastshelter@gmail.com
EMAIL_HOST_PASSWORD=SUA_NOVA_SENHA_APP_16_CHARS
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=jogador.lastshelter@gmail.com

FOOTBALL_API_KEY=SUA_NOVA_API_KEY_AQUI
```