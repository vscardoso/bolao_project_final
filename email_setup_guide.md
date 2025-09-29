# 📧 Guia de Configuração de Email - Gmail SMTP
**Data**: 29/09/2025  
**Projeto**: Bolão Online  
**Objetivo**: Configurar email real com Gmail para produção  

## 🎯 Pré-requisitos

### 📱 **1. Conta Gmail Ativa**
- Ter uma conta Gmail válida
- Acesso às configurações de segurança

### 🔐 **2. Verificação em 2 Etapas (Obrigatório)**
- Gmail exige 2FA para senhas de app
- Necessário configurar antes de gerar senha

---

## 🔧 Passo a Passo - Configuração Gmail

### 📋 **Etapa 1: Ativar Verificação em 2 Etapas**

1. **Acesse**: https://myaccount.google.com/security
2. **Procure**: "Verificação em duas etapas"
3. **Clique**: "Começar"
4. **Configure**: SMS, app autenticador ou chave de segurança
5. **Confirme**: Processo de ativação

### 🔑 **Etapa 2: Gerar Senha de App**

1. **Acesse**: https://myaccount.google.com/apppasswords
2. **Selecione app**: "Email"
3. **Selecione dispositivo**: "Outro (nome personalizado)"
4. **Digite nome**: "Django Bolao"
5. **Clique**: "Gerar"
6. **Copie**: A senha de 16 caracteres (formato: xxxx xxxx xxxx xxxx)

⚠️ **IMPORTANTE**: Anote a senha imediatamente! Não será exibida novamente.

### 📝 **Etapa 3: Configurar .env**

Adicione as seguintes linhas ao arquivo `.env`:

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

**Substitua**:
- `seu_email@gmail.com` → Seu email real
- `xxxx xxxx xxxx xxxx` → Senha de app gerada

---

## 🔧 Implementação Automática

### 📄 **Script de Configuração**

Vou criar um script para facilitar a configuração:

```python
# configure_gmail.py
import os
from pathlib import Path

def configure_gmail_smtp():
    """Script para configurar Gmail SMTP"""
    
    print("📧 CONFIGURAÇÃO DE EMAIL GMAIL")
    print("=" * 50)
    
    # Solicitar dados do usuário
    email = input("Digite seu email Gmail: ")
    app_password = input("Digite a senha de app (16 chars): ")
    
    # Validações básicas
    if "@gmail.com" not in email:
        print("❌ Email deve ser Gmail (@gmail.com)")
        return
    
    if len(app_password.replace(" ", "")) != 16:
        print("❌ Senha de app deve ter 16 caracteres")
        return
    
    # Atualizar .env
    env_path = Path(".env")
    
    # Ler .env atual
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # Configurações de email
    email_config = f"""
# Email Configuration (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={app_password}
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL={email}
"""
    
    # Remover configurações antigas de email
    lines = content.split('\n')
    new_lines = []
    skip_email_section = False
    
    for line in lines:
        if line.startswith('# Email Configuration') or line.startswith('EMAIL_') or line.startswith('DEFAULT_FROM_EMAIL'):
            skip_email_section = True
            continue
        elif line.strip() == "" and skip_email_section:
            skip_email_section = False
            continue
        elif not skip_email_section:
            new_lines.append(line)
    
    # Adicionar nova configuração
    new_content = '\n'.join(new_lines) + email_config
    
    # Salvar .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Configuração Gmail salva em .env")
    print(f"📧 Email: {email}")
    print("🔐 Senha: ****** (protegida)")
    
    return True

if __name__ == "__main__":
    configure_gmail_smtp()
```

---

## 🧪 Teste de Email

### 📨 **Script de Teste**

