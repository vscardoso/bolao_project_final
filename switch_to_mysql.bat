@echo off
REM ========================================
REM ALTERNAR DJANGO PARA MYSQL
REM Execute APÓS configurar MySQL com sucesso
REM ========================================

echo.
echo ========================================
echo ALTERANDO DJANGO PARA MYSQL
echo ========================================
echo.

REM Verificar se MySQL está rodando
sc query MySQL80 | find "RUNNING" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Servico MySQL80 nao esta rodando!
    echo Execute primeiro: install_mysql_service.bat
    pause
    exit /b 1
)

REM Testar conexão com bolao_user
echo Testando conexao com bolao_user...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u bolao_user -pnova_senha_123 -e "SELECT 1;" 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Usuario bolao_user nao esta configurado!
    echo Execute primeiro: configure_mysql_complete.bat
    pause
    exit /b 1
)

echo OK: Conexao MySQL funcionando!
echo.

REM Fazer backup do .env
echo Criando backup do .env...
copy .env .env.backup.sqlite 2>nul

REM Atualizar .env para MySQL
echo Atualizando .env para MySQL...

(
echo # ========================================
echo # CONFIGURAÇÕES DJANGO - MYSQL ATIVO
echo # ========================================
echo.
echo # Nova SECRET_KEY gerada em 30/09/2025 - Máxima Segurança
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
echo # EMAIL - CONFIGURAÇÃO TEMPORÁRIA SEGURA
echo # ========================================
echo.
echo # Modo console para desenvolvimento ^(SEGURO^)
echo EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
echo.
echo # ========================================
echo # APIs EXTERNAS - NOVAS CREDENCIAIS
echo # ========================================
echo.
echo # Football-Data.org API ^(CONFIGURAR NOVA CHAVE^)
echo FOOTBALL_API_KEY=SUA_NOVA_CHAVE_API_AQUI
echo.
echo # ========================================
echo # SESSÃO E AUTENTICAÇÃO
echo # ========================================
echo.
echo INACTIVITY_TIMEOUT=30
echo SESSION_COOKIE_AGE=7200
echo.
echo # ========================================
echo # ARQUIVOS ESTÁTICOS
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
echo # SEGURANÇA PRODUÇÃO
echo # ========================================
echo.
echo # CSRF e Cookies
echo CSRF_COOKIE_SECURE=False
echo SESSION_COOKIE_SECURE=False
echo.
echo # HSTS
echo SECURE_HSTS_SECONDS=0
echo SECURE_SSL_REDIRECT=False
) > .env

echo OK: .env atualizado para MySQL!
echo.
echo ========================================
echo TESTANDO DJANGO COM MYSQL
echo ========================================
echo.

echo Testando conexao Django...
python manage.py check --database default

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCESSO! Django conectado ao MySQL!
    echo ========================================
    echo.
    echo Proximos passos:
    echo 1. python manage.py migrate
    echo 2. python manage.py createsuperuser
    echo 3. python manage.py runserver
    echo.
) else (
    echo.
    echo ERRO: Django nao conseguiu conectar ao MySQL
    echo Restaurando backup SQLite...
    copy .env.backup.sqlite .env 2>nul
    echo.
    echo Verifique:
    echo 1. mysqlclient instalado: pip install mysqlclient
    echo 2. Credenciais corretas no MySQL
    echo.
)

pause
