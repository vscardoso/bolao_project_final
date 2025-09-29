# 🔄 Guia de Migração: Consolidação de Modelos Bets → Pools

## Visão Geral
Este documento descreve o processo de consolidação dos modelos duplicados entre os apps `bets/` e `pools/`, movendo ## Contact & Suporte
Para dúvidas ou problemas durante a execução, contate o responsável pelo projeto ou registre issues no repositório com logs e passos executados.

---

## ✅ Resultado da Migração

**Data**: 2025-09-29
**Status**: Concluída com sucesso

### Resumo
- As tabelas legadas `bets_team`, `bets_match`, `bets_bet` não foram encontradas no banco
- Não havia dados para migrar
- App `bets` foi removido do projeto sem perda de dados
- Todos os modelos agora estão consolidados em `pools/`

### Arquivos Modificados
- ✅ `settings.py`: App 'bets' já não estava em INSTALLED_APPS
- ✅ Substituídos imports em 2 arquivos (find_bets_imports.py, substituir_imports.py)
- ✅ Removido diretório `bets/` (backup em `backups/removed_apps/bets_20250929/`)
- ✅ Migrations corrigidas e aplicadas
- ✅ Testes básicos passando

### Validação Final
```bash
python manage.py check           # ✓ System check identified no issues
python manage.py shell -c "..."  # ✓ 110 pools funcionando normalmente
python manage.py runserver       # ✓ Servidor Django iniciando sem erros
```

### Estrutura Final
- **Modelos consolidados**: `pools/models.py` (único)
- **Legacy models**: `pools/legacy_models.py` (para futuras migrações se necessário)
- **Comando de migração**: `pools/management/commands/migrate_bets_to_pools.py` (mantido para auditoria)
- **Backup do app removido**: `backups/removed_apps/bets_20250929/`

### Próximos Passos
1. **Monitorar produção** por 48h para identificar possíveis problemas
2. **Remover arquivos auxiliares** após 1 semana: `find_bets_imports.py`, `substituir_imports.py`
3. **Limpar legacy models** após 1 mês: `pools/legacy_models.py`
4. **Remover backup** após validação completa: `backups/removed_apps/bets_20250929/`

### Commits Relevantes
- `a1d33dd`: backup antes de substituir imports bets→pools
- `3149bff`: refactor: remove app bets após consolidação em pools

**Migração concluída com sucesso! 🎉**

---s os dados para `pools/` como fonte única de verdade. O objetivo é garantir integridade dos dados, manter histórico e minimizar downtime.

## Pré-requisitos
- [ ] Backup completo do banco de dados (dump) e arquivos de mídia
- [ ] Ambiente de staging para testes (igual ao production quando possível)
- [ ] Código em branch separada `consolidation/pools-bets`
- [ ] Testes unitários e de integração passando
- [ ] Acesso ao servidor/DB para restaurar backups se necessário

## Modelos Afetados
- `Team` (bets.Team → pools.Team)
- `Match` (bets.Match → pools.Match)
- `Bet` (bets.Bet → pools.Bet)

## Timeline Estimado
- Preparação: 2 horas
- Migração em staging: 4 horas
- Validação: 2 horas
- Migração em produção: 1 hora
- **Total estimado: ~9 horas** (varia conforme volume de dados)

---

## Passos Detalhados

### 0) Iniciar branch e preparar ambiente

```bash
git checkout -b consolidation/pools-bets
pip install -r requirements.txt
# (opcionais)
pip install pytest-django factory-boy
```

### 1) Backup (obrigatório)

Use o script fornecido `backup_before_migration.sh` ou uma alternativa adaptada ao ambiente Windows.

Exemplo (bash / WSL / Git Bash):
```bash
export DB_USER='meu_usuario'
export DB_PASSWORD='minha_senha'
export DB_NAME='nome_db'
bash backup_before_migration.sh
```

Restaurar (se necessário):
```bash
mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < backups/db_backup_<TIMESTAMP>.sql
tar -xzf backups/media_backup_<TIMESTAMP>.tar.gz -C ./
```

> Nota: no Windows PowerShell prefira `Get-FileHash` para checksums e adapte comandos de `tar`/`mysqldump` conforme sua stack.

### 2) Localizar e ajustar imports antigos

Execute o script `find_bets_imports.py` para listar lugares que importam `bets`:

```powershell
python find_bets_imports.py
```

O script sugere comandos `sed`/Python para substituir importações para `pools`.

Faça as substituições com cuidado e crie commits pequenos (um commit por tipo de alteração).

### 3) Criar modelos legados (unmanaged)

Foi criado `pools/legacy_models.py` com `LegacyTeam`, `LegacyMatch`, `LegacyBet` (managed=False). Esses modelos servem apenas para leitura no processo de migração e não alteram a estrutura do DB.

