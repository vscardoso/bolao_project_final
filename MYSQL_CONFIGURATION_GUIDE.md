# 🔧 GUIA PARA CONFIGURAR MYSQL - PASSO A PASSO

## 🚨 PROBLEMA IDENTIFICADO
- MySQL está rodando ✅
- Mas não conseguimos conectar (credenciais incorretas)
- Precisamos descobrir a senha do root ou criar novo usuário

## 🔧 OPÇÕES PARA RESOLVER

### **OPÇÃO 1: RESETAR SENHA DO MYSQL ROOT**

#### Passo 1: Parar o serviço MySQL
```powershell
net stop MySQL80
```

#### Passo 2: Iniciar MySQL em modo seguro
```powershell
# Navegue até o diretório do MySQL (geralmente):
cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"

# Inicie em modo seguro
mysqld --skip-grant-tables --skip-networking
```

#### Passo 3: Em outro terminal, conecte sem senha
```powershell
mysql -u root
```

#### Passo 4: Resetar senha do root
```sql
USE mysql;
ALTER USER 'root'@'localhost' IDENTIFIED BY 'nova_senha_123';
FLUSH PRIVILEGES;
EXIT;
```

#### Passo 5: Reiniciar MySQL normalmente
```powershell
net start MySQL80
```

---

### **OPÇÃO 2: TENTAR SENHAS COMUNS**

Teste essas senhas comuns para root:
- (vazia)
- root
- password
- admin
- 123456
- mysql

#### Teste manual:
```powershell
mysql -u root -p
# Digite cada senha quando solicitado
```

---

### **OPÇÃO 3: USAR SQLITE TEMPORARIAMENTE**

Se não conseguir configurar MySQL agora, posso configurar SQLite:

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

---

## 🎯 RECOMENDAÇÃO

**Execute primeiro a OPÇÃO 2** (testar senhas comuns).

Se não funcionar, me informe e eu configuro SQLite temporariamente para o projeto funcionar.

## 📞 PRÓXIMO PASSO

Depois que descobrir a senha do MySQL:

1. **Atualize o .env**:
```env
DB_PASSWORD=sua_senha_descoberta
```

2. **Crie o banco de dados**:
```sql
CREATE DATABASE bolao_online CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. **Execute migrações**:
```bash
python manage.py migrate
```

## 🔄 ALTERNATIVA RÁPIDA

Se quiser que eu configure **SQLite temporariamente** para o projeto funcionar agora, me avise!