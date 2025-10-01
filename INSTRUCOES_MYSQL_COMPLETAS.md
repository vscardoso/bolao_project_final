# 🚀 INSTRUÇÕES COMPLETAS - RECUPERAÇÃO MYSQL

## 📋 RESUMO DO PROBLEMA

O MySQL está **instalado mas sem serviço Windows registrado**, impedindo qualquer conexão.

---

## ✅ SOLUÇÃO COMPLETA (3 Passos)

### **PASSO 1: Instalar Serviço MySQL** ⚠️ REQUER ADMINISTRADOR

1. **Botão direito** em `install_mysql_service.bat`
2. Selecione **"Executar como administrador"**
3. Aguarde mensagem: `Serviço MySQL80 iniciado com sucesso!`

**O que faz:**
- Registra `MySQL80` como serviço Windows
- Inicia o servidor MySQL
- Verifica status

---

### **PASSO 2: Configurar Banco e Usuários**

Execute normalmente (não precisa admin):
```batch
configure_mysql_complete.bat
```

**O que faz:**
- Testa 3 senhas root comuns (sem senha, "root", "password")
- Cria banco `bolao_online`
- Cria usuário `bolao_user` / senha `nova_senha_123`
- Define senha root como `root_senha_123`
- Exibe credenciais finais

**Credenciais após este passo:**
```
ROOT:
  Usuário: root
  Senha: root_senha_123

APLICAÇÃO:
  Usuário: bolao_user
  Senha: nova_senha_123
  Banco: bolao_online
```

---

### **PASSO 3: Ativar MySQL no Django**

Execute normalmente:
```batch
switch_to_mysql.bat
```

**O que faz:**
- Verifica serviço MySQL rodando
- Testa conexão com `bolao_user`
- Faz backup do `.env` atual (`.env.backup.sqlite`)
- Atualiza `.env` para usar MySQL
- Testa conexão Django → MySQL

---

## 🔄 PASSO 4: Migrar Banco de Dados

Após tudo funcionando:

```batch
# 1. Aplicar migrações
python manage.py migrate

# 2. Criar superusuário admin
python manage.py createsuperuser

# 3. Iniciar servidor
python manage.py runserver
```

---

## ⚠️ SOLUÇÃO DE PROBLEMAS

### **Erro: "Install/Remove of the Service Denied!"**
→ Você NÃO executou como administrador. Clique com botão direito → "Executar como administrador"

### **Erro: "Serviço MySQL80 não encontrado"**
→ Passo 1 não foi concluído. Execute `install_mysql_service.bat` como admin.

### **Erro: MySQL não aceita conexão sem senha**
→ MySQL tem senha root definida. Opções:

**Opção A: Reset senha manualmente**
```batch
# 1. Parar serviço
net stop MySQL80

# 2. Iniciar em modo seguro
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --skip-grant-tables --console

# 3. Em OUTRO CMD, conectar e resetar senha
mysql -u root
```
```sql
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'root_senha_123';
FLUSH PRIVILEGES;
EXIT;
```

**Opção B: Usar MySQL Installer**
1. Abrir MySQL Installer
2. Reconfigure MySQL Server 8.0
3. Definir nova senha root

### **Erro: Django não conecta ao MySQL**
```batch
# Instalar driver MySQL
pip install mysqlclient

# Se falhar, alternativa:
pip install pymysql
```

Depois adicionar em `bolao_config/__init__.py`:
```python
import pymysql
pymysql.install_as_MySQLdb()
```

---

## 📁 ARQUIVOS CRIADOS

| Arquivo | Função |
|---------|--------|
| `install_mysql_service.bat` | Registra e inicia serviço MySQL80 (ADMIN) |
| `configure_mysql_complete.bat` | Cria banco e usuários |
| `switch_to_mysql.bat` | Ativa MySQL no Django |
| `manual_mysql_setup.sql` | Comandos SQL para configuração manual |

---

## 🎯 ORDEM DE EXECUÇÃO

```
1. install_mysql_service.bat (COMO ADMIN)
   ↓
2. configure_mysql_complete.bat
   ↓
3. switch_to_mysql.bat
   ↓
4. python manage.py migrate
   ↓
5. python manage.py createsuperuser
   ↓
6. python manage.py runserver
```

---

## 📞 VERIFICAÇÕES ÚTEIS

```batch
# Ver status do serviço
sc query MySQL80

# Conectar ao MySQL
mysql -u root -proot_senha_123

# Testar conexão aplicação
mysql -u bolao_user -pnova_senha_123 -D bolao_online

# Ver logs MySQL
type "C:\ProgramData\MySQL\MySQL Server 8.0\Data\KYROS.err"
```

---

## 💾 BACKUP/RESTORE

### Voltar para SQLite
```batch
copy .env.backup.sqlite .env
python manage.py migrate
```

### Backup do banco MySQL
```batch
mysqldump -u bolao_user -pnova_senha_123 bolao_online > backup.sql
```

### Restore do backup
```batch
mysql -u bolao_user -pnova_senha_123 bolao_online < backup.sql
```
