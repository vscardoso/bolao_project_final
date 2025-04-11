import os
import sys
import django
from datetime import datetime, timedelta

# Configuração básica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
for item in os.listdir(BASE_DIR):
    if os.path.isdir(os.path.join(BASE_DIR, item)) and os.path.exists(os.path.join(BASE_DIR, item, 'settings.py')):
        settings_module = f"{item}.settings"
        break
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup()

# Importar modelos
from pools.models import Competition, Match

# Buscar a competição
competition = Competition.objects.get(name="Copa do Mundo 2026")

# Criar uma partida que começa em 5 minutos
start_time = datetime.now() + timedelta(minutes=5)

match = Match.objects.create(
    competition=competition,
    home_team="Brasil",
    away_team="Uruguai",
    start_time=start_time,
    finished=False,
)

print(f"Partida criada: {match.home_team} vs {match.away_team}")
print(f"Horário de início: {match.start_time.strftime('%H:%M:%S')}")
print(f"Horário atual: {datetime.now().strftime('%H:%M:%S')}")
print(f"Tempo restante para apostar: aproximadamente 5 minutos")