### 4) Migrations para introduzir FKs temporários

Foram adicionadas migrations:
- `pools/migrations/0009_add_team_fks.py` — adiciona `home_team_fk` e `away_team_fk` (null=True) e executa uma `RunPython` para popular esses FKs.
- `pools/migrations/0010_make_team_fks_required.py` — remove campos CharField (`home_team`, `away_team`), renomeia os FK temporários para os nomes finais e altera para `null=False`.

Como executar (staging primeiro):

```powershell
python manage.py migrate pools 0009_add_team_fks
# Executa a data migration que popula os FKs
python manage.py migrate pools
```

OBS: As migrations já adicionadas no repositório podem ser aplicadas com `python manage.py migrate` normalmente; teste em staging antes de produção.

### 5) Command de migração de dados (migrate_bets_to_pools)

Arquivo: `pools/management/commands/migrate_bets_to_pools.py`

Características:
- `--dry-run` (simula sem commitar)
- Logging detalhado
- Contadores e relatório final
- Validações: Pool existe, User existe, Match existe
- Mapeamento legacy_id -> new object
- Evita duplicatas
- Progress indicator

Execução (dry-run):

```powershell
python manage.py migrate_bets_to_pools --dry-run
```

Se o dry-run estiver OK, execute sem a flag para aplicar:

```powershell
python manage.py migrate_bets_to_pools
```

### 6) Testes automatizados

Use `pytest` com `pytest-django`. Existem factories e testes em `pools/tests/` para validar:
- criação de teams
- prevenção de duplicatas
- preservação de scores
- cálculo de pontos
- rollback/dry-run

Rodar os testes:

```powershell
pytest -q
```

> Garanta que `pytest`, `pytest-django` e `factory_boy` estão instalados no ambiente.

### 7) Validação pós-migração

Verificações recomendadas (exemplos SQL / Django shell):

Contagens básicas:
```sql
SELECT COUNT(*) FROM bets_team;
SELECT COUNT(*) FROM pools_team;
```

Checar duplicatas por nome:
```sql
SELECT name, COUNT(*) c FROM pools_team GROUP BY name HAVING c > 1;
```

Verificar matches têm pool válido:
```python
from pools.models import Match
assert all(m.pool is not None for m in Match.objects.all())
```

Somatório de pontos (antes vs depois):
```python
# usar Django shell para comparar agregações entre tables legacy (se acessíveis) e novas
```

### 8) Rollback / Contingência

Se precisar reverter:
1. Restaurar dump SQL: `mysql -u user -p db < backups/db_backup_<TIMESTAMP>.sql`
2. Restaurar mídia: `tar -xzf backups/media_backup_<TIMESTAMP>.tar.gz -C ./`
3. Reverter código: `git checkout main && git branch -D consolidation/pools-bets` ou reset para commit anterior.
4. Reverter migrations (apenas se apropriado): `python manage.py migrate pools 0008_standardize_english_names`

> Importante: testar restauração em staging antes de usar em produção.

### 9) Pós-migração (cleanup)

- Rodar `python manage.py makemigrations` e revisar se restaram mudanças pendentes
- Remover `pools/legacy_models.py` se não for mais necessário (após checagens finais)
- Remover app `bets` do código (substituir imports) e, opcionalmente, criar uma migration para `DeleteModel` no app `bets` (somente após confirmar que os dados foram migrados e backups estão OK)
- Atualizar documentação e README

## Riscos e Mitigações

- Dados inconsistentes (nomes diferentes, falta de pool/user): mitigar com validações e registros de warnings no comando de migração.
- Grandes volumes de dados: usar batch processing e `iterator()` para evitar OOM.
- Signals (post_save) que recalculam pontos automaticamente: temporariamente desabilitar signals ou adicionar flag `MIGRATION_RUNNING` em settings e checar no handler.

Exemplo de checagem de signal:
```python
from django.conf import settings

if getattr(settings, 'MIGRATION_RUNNING', False):
    return
```

## Checklist Final (pré-produção)
- [ ] Backups verificados e testados
- [ ] Dry-run em staging OK
- [ ] Testes unitários passando
- [ ] Planos de rollback escritos e testados
- [ ] Janela de manutenção agendada

## Contact & Suporte
Para dúvidas ou problemas durante a execução, contate o responsável pelo projeto ou registre issues no repositório com logs e passos executados.

---

Arquivo(s) relevantes
- `pools/legacy_models.py` — modelos unmanaged para leitura
- `pools/management/commands/migrate_bets_to_pools.py` — comando de migração
- `pools/migrations/0009_add_team_fks.py`, `0010_make_team_fks_required.py`
- `find_bets_imports.py`, `backup_before_migration.sh`

Boa migração! 🚀
