from django.db import migrations


class Migration(migrations.Migration):
    """
    Remove modelos legados do app bets após consolidação em pools.
    
    Esta migration documenta a remoção dos modelos Team, Match e Bet
    que foram consolidados no app pools. As tabelas do banco de dados
    foram mantidas temporariamente para auditoria, mas podem ser
    removidas manualmente após validação completa.
    
    Para remover as tabelas manualmente:
    DROP TABLE IF EXISTS bets_bet;
    DROP TABLE IF EXISTS bets_match;
    DROP TABLE IF EXISTS bets_team;
    
    IMPORTANTE: Esta migration é apenas documental e não executa
    operações automáticas de remoção. As tabelas devem ser removidas
    manualmente apenas após:
    1. Migração completa dos dados para pools
    2. Validação de que todos os dados foram migrados corretamente
    3. Backup completo do banco de dados
    4. Testes em ambiente de produção
    """

    dependencies = [
        ('bets', '0002_initial'),  # Última migration existente
    ]

    operations = [
        # Operações de delete comentadas para não executar automaticamente
        # migrations.DeleteModel(name='Team'),
        # migrations.DeleteModel(name='Match'),
        # migrations.DeleteModel(name='Bet'),
        
        # Migration vazia - apenas documentação
        # As tabelas podem ser removidas manualmente quando apropriado
        # após validação completa da migração de dados
    ]