# ========================================
# SETUP COMPLETO MYSQL + DJANGO
# Auto-eleva para Administrador
# ========================================

# Verificar e solicitar privilégios de administrador
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "SOLICITANDO PRIVILEGIOS DE ADMINISTRADOR" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Aguarde... uma janela UAC sera exibida." -ForegroundColor Cyan
    Write-Host ""

    # Reexecutar como administrador
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SETUP COMPLETO - BOLAO ONLINE + MYSQL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[OK] Executando como Administrador" -ForegroundColor Green
Write-Host ""

# ========================================
# PASSO 1: REGISTRAR E INICIAR SERVICO MYSQL
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 1/6: Instalando Servico MySQL80" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$service = Get-Service -Name "MySQL80" -ErrorAction SilentlyContinue

if ($service -and $service.Status -eq "Running") {
    Write-Host "[OK] Servico MySQL80 ja esta rodando!" -ForegroundColor Green
} elseif ($service) {
    Write-Host "[INFO] Servico MySQL80 registrado, iniciando..." -ForegroundColor Yellow
    Start-Service -Name "MySQL80"
    Write-Host "[OK] Servico MySQL80 iniciado!" -ForegroundColor Green
} else {
    Write-Host "[INFO] Registrando servico MySQL80..." -ForegroundColor Yellow

    $mysqldPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe"
    $configPath = "C:\ProgramData\MySQL\MySQL Server 8.0\my.ini"

    & $mysqldPath --install MySQL80 --defaults-file="$configPath"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha ao registrar servico MySQL80" -ForegroundColor Red
        pause
        exit 1
    }

    Write-Host "[OK] Servico MySQL80 registrado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[INFO] Iniciando servico MySQL80..." -ForegroundColor Yellow

    Start-Service -Name "MySQL80"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha ao iniciar servico MySQL80" -ForegroundColor Red
        pause
        exit 1
    }

    Write-Host "[OK] Servico MySQL80 iniciado com sucesso!" -ForegroundColor Green
}

Write-Host ""

# ========================================
# PASSO 2: CONFIGURAR BANCO E USUARIOS
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 2/6: Configurando Banco e Usuarios" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$mysqlPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$setupSQL = @"
CREATE DATABASE IF NOT EXISTS bolao_online CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP USER IF EXISTS 'bolao_user'@'localhost';
CREATE USER 'bolao_user'@'localhost' IDENTIFIED BY 'nova_senha_123';
GRANT ALL PRIVILEGES ON bolao_online.* TO 'bolao_user'@'localhost';
FLUSH PRIVILEGES;
"@

$setupSQL | Out-File -FilePath "temp_setup.sql" -Encoding ASCII

$connected = $false

# Tentar sem senha
Write-Host "[INFO] Tentando conectar como root (sem senha)..." -ForegroundColor Yellow
& $mysqlPath -u root --skip-password -e "source temp_setup.sql" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Banco configurado com sucesso!" -ForegroundColor Green

    # Definir senha root
    "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root_senha_123'; FLUSH PRIVILEGES;" | Out-File -FilePath "temp_root.sql" -Encoding ASCII
    & $mysqlPath -u root --skip-password -e "source temp_root.sql" 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Senha root definida: root_senha_123" -ForegroundColor Green
    }

    Remove-Item "temp_root.sql" -ErrorAction SilentlyContinue
    $connected = $true
}

# Tentar com senha root_senha_123
if (-not $connected) {
    Write-Host "[INFO] Tentando conectar como root (senha: root_senha_123)..." -ForegroundColor Yellow
    & $mysqlPath -u root -proot_senha_123 -e "source temp_setup.sql" 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Banco configurado com sucesso!" -ForegroundColor Green
        $connected = $true
    }
}

# Tentar com senha root
if (-not $connected) {
    Write-Host "[INFO] Tentando conectar como root (senha: root)..." -ForegroundColor Yellow
    & $mysqlPath -u root -proot -e "source temp_setup.sql" 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Banco configurado com sucesso!" -ForegroundColor Green
        $connected = $true
    }
}

