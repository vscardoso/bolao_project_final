import os
import sys
import django
from datetime import datetime, timedelta

# Adicionar o diretório raiz do projeto ao PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Verifique o nome correto do arquivo de configurações
# Substitua 'bolao_project.settings' pelo nome correto se for diferente
try:
    # Tente listar os arquivos para ver o nome correto do módulo de configurações
    for item in os.listdir(BASE_DIR):
        if os.path.isdir(os.path.join(BASE_DIR, item)) and os.path.exists(os.path.join(BASE_DIR, item, 'settings.py')):
            settings_module = f"{item}.settings"
            print(f"Encontrado módulo de configurações: {settings_module}")
            break
    else:
        # Caso não encontre, usar o padrão
        settings_module = 'bolao_project.settings'
        print(f"Usando módulo de configurações padrão: {settings_module}")
except Exception as e:
    # Se algo falhar, usar o padrão
    settings_module = 'bolao_project.settings'
    print(f"Erro ao buscar módulo de configurações: {e}")
    print(f"Usando módulo de configurações padrão: {settings_module}")

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

# Tentar inicializar o Django
try:
    django.setup()
    print("Django inicializado com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar Django: {e}")
    sys.exit(1)

# Agora podemos importar os modelos com segurança
from pools.models import Competition, Match

# Verificar quais campos o modelo Match tem
print("\nCampos disponíveis no modelo Match:")
for field in Match._meta.fields:
    print(f" - {field.name}")

# Buscar a competição Copa do Mundo 2026
try:
    competition = Competition.objects.get(name="Copa do Mundo 2026")
    print(f"\nCompetição encontrada: {competition.name}")
except Competition.DoesNotExist:
    print("\nCompetição 'Copa do Mundo 2026' não encontrada!")
    exit()

# Criar algumas partidas para a Copa do Mundo 2026
# Datas futuras para permitir apostas
start_date = datetime.now() + timedelta(days=1)  # Amanhã

# Fase de grupos - 6 jogos
matches = [
    # Grupo A
    {"home_team": "Brasil", "away_team": "França", "location": "Estádio Azteca, México", "stage": "Grupo A"},
    {"home_team": "Estados Unidos", "away_team": "Canadá", "location": "MetLife Stadium, EUA", "stage": "Grupo A"},
    
    # Grupo B
    {"home_team": "Argentina", "away_team": "Alemanha", "location": "Hard Rock Stadium, EUA", "stage": "Grupo B"},
    {"home_team": "Espanha", "away_team": "Inglaterra", "location": "Rose Bowl, EUA", "stage": "Grupo B"},
    
    # Grupo C
    {"home_team": "Itália", "away_team": "Portugal", "location": "BC Place, Canadá", "stage": "Grupo C"},
    {"home_team": "Holanda", "away_team": "Bélgica", "location": "BMO Field, Canadá", "stage": "Grupo C"},
]

# Criar as partidas com datas espaçadas
for i, match_data in enumerate(matches):
    match_date = start_date + timedelta(days=i)  # Cada partida um dia após a anterior
    
    # Usar apenas os campos que existem no modelo Match
    try:
        match = Match.objects.create(
            competition=competition,
            home_team=match_data["home_team"],
            away_team=match_data["away_team"],
            start_time=match_date,
            # Tentar usar location e stage se venue e round não existirem
            # Você pode precisar ajustar esses nomes de campo
            location=match_data.get("location", ""),
            stage=match_data.get("stage", ""),
            finished=False,
        )
        print(f"Criada partida: {match.home_team} vs {match.away_team} em {match.start_time.strftime('%d/%m/%Y')}")
    except TypeError as e:
        print(f"Erro ao criar partida {match_data['home_team']} vs {match_data['away_team']}: {e}")
        # Tentar novamente sem os campos problemáticos
        match = Match.objects.create(
            competition=competition,
            home_team=match_data["home_team"],
            away_team=match_data["away_team"],
            start_time=match_date,
            finished=False,
        )
        print(f"Criada partida com campos limitados: {match.home_team} vs {match.away_team}")

print(f"\nTotal de {len(matches)} partidas criadas!")