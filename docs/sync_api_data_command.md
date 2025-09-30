# Comando sync_api_data - Sincronização Football-Data.org

## Descrição
O comando `sync_api_data` permite sincronizar dados da API Football-Data.org com o banco de dados do projeto, incluindo competições, times, partidas e resultados.

## Configuração
Antes de usar o comando, certifique-se de que a chave da API está configurada no arquivo `.env`:

```env
FOOTBALL_API_KEY=sua_chave_da_api_aqui
```

## Uso

### Sincronizar todas as competições
```bash
python manage.py sync_api_data
```

### Sincronizar competição específica
```bash
python manage.py sync_api_data --competition-id PL
python manage.py sync_api_data --competition-id CL
```

### Atualizar resultados de partidas
```bash
python manage.py sync_api_data --update-matches
```

### Importar times das competições
```bash
python manage.py sync_api_data --import-teams
```

### Teste sem modificar dados (dry-run)
```bash
python manage.py sync_api_data --dry-run
```

### Combinando opções
```bash
python manage.py sync_api_data --competition-id PL --import-teams --update-matches
```

## Códigos de Competições Comuns
- `PL` - Premier League (Inglaterra)
- `CL` - Champions League
- `ELC` - Championship (Inglaterra)
- `PD` - La Liga (Espanha)
- `SA` - Serie A (Itália)
- `BL1` - Bundesliga (Alemanha)
- `FL1` - Ligue 1 (França)
- `BSA` - Série A (Brasil)

## Funcionalidades

### 1. Sincronização de Competições
- Importa informações básicas das competições
- Cria ou atualiza registros de Competition no banco
- Inclui dados como nome, código, país e temporada

### 2. Importação de Times
- Busca times participantes de cada competição
- Cria ou atualiza registros de Team
- Inclui nome, nome curto, logo e status

### 3. Sincronização de Partidas
- Importa fixtures de cada competição
- Cria registros de Match com times, data e rodada
- Mapeia status da partida (agendada, ao vivo, finalizada)

### 4. Atualização de Resultados
- Busca resultados de partidas já existentes
- Atualiza placar e marca como finalizada
- Processa apenas partidas ainda não finalizadas

## Status de Partidas
O comando mapeia os status da API para os seguintes valores:
- `SCHEDULED` → `scheduled`
- `LIVE`, `IN_PLAY`, `PAUSED` → `live`
- `FINISHED` → `finished`
- `POSTPONED` → `postponed`
- `SUSPENDED` → `suspended`
- `CANCELLED` → `cancelled`

## Tratamento de Erros
- Rate limit da API (429): Avisa para aguardar
- Acesso negado (403): Verifica chave da API
- Erros de rede: Exibe mensagem detalhada
- Transações atômicas: Reverte em caso de erro

## Logs e Feedback
O comando fornece feedback detalhado sobre:
- URLs sendo acessadas
- Competições criadas/atualizadas
- Partidas processadas
- Erros encontrados
- Status geral da sincronização

## Exemplo de Uso Completo

```bash
# 1. Teste inicial sem modificar dados
python manage.py sync_api_data --dry-run

# 2. Importar dados da Premier League
python manage.py sync_api_data --competition-id PL --import-teams

# 3. Atualizar resultados
python manage.py sync_api_data --update-matches

# 4. Sincronização completa (cuidado com rate limits)
python manage.py sync_api_data --import-teams --update-matches
```

## Considerações Importantes
- **Rate Limits**: A API tem limites de requisições por minuto
- **Chave da API**: Necessária chave válida do Football-Data.org
- **Transações**: Operações são atômicas por competição/partida
- **Dry Run**: Sempre teste com `--dry-run` primeiro

## Segurança
- Chave da API armazenada em variável de ambiente
- Validação de entrada para evitar injeção
- Transações atômicas para consistência de dados