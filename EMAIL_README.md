# 📧 README - Configuração de Email Gmail

**Sistema**: Django Bolão  
**Data**: 29/09/2025  
**Objetivo**: Configurar email profissional com Gmail SMTP  

## 🚀 Quick Start

### 1️⃣ **Configuração Rápida**
```bash
# Execute o script de demonstração
python setup_email_demo.py
```

### 2️⃣ **Configuração Manual**
```bash
# 1. Configure Gmail
python configure_gmail.py

# 2. Teste funcionamento
python test_email.py
```

---

## 📋 Pré-requisitos Gmail

### 🔐 **Verificação em 2 Etapas**
1. Acesse: https://myaccount.google.com/security
2. Ative "Verificação em duas etapas"
3. Configure SMS, app autenticador ou chave

### 🔑 **Senha de App**
1. Acesse: https://myaccount.google.com/apppasswords
2. Selecione "Email" → "Outro (nome personalizado)"
3. Digite "Django Bolao"
4. Copie a senha de 16 caracteres

---

## 📁 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `email_setup_guide.md` | Guia completo de configuração |
| `configure_gmail.py` | Script de configuração automática |
| `test_email.py` | Script de teste de envio |
| `setup_email_demo.py` | Demo interativo |

---

## ⚙️ Configurações no Django

### 📄 **settings.py** (já configurado)
```python
# Email settings usando python-decouple
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='naoresponda@bolaoonline.com')
```

### 📄 **.env** (será criado)
```env
# Email Configuration (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=seu_email@gmail.com
```

---

## 🧪 Teste de Funcionamento

### ✅ **Execução do Teste**
```bash
python test_email.py
```

### 📧 **Email de Teste Esperado**
- **Assunto**: ✅ Teste Django Bolão - DD/MM/AAAA HH:MM:SS
- **Conteúdo**: Informações do sistema e configurações
- **Entrega**: 1-5 minutos (verificar spam)

---

## 🔧 Solução de Problemas

### ❌ **Erro: "Authentication failed"**
- **Causa**: Senha de app incorreta
- **Solução**: Gerar nova senha no Gmail

### ❌ **Erro: "SMTP connection failed"**
- **Causa**: Firewall ou conectividade
- **Solução**: Verificar porta 587 e internet

### ❌ **Erro: "2-step verification required"**
- **Causa**: 2FA não ativado
- **Solução**: Ativar no Gmail primeiro

---

## 📊 Limites Gmail

| Recurso | Limite |
|---------|--------|
| Emails/dia (gratuito) | 500 |
| Destinatários/email | 100 |
| G Workspace | 2000/dia |

---

## 🔒 Segurança

### ✅ **Boas Práticas**
- ✅ Usar senhas de app (não senha principal)
- ✅ Manter credenciais no .env
- ✅ Não versionar .env no Git
- ✅ Ativar logs de email
- ✅ Monitorar envios

### ❌ **Evitar**
- ❌ Hardcoded de senhas no código
- ❌ Usar senha principal do Gmail
- ❌ Compartilhar senhas de app
- ❌ Envios em massa sem controle

---

## 🚀 Uso no Django

### 📧 **Envio Básico**
```python
from django.core.mail import send_mail

send_mail(
    'Assunto do Email',
    'Mensagem do email...',
    'remetente@gmail.com',
    ['destinatario@email.com'],
    fail_silently=False,
)
```

### 📧 **Email HTML**
```python
from django.core.mail import EmailMessage

email = EmailMessage(
    'Assunto',
    '<h1>Email HTML</h1><p>Conteúdo...</p>',
    'remetente@gmail.com',
    ['destinatario@email.com'],
)
email.content_subtype = 'html'
email.send()
```

---

## 📈 Próximos Passos

### 🎯 **Para Produção**
1. **Domínio Próprio**: Configurar `@seudominio.com`
2. **Email Service**: Migrar para SendGrid/Mailgun
3. **Templates**: Criar templates HTML profissionais
4. **Monitoramento**: Implementar tracking de entregas
5. **Automação**: Emails automáticos de notificação

### 🔄 **Integração com Bolão**
1. **Notificações**: Resultados de jogos
2. **Convites**: Novos bolões criados
3. **Relatórios**: Performance semanal
4. **Alertas**: Deadlines de apostas

---

**✅ Sistema de email profissional configurado!**

**🚀 Pronto para produção com Gmail SMTP!**