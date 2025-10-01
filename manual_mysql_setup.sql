# SCRIPT COMPLETO DE CONFIGURAÇÃO MYSQL
# Execute este script LINHA POR LINHA no MySQL após resetar a senha do root

# 1. Conectar como root
# mysql -u root

# 2. Executar os comandos abaixo um por um:

-- Remover usuários antigos se existirem
DROP USER IF EXISTS 'bolao_user'@'localhost';
DROP USER IF EXISTS 'bolao_user'@'%';

-- Criar/recriar banco de dados
DROP DATABASE IF EXISTS bolao_online;
CREATE DATABASE bolao_online CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário com autenticação nativa
CREATE USER 'bolao_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'nova_senha_123';

-- Dar todas as permissões
GRANT ALL PRIVILEGES ON bolao_online.* TO 'bolao_user'@'localhost';

-- Aplicar mudanças
FLUSH PRIVILEGES;

-- Verificar criação
SELECT user, host, plugin FROM mysql.user WHERE user = 'bolao_user';

-- Testar permissões
SHOW GRANTS FOR 'bolao_user'@'localhost';

-- Sair do MySQL e testar conexão:
-- mysql -u bolao_user -pnova_senha_123 bolao_online