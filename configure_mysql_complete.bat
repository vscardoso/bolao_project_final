@echo off
REM ========================================
REM CONFIGURAÇÃO COMPLETA MYSQL
REM Execute APÓS instalar o serviço
REM ========================================

echo.
echo ========================================
echo CONFIGURACAO MYSQL - BOLAO ONLINE
echo ========================================
echo.

REM Verificar se o serviço está rodando
sc query MySQL80 | find "RUNNING" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Servico MySQL80 nao esta rodando!
    echo Execute primeiro: install_mysql_service.bat como ADMINISTRADOR
    pause
    exit /b 1
)

echo Servico MySQL80 detectado e rodando!
echo.

REM Criar arquivo SQL temporário
echo CREATE DATABASE IF NOT EXISTS bolao_online CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; > temp_mysql_setup.sql
echo. >> temp_mysql_setup.sql
echo -- Criar usuario bolao_user >> temp_mysql_setup.sql
echo DROP USER IF EXISTS 'bolao_user'@'localhost'; >> temp_mysql_setup.sql
echo CREATE USER 'bolao_user'@'localhost' IDENTIFIED BY 'nova_senha_123'; >> temp_mysql_setup.sql
echo. >> temp_mysql_setup.sql
echo -- Conceder privilegios >> temp_mysql_setup.sql
echo GRANT ALL PRIVILEGES ON bolao_online.* TO 'bolao_user'@'localhost'; >> temp_mysql_setup.sql
echo FLUSH PRIVILEGES; >> temp_mysql_setup.sql
echo. >> temp_mysql_setup.sql
echo -- Verificar usuarios >> temp_mysql_setup.sql
echo SELECT User, Host FROM mysql.user WHERE User IN ('root', 'bolao_user'); >> temp_mysql_setup.sql
echo. >> temp_mysql_setup.sql
echo -- Verificar bancos >> temp_mysql_setup.sql
echo SHOW DATABASES; >> temp_mysql_setup.sql

echo.
echo ========================================
echo TENTANDO CONECTAR AO MYSQL...
echo ========================================
echo.
echo OPCAO 1: Tentando root sem senha...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root --skip-password < temp_mysql_setup.sql 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Configuracao concluida!
    echo ========================================
    echo.
    echo Banco criado: bolao_online
    echo Usuario criado: bolao_user
    echo Senha: nova_senha_123
    echo.
    echo IMPORTANTE: Definir senha do root agora...
    echo.

    REM Definir senha do root
    echo ALTER USER 'root'@'localhost' IDENTIFIED BY 'root_senha_123'; > temp_root_password.sql
    echo FLUSH PRIVILEGES; >> temp_root_password.sql

    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root --skip-password < temp_root_password.sql 2>nul

    if %ERRORLEVEL% EQU 0 (
        echo OK: Senha do root definida como 'root_senha_123'
        echo.
        echo GUARDE ESTAS CREDENCIAIS:
        echo --------------------------
        echo ROOT:
        echo   Usuario: root
        echo   Senha: root_senha_123
        echo.
        echo APLICACAO:
        echo   Usuario: bolao_user
        echo   Senha: nova_senha_123
        echo   Banco: bolao_online
        echo.
    )

    del temp_root_password.sql 2>nul
    del temp_mysql_setup.sql 2>nul

    echo Agora execute: python manage.py migrate
    echo.
    pause
    exit /b 0
)

echo.
echo OPCAO 2: Tentando root com senha 'root'...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -proot < temp_mysql_setup.sql 2>nul

if %ERRORLEVEL% EQU 0 (
    echo SUCESSO com senha 'root'!
    del temp_mysql_setup.sql 2>nul
    pause
    exit /b 0
)

echo.
echo OPCAO 3: Tentando root com senha 'password'...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -ppassword < temp_mysql_setup.sql 2>nul

if %ERRORLEVEL% EQU 0 (
    echo SUCESSO com senha 'password'!
    del temp_mysql_setup.sql 2>nul
    pause
    exit /b 0
)

echo.
echo ========================================
echo ERRO: Nao foi possivel conectar ao MySQL
echo ========================================
echo.
echo O MySQL pode ter uma senha root definida.
echo.
echo SOLUCAO MANUAL:
echo 1. Abra um novo CMD
echo 2. Execute: mysql -u root -p
echo 3. Digite a senha quando solicitado
echo 4. Execute os comandos do arquivo: manual_mysql_setup.sql
echo.

del temp_mysql_setup.sql 2>nul
pause
