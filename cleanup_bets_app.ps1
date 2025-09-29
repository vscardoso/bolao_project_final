# cleanup_bets_app.ps1
# Script PowerShell para limpeza consolidada do app bets

Write-Host "🧹 Iniciando limpeza do app bets..." -ForegroundColor Green

# 1. Auditoria
Write-Host "📊 1/8 - Executando auditoria..." -ForegroundColor Yellow
python find_bets_imports.py | Out-File -FilePath "bets_audit_report.txt" -Encoding UTF8

# 2. Backup antes de qualquer mudança
Write-Host "💾 2/8 - Criando backup..." -ForegroundColor Yellow
git add .
git commit -m "backup: antes de remover app bets"

# 3. Remover de INSTALLED_APPS (manual - pausar aqui)
Write-Host "✋ 3/8 - AÇÃO MANUAL: Remova 'bets' de INSTALLED_APPS em settings.py" -ForegroundColor Red
Read-Host "Pressione ENTER após remover 'bets' de INSTALLED_APPS"

# 4. Substituir imports
Write-Host "🔄 4/8 - Substituindo imports..." -ForegroundColor Yellow
echo "s" | python substituir_imports.py

# 5. Validar
Write-Host "✅ 5/8 - Validando mudanças..." -ForegroundColor Yellow
python manage.py check
python manage.py makemigrations
python manage.py migrate

# 6. Testes
Write-Host "🧪 6/8 - Executando testes..." -ForegroundColor Yellow
python manage.py test

# 7. Mover app bets para backup
Write-Host "📦 7/8 - Movendo app bets para backup..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "backups\removed_apps" | Out-Null
$backupName = "bets_$(Get-Date -Format 'yyyyMMdd')"
Move-Item -Path "bets" -Destination "backups\removed_apps\$backupName"

# 8. Commit final
Write-Host "💾 8/8 - Commitando mudanças..." -ForegroundColor Yellow
git add .
git commit -m "refactor: remove app bets após consolidação em pools"

Write-Host "✨ Limpeza concluída!" -ForegroundColor Green
Write-Host "📋 Relatório salvo em: bets_audit_report.txt" -ForegroundColor Cyan
Write-Host "💾 Backup do app bets em: backups/removed_apps/" -ForegroundColor Cyan

# Pausar para o usuário ver o resultado
Write-Host "`nPressione qualquer tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")