Remove-Item "temp_setup.sql" -ErrorAction SilentlyContinue

if (-not $connected) {
    Write-Host ""
    Write-Host "[ERRO] Nao foi possivel conectar ao MySQL" -ForegroundColor Red
    Write-Host "Execute manualmente: mysql -u root -p" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# ========================================
# PASSO 3: ATUALIZAR .ENV PARA MYSQL
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 3/6: Atualizando .env para MySQL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Backup do .env
Copy-Item ".env" ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')" -ErrorAction SilentlyContinue
Write-Host "[OK] Backup do .env criado" -ForegroundColor Green

# Atualizar .env
$envContent = @"
# ========================================
# CONFIGURACOES DJANGO - MYSQL ATIVO
# ========================================

# Nova SECRET_KEY gerada em 30/09/2025 - Maxima Seguranca
SECRET_KEY=5l9mho!7`$m)ffadw7#q6all19p8ff3w*+5-2c0pm7`$2hrfym=)

# Ambiente
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*.localhost,0.0.0.0

# URL do site
SITE_URL=http://localhost:8000

# ========================================
# BANCO DE DADOS - MYSQL ATIVO
# ========================================

DB_ENGINE=django.db.backends.mysql
DB_NAME=bolao_online
DB_USER=bolao_user
DB_PASSWORD=nova_senha_123
DB_HOST=localhost
DB_PORT=3306

# ========================================
# EMAIL - CONFIGURACAO TEMPORARIA SEGURA
# ========================================

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# ========================================
# APIs EXTERNAS
# ========================================

FOOTBALL_API_KEY=SUA_NOVA_CHAVE_API_AQUI

# ========================================
# SESSAO E AUTENTICACAO
# ========================================

INACTIVITY_TIMEOUT=30
SESSION_COOKIE_AGE=7200

# ========================================
# ARQUIVOS ESTATICOS
# ========================================

STATIC_URL=/static/
STATIC_ROOT=staticfiles/
MEDIA_URL=/media/
MEDIA_ROOT=media/

# ========================================
# CRISPY FORMS
# ========================================

CRISPY_ALLOWED_TEMPLATE_PACKS=bootstrap5
CRISPY_TEMPLATE_PACK=bootstrap5

# ========================================
# SEGURANCA PRODUCAO
# ========================================

CSRF_COOKIE_SECURE=False
SESSION_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_SSL_REDIRECT=False
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "[OK] .env atualizado para MySQL!" -ForegroundColor Green

# ========================================
# PASSO 4: TESTAR CONEXAO DJANGO
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 4/6: Testando Conexao Django" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python manage.py check --database default

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Django nao conseguiu conectar ao MySQL" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[OK] Conexao Django -> MySQL funcionando!" -ForegroundColor Green

# ========================================
# PASSO 5: EXECUTAR MIGRACOES DJANGO
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PASSO 5/6: Executando Migracoes Django" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Falha ao aplicar migracoes" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[OK] Migracoes aplicadas com sucesso!" -ForegroundColor Green

# ========================================
# PASSO 6: RESUMO FINAL
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "PASSO 6/6: Setup Concluido!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[SUCESSO] Projeto configurado com MySQL!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CREDENCIAIS MYSQL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ROOT (Administrador):" -ForegroundColor Yellow
Write-Host "  Usuario: root"
Write-Host "  Senha: root_senha_123"
Write-Host ""
Write-Host "APLICACAO (Django):" -ForegroundColor Yellow
Write-Host "  Usuario: bolao_user"
Write-Host "  Senha: nova_senha_123"
Write-Host "  Banco: bolao_online"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Criar superusuario Django:" -ForegroundColor Yellow
Write-Host "   python manage.py createsuperuser"
Write-Host ""
Write-Host "2. Iniciar servidor:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver"
Write-Host ""
Write-Host "3. Acessar: http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Read-Host "Pressione ENTER para fechar"
