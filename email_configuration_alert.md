# 🚨 AVISO IMPORTANTE - Configuração de Email

**Data**: 29/09/2025  
**Status**: ❌ **CONFIGURAÇÃO REQUER ATENÇÃO**  

---

## ⚠️ **PROBLEMA IDENTIFICADO**

### 📧 **Email configurado**: `jogador.lastshelter@gmail.com`
### 🔐 **Senha fornecida**: `Maria@8822` (senha regular)

### ❌ **ERRO**: Gmail não aceita senhas regulares para SMTP
```
Error: (535, 'Username and Password not accepted')
```

---

## 🔧 **SOLUÇÃO NECESSÁRIA**

O Gmail **EXIGE** senha de app para SMTP (não a senha da conta). Você precisa:

### 1️⃣ **Ativar Verificação em 2 Etapas**
- Acesse: https://myaccount.google.com/security
- Procure "Verificação em duas etapas"
- Ative usando SMS ou app autenticador

### 2️⃣ **Gerar Senha de App**
- Acesse: https://myaccount.google.com/apppasswords
- Selecione "Email" 
- Digite "Django Bolao"
- **Copie a senha de 16 caracteres** (ex: `abcd efgh ijkl mnop`)

### 3️⃣ **Atualizar .env**
Substitua no arquivo `.env`:
```env
EMAIL_HOST_PASSWORD=Maria@8822
```
Por:
```env
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
```
(usando a senha de app real gerada)

---

## 🔄 **ALTERNATIVAS**

### **Opção A**: Usar senha de app (recomendado)
- ✅ Mais seguro
- ✅ Funciona com 2FA
- ✅ Gmail recomenda

### **Opção B**: Configurar para desenvolvimento
Se for apenas para testes locais:
```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### **Opção C**: Usar outro provedor
- SendGrid, Mailgun, ou Amazon SES
- Não exigem configurações especiais

---

## 📋 **PRÓXIMOS PASSOS**

### 🎯 **Para continuar com Gmail**:
1. Ative 2FA na conta `jogador.lastshelter@gmail.com`
2. Gere senha de app
3. Atualize `.env` com a nova senha
4. Teste novamente: `python test_email.py`

### 🎯 **Para desenvolvimento rápido**:
```bash
# Voltar para modo console (emails no terminal)
python -c "
with open('.env', 'r') as f: content = f.read()
content = content.replace('EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend', 'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend')
with open('.env', 'w') as f: f.write(content)
print('✅ Email configurado para modo console (desenvolvimento)')
"
```

---

## 💡 **LEMBRETE**

### 🔒 **Segurança Gmail**:
- Gmail **NUNCA** aceita senha principal para SMTP
- **SEMPRE** usar senha de app (16 caracteres)
- **OBRIGATÓRIO** ter 2FA ativado

### 🚀 **Para produção**:
- Recomendo usar serviços dedicados (SendGrid, etc.)
- Gmail tem limite de 500 emails/dia
- Senhas de app são mais seguras

---

**🎯 Escolha uma das opções acima para continuar!**