```python
# test_email.py
import os
import sys
from pathlib import Path
from django.core.mail import send_mail
from django.conf import settings

# Configurar Django
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')

import django
django.setup()

def test_email_sending():
    """Testa o envio de email"""
    
    print("📧 TESTE DE ENVIO DE EMAIL")
    print("=" * 40)
    
    print(f"Backend: {settings.EMAIL_BACKEND}")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    print(f"TLS: {settings.EMAIL_USE_TLS}")
    print(f"From: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        # Enviar email de teste
        result = send_mail(
            subject='Teste Django Bolão - Email Funcionando!',
            message='''
            Olá!
            
            Este é um email de teste do sistema Django Bolão.
            
            Se você recebeu este email, a configuração está funcionando corretamente!
            
            Data do teste: 29/09/2025
            Sistema: Bolão Online
            
            Atenciosamente,
            Sistema Django Bolão
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Enviar para si mesmo
            fail_silently=False,
        )
        
        if result:
            print("✅ Email enviado com sucesso!")
            print(f"📧 Destinatário: {settings.EMAIL_HOST_USER}")
            print("🔍 Verifique sua caixa de entrada")
        else:
            print("❌ Falha no envio do email")
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        print()
        print("💡 Possíveis causas:")
        print("   • Senha de app incorreta")
        print("   • Verificação em 2 etapas não ativada")
        print("   • Email ou configurações inválidas")
        print("   • Firewall bloqueando conexão SMTP")

if __name__ == "__main__":
    test_email_sending()
```

---

## ⚙️ Configurações Avançadas

### 🔐 **Segurança Adicional**

```python
# settings.py - Configurações adicionais de segurança
EMAIL_TIMEOUT = 30  # Timeout em segundos
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_USE_LOCALTIME = False

# Para ambientes de desenvolvimento
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = config('EMAIL_BACKEND')
```

### 📊 **Logging de Email**

```python
# settings.py - Logging para emails
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'email_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/email.log',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['email_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 🚨 Troubleshooting

### ❌ **Problemas Comuns**

#### 1. **"Authentication failed"**
```
Causa: Senha de app incorreta
Solução: Gerar nova senha de app no Gmail
```

#### 2. **"SMTP connection failed"**
```
Causa: Firewall ou proxy bloqueando
Solução: Verificar conectividade na porta 587
```

#### 3. **"2-step verification required"**
```
Causa: 2FA não ativado no Gmail
Solução: Ativar verificação em 2 etapas
```

#### 4. **"Less secure app access"**
```
Causa: Configuração desatualizada
Solução: Usar senhas de app (método atual)
```

### 🔧 **Comandos de Diagnóstico**

```bash
# Testar conectividade SMTP
telnet smtp.gmail.com 587

# Verificar configurações Django
python manage.py shell -c "from django.conf import settings; print(settings.EMAIL_HOST)"

# Enviar email de teste
python test_email.py
```

---

## 📋 Checklist de Configuração

### ✅ **Antes de Configurar**
- [ ] Conta Gmail ativa
- [ ] Acesso às configurações de segurança
- [ ] Verificação em 2 etapas ativada

### ✅ **Durante a Configuração**
- [ ] Senha de app gerada corretamente
- [ ] Configurações adicionadas ao .env
- [ ] Email de teste enviado com sucesso

### ✅ **Após Configuração**
- [ ] Sistema funcionando normalmente
- [ ] Emails sendo entregues
- [ ] Logs de email configurados (opcional)

---

## 💡 Dicas Importantes

### 🔒 **Segurança**
- **NUNCA** versione a senha de app
- **USE** .env para credenciais
- **ATIVE** logs para monitoramento
- **TESTE** regularmente o envio

### 🚀 **Performance**
- **CONFIGURE** timeout adequado
- **USE** connection pooling se necessário
- **MONITORE** limites do Gmail
- **IMPLEMENTE** retry para falhas

### 📈 **Produção**
- **CONFIGURE** domínio próprio (futuro)
- **USE** serviços dedicados (SendGrid, etc.)
- **MONITORE** reputação do sender
- **IMPLEMENTE** templates de email

---

**📧 Configuração Gmail SMTP pronta para implementação!**

**🚀 Sistema de email profissional para o Bolão Online!**