# 🧹 Scripts de Limpeza do App Bets

Este diretório contém scripts automatizados para remover completamente o app `bets` após a consolidação dos modelos em `pools`.

## 📁 Arquivos Disponíveis

- `cleanup_bets_app.sh` - Script Bash (Linux/Mac/WSL)
- `cleanup_bets_app.ps1` - Script PowerShell (Windows)

## 🚀 Como Executar

### Windows (PowerShell)
```powershell
# Executar no diretório do projeto
.\cleanup_bets_app.ps1
```

### Linux/Mac/WSL (Bash)
```bash
# Dar permissão de execução
chmod +x cleanup_bets_app.sh

# Executar
./cleanup_bets_app.sh
```

## 📋 O que o Script Faz

1. **📊 Auditoria** - Executa `find_bets_imports.py` e salva relatório
2. **💾 Backup** - Cria commit de backup antes das mudanças
3. **✋ Pausa Manual** - Aguarda remoção de 'bets' do INSTALLED_APPS
4. **🔄 Substituição** - Executa `substituir_imports.py` automaticamente
5. **✅ Validação** - Roda check, makemigrations e migrate
6. **🧪 Testes** - Executa suite de testes Django
7. **📦 Backup do App** - Move `bets/` para `backups/removed_apps/`
8. **💾 Commit Final** - Comita todas as mudanças

## ⚠️ Pré-requisitos

- [ ] **Backup completo** do banco de dados realizado
- [ ] **Ambiente de teste** validado (staging)
- [ ] **Branch separada** para as mudanças
- [ ] **Scripts auxiliares** presentes: `find_bets_imports.py`, `substituir_imports.py`

## 🔄 Rollback

Se algo der errado, você pode reverter:

```bash
# Reverter para commit anterior
git reset --hard HEAD~2

# Restaurar app bets do backup
cp -r backups/removed_apps/bets_YYYYMMDD/ bets/

# Adicionar 'bets' de volta ao INSTALLED_APPS
```

## 📊 Relatórios Gerados

- `bets_audit_report.txt` - Relatório completo de referências ao app bets
- Git commits com histórico detalhado das mudanças

## 💡 Dicas

- **Execute primeiro em staging** antes de usar em produção
- **Monitore os logs** durante a execução
- **Mantenha backups** por pelo menos 30 dias
- **Teste funcionalidades críticas** após a execução

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs de erro
2. Consulte o `MIGRATION_GUIDE.md`
3. Use os comandos de rollback se necessário
4. Restaure backups se tudo mais falhar

---
**Última atualização**: 29/09/2025