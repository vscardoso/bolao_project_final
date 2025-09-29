#!/bin/bash
# cleanup_bets_app.sh

echo "🧹 Iniciando limpeza do app bets..."

# 1. Auditoria
echo "📊 1/8 - Executando auditoria..."
python find_bets_imports.py > bets_audit_report.txt

# 2. Backup antes de qualquer mudança
echo "💾 2/8 - Criando backup..."
git add .
git commit -m "backup: antes de remover app bets"

# 3. Remover de INSTALLED_APPS (manual - pausar aqui)
echo "✋ 3/8 - AÇÃO MANUAL: Remova 'bets' de INSTALLED_APPS em settings.py"
read -p "Pressione ENTER após remover 'bets' de INSTALLED_APPS..."

# 4. Substituir imports
echo "🔄 4/8 - Substituindo imports..."
python substituir_imports.py

# 5. Validar
echo "✅ 5/8 - Validando mudanças..."
python manage.py check
python manage.py makemigrations
python manage.py migrate

# 6. Testes
echo "🧪 6/8 - Executando testes..."
python manage.py test

# 7. Mover app bets para backup
echo "📦 7/8 - Movendo app bets para backup..."
mkdir -p backups/removed_apps
mv bets backups/removed_apps/bets_$(date +%Y%m%d)

# 8. Commit final
echo "💾 8/8 - Commitando mudanças..."
git add .
git commit -m "refactor: remove app bets após consolidação em pools"

echo "✨ Limpeza concluída!"
echo "📋 Relatório salvo em: bets_audit_report.txt"
echo "💾 Backup do app bets em: backups/removed_apps/"