#!/bin/bash
# backup_before_migration.sh

echo "🔒 Iniciando backup pré-migração..."

# Criar diretório de backups se não existir
mkdir -p backups/

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup do banco de dados MySQL
echo "📦 Fazendo dump do MySQL..."
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > backups/db_backup_$TIMESTAMP.sql

# Backup dos arquivos de mídia (logos, etc)
echo "📁 Copiando arquivos de mídia..."
tar -czf backups/media_backup_$TIMESTAMP.tar.gz media/

# Backup do código (git)
echo "💾 Salvando estado do git..."
git branch backup-$TIMESTAMP
git stash save "Backup antes migração $TIMESTAMP"

# Gerar checksum para validação
echo "✅ Gerando checksums..."
md5sum backups/db_backup_$TIMESTAMP.sql > backups/db_backup_$TIMESTAMP.md5

echo "✨ Backup completo! Arquivos salvos em backups/"
echo "   - Banco: db_backup_$TIMESTAMP.sql"
echo "   - Mídia: media_backup_$TIMESTAMP.tar.gz"
echo "   - Branch: backup-$TIMESTAMP"

# Listar backups existentes
echo ""
echo "📋 Backups disponíveis:"
ls -lh backups/
