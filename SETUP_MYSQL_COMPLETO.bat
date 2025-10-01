@echo off
REM ========================================
REM SETUP COMPLETO MYSQL + DJANGO
REM Execute como ADMINISTRADOR
REM ========================================

echo.
echo ========================================
echo SETUP COMPLETO - BOLAO ONLINE + MYSQL
echo ========================================
echo.

REM Verificar se está rodando como administrador
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Este script precisa ser executado como ADMINISTRADOR!
    echo.
    echo Clique com botao direito neste arquivo e selecione:
    echo "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Executando como Administrador
echo.

REM ========================================
REM PASSO 1: REGISTRAR E INICIAR SERVICO MYSQL
REM ========================================

echo ========================================
echo PASSO 1/6: Instalando Servico MySQL80
echo ========================================
echo.

sc query MySQL80 | find "RUNNING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Servico MySQL80 ja esta rodando!
    goto :configure_mysql
)

sc query MySQL80 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Servico MySQL80 ja esta registrado, apenas iniciando...
    net start MySQL80
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao iniciar servico MySQL80
        pause
        exit /b 1
    )
    echo [OK] Servico MySQL80 iniciado!
    goto :configure_mysql
)

echo [INFO] Registrando servico MySQL80...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --install MySQL80 --defaults-file="C:\ProgramData\MySQL\MySQL Server 8.0\my.ini"

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao registrar servico MySQL80
    pause
    exit /b 1
)

echo [OK] Servico MySQL80 registrado!
echo.

echo [INFO] Iniciando servico MySQL80...
net start MySQL80

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao iniciar servico MySQL80
    pause
    exit /b 1
)

echo [OK] Servico MySQL80 iniciado com sucesso!
echo.

REM ========================================
REM PASSO 2: CONFIGURAR BANCO E USUARIOS
REM ========================================

:configure_mysql
echo ========================================
echo PASSO 2/6: Configurando Banco e Usuarios
echo ========================================
echo.

REM Criar arquivo SQL de configuração
echo CREATE DATABASE IF NOT EXISTS bolao_online CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; > temp_setup.sql
echo DROP USER IF EXISTS 'bolao_user'@'localhost'; >> temp_setup.sql
echo CREATE USER 'bolao_user'@'localhost' IDENTIFIED BY 'nova_senha_123'; >> temp_setup.sql
echo GRANT ALL PRIVILEGES ON bolao_online.* TO 'bolao_user'@'localhost'; >> temp_setup.sql
echo FLUSH PRIVILEGES; >> temp_setup.sql

REM Tentar conectar sem senha
echo [INFO] Tentando conectar como root (sem senha)...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root --skip-password < temp_setup.sql 2>nul

if %ERRORLEVEL% EQU 0 (
    echo [OK] Banco configurado com sucesso!

    REM Definir senha do root
    echo ALTER USER 'root'@'localhost' IDENTIFIED BY 'root_senha_123'; > temp_root.sql
    echo FLUSH PRIVILEGES; >> temp_root.sql
    "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root --skip-password < temp_root.sql 2>nul

    if %ERRORLEVEL% EQU 0 (
        echo [OK] Senha root definida: root_senha_123
    )

    del temp_root.sql 2>nul
    goto :install_python_deps
)

REM Tentar com senha root
echo [INFO] Tentando conectar como root (senha: root)...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -proot < temp_setup.sql 2>nul

if %ERRORLEVEL% EQU 0 (
    echo [OK] Banco configurado com sucesso!
    goto :install_python_deps
)

REM Tentar com senha root_senha_123
echo [INFO] Tentando conectar como root (senha: root_senha_123)...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -proot_senha_123 < temp_setup.sql 2>nul

if %ERRORLEVEL% EQU 0 (
    echo [OK] Banco configurado com sucesso!
    goto :install_python_deps
)

echo.
echo [AVISO] Nao foi possivel conectar automaticamente ao MySQL
echo A senha root pode ser diferente das testadas.
echo.
echo Execute manualmente:
echo mysql -u root -p
echo (digite sua senha root quando solicitado)
echo.
echo Depois execute os comandos em: manual_mysql_setup.sql
echo.
del temp_setup.sql 2>nul
pause
exit /b 1

REM ========================================
REM PASSO 3: INSTALAR DEPENDENCIAS PYTHON
REM ========================================

:install_python_deps
del temp_setup.sql 2>nul

echo.
echo ========================================
echo PASSO 3/6: Instalando mysqlclient
echo ========================================
echo.

