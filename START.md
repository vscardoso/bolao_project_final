# 🚀 INICIAR PROJETO - 1 CLIQUE

## ⚡ PASSO ÚNICO

1. **Botão direito** em `SETUP_MYSQL_COMPLETO.bat`
2. Selecione **"Executar como administrador"**
3. Aguarde finalizar
4. Execute: `python manage.py runserver`

---

## 📝 ALTERNATIVA: PowerShell Auto-Elevação

**Clique duplo em:** `SETUP_MYSQL_AUTO.ps1`

O PowerShell vai solicitar permissão de admin automaticamente.

---

## ✅ O que será feito automaticamente:

- ✅ Registrar serviço MySQL80
- ✅ Iniciar MySQL
- ✅ Criar banco `bolao_online`
- ✅ Criar usuário `bolao_user`
- ✅ Atualizar `.env` para MySQL
- ✅ Executar `python manage.py migrate`
- ✅ Exibir credenciais

---

## 🔑 Credenciais após setup:

```
MySQL Root:
  Usuário: root
  Senha: root_senha_123

Django/App:
  Usuário: bolao_user
  Senha: nova_senha_123
  Banco: bolao_online
```

---

## 🎯 Após finalizar:

```bash
python manage.py createsuperuser
python manage.py runserver
```

Acesse: http://localhost:8000
