@echo off
REM ========================================
REM INSTALAR SERVIÇO MYSQL80
REM Execute este arquivo como ADMINISTRADOR
REM ========================================

echo.
echo ========================================
echo INSTALANDO SERVICO MYSQL80
echo ========================================
echo.

REM 1. Registrar o serviço
echo [1/3] Registrando servico MySQL80...
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --install MySQL80 --defaults-file="C:\ProgramData\MySQL\MySQL Server 8.0\my.ini"

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao registrar servico. Execute este arquivo como ADMINISTRADOR!
    pause
    exit /b 1
)

echo OK: Servico MySQL80 registrado com sucesso!
echo.

REM 2. Iniciar o serviço
echo [2/3] Iniciando servico MySQL80...
net start MySQL80

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao iniciar servico MySQL80
    pause
    exit /b 1
)

echo OK: Servico MySQL80 iniciado com sucesso!
echo.

REM 3. Verificar status
echo [3/3] Verificando status do servico...
sc query MySQL80

echo.
echo ========================================
echo INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Proximo passo: Execute 'configure_mysql.bat' para configurar usuarios e banco
echo.
pause