pip show mysqlclient >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] mysqlclient ja esta instalado!
) else (
    echo [INFO] Instalando mysqlclient...
    pip install mysqlclient

    if %ERRORLEVEL% NEQ 0 (
        echo [AVISO] Falha ao instalar mysqlclient
        echo Tentando alternativa pymysql...
        pip install pymysql

        if %ERRORLEVEL% NEQ 0 (
            echo [ERRO] Falha ao instalar driver MySQL
            pause
            exit /b 1
        )

        echo [OK] pymysql instalado como alternativa

        REM Configurar pymysql
        echo import pymysql > bolao_config\__init__.py
        echo pymysql.install_as_MySQLdb^(^) >> bolao_config\__init__.py
        echo [OK] pymysql configurado em bolao_config/__init__.py
    ) else (
        echo [OK] mysqlclient instalado com sucesso!
    )
)

REM ========================================
REM PASSO 4: ATUALIZAR .ENV PARA MYSQL
REM ========================================

echo.
echo ========================================
echo PASSO 4/6: Atualizando .env para MySQL
echo ========================================
echo.

REM Backup do .env
copy .env .env.backup.%DATE:/=%.%TIME::=% >nul 2>&1
echo [OK] Backup do .env criado

REM Atualizar .env
(
echo # ========================================
echo # CONFIGURACOES DJANGO - MYSQL ATIVO
echo # ========================================
echo.
echo # Nova SECRET_KEY gerada em 30/09/2025 - Maxima Seguranca
echo SECRET_KEY=5l9mho!7$m)ffadw7#q6all19p8ff3w*+5-2c0pm7$2hrfym=^)
echo.
echo # Ambiente
echo DEBUG=True
echo ALLOWED_HOSTS=localhost,127.0.0.1,*.localhost,0.0.0.0
echo.
echo # URL do site
echo SITE_URL=http://localhost:8000
echo.
echo # ========================================
echo # BANCO DE DADOS - MYSQL ATIVO
echo # ========================================
echo.
echo DB_ENGINE=django.db.backends.mysql
echo DB_NAME=bolao_online
echo DB_USER=bolao_user
echo DB_PASSWORD=nova_senha_123
echo DB_HOST=localhost
echo DB_PORT=3306
echo.
echo # ========================================
echo # EMAIL - CONFIGURACAO TEMPORARIA SEGURA
echo # ========================================
echo.
echo EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
echo.
echo # ========================================
echo # APIs EXTERNAS
echo # ========================================
echo.
echo FOOTBALL_API_KEY=SUA_NOVA_CHAVE_API_AQUI
echo.
echo # ========================================
echo # SESSAO E AUTENTICACAO
echo # ========================================
echo.
echo INACTIVITY_TIMEOUT=30
echo SESSION_COOKIE_AGE=7200
echo.
echo # ========================================
echo # ARQUIVOS ESTATICOS
echo # ========================================
echo.
echo STATIC_URL=/static/
echo STATIC_ROOT=staticfiles/
echo MEDIA_URL=/media/
echo MEDIA_ROOT=media/
echo.
echo # ========================================
echo # CRISPY FORMS
echo # ========================================
echo.
echo CRISPY_ALLOWED_TEMPLATE_PACKS=bootstrap5
echo CRISPY_TEMPLATE_PACK=bootstrap5
echo.
echo # ========================================
echo # SEGURANCA PRODUCAO
echo # ========================================
echo.
echo CSRF_COOKIE_SECURE=False
echo SESSION_COOKIE_SECURE=False
echo SECURE_HSTS_SECONDS=0
echo SECURE_SSL_REDIRECT=False
) > .env

echo [OK] .env atualizado para MySQL!

REM ========================================
REM PASSO 5: EXECUTAR MIGRACOES DJANGO
REM ========================================

echo.
echo ========================================
echo PASSO 5/6: Executando Migracoes Django
echo ========================================
echo.

python manage.py check --database default

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Django nao conseguiu conectar ao MySQL
    echo Verifique as credenciais e tente novamente
    pause
    exit /b 1
)

echo [OK] Conexao Django -> MySQL funcionando!
echo.

echo [INFO] Aplicando migracoes...
python manage.py migrate

if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao aplicar migracoes
    pause
    exit /b 1
)

echo [OK] Migracoes aplicadas com sucesso!

REM ========================================
REM PASSO 6: RESUMO FINAL
REM ========================================

echo.
echo ========================================
echo PASSO 6/6: Setup Concluido!
echo ========================================
echo.
echo [SUCESSO] Projeto configurado com MySQL!
echo.
echo ========================================
echo CREDENCIAIS MYSQL
echo ========================================
echo.
echo ROOT (Administrador):
echo   Usuario: root
echo   Senha: root_senha_123
echo.
echo APLICACAO (Django):
echo   Usuario: bolao_user
echo   Senha: nova_senha_123
echo   Banco: bolao_online
echo.
echo ========================================
echo PROXIMOS PASSOS
echo ========================================
echo.
echo 1. Criar superusuario Django:
echo    python manage.py createsuperuser
echo.
echo 2. Iniciar servidor:
echo    python manage.py runserver
echo.
echo 3. Acessar: http://localhost:8000
echo.
echo ========================================
echo.

pause
