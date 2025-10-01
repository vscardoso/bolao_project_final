# SCRIPT DE CONFIGURAÇÃO MYSQL APÓS RESET
# Execute este script depois de rodar reset_mysql.bat como administrador

# 1. Conectar como root (sem senha após reset)
mysql -u root -e "
-- Remover usuários antigos se existirem
DROP USER IF EXISTS 'bolao_user'@'localhost';

-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS bolao_online CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário bolao_user com nova senha
CREATE USER 'bolao_user'@'localhost' IDENTIFIED BY 'nova_senha_123';

-- Dar todas as permissões para o banco bolao_online
GRANT ALL PRIVILEGES ON bolao_online.* TO 'bolao_user'@'localhost';

-- Aplicar mudanças
FLUSH PRIVILEGES;

-- Mostrar usuários criados
SELECT user, host FROM mysql.user WHERE user IN ('root', 'bolao_user');
"

echo "✅ CONFIGURAÇÃO MYSQL CONCLUÍDA!"
echo "Usuário: bolao_user"
echo "Senha: nova_senha_123"
echo "Banco: bolao_online"