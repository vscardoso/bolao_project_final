@echo off
echo ========================================
echo SCRIPT DE RESET MYSQL - EXECUTAR COMO ADMINISTRADOR
echo ========================================
echo.

echo 1. Parando serviço MySQL...
net stop mysql80
if %errorlevel% neq 0 (
    echo ERRO: Não foi possível parar o MySQL. Execute como Administrador.
    pause
    exit /b 1
)

echo.
echo 2. Iniciando MySQL com reset de senha...
echo AVISO: Deixe este terminal aberto e execute os próximos passos em outro terminal
echo.
start "MySQL Reset" /wait mysqld --init-file=C:\mysql-init.txt --console

echo.
echo 3. Reiniciando MySQL normalmente...
net start mysql80

echo.
echo ========================================
echo RESET CONCLUÍDO!
echo Agora você pode conectar com: mysql -u root
echo ========================================
pause