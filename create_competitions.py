import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_project.settings')
django.setup()

# Agora podemos importar os modelos com segurança
from pools.models import Competition, Sport

# Verificar se já existem esportes
sports = Sport.objects.all()
if not sports.exists():
    # Criar alguns esportes básicos
    futebol = Sport.objects.create(name="Futebol", icon="football")
    basquete = Sport.objects.create(name="Basquete", icon="basketball")
    volei = Sport.objects.create(name="Vôlei", icon="volleyball")
else:
    # Usar o primeiro esporte existente
    futebol = Sport.objects.first()

# Criar competições
Competition.objects.create(
    name="Campeonato Brasileiro 2025",
    sport=futebol,
    description="Campeonato Brasileiro Série A",
    start_date="2025-04-15",
    end_date="2025-12-10",
    is_active=True
)

Competition.objects.create(
    name="Copa do Brasil 2025",
    sport=futebol,
    description="Copa nacional brasileira",
    start_date="2025-05-01",
    end_date="2025-11-15",
    is_active=True
)

Competition.objects.create(
    name="Copa do Mundo 2026",
    sport=futebol,
    description="Copa do Mundo FIFA 2026",
    start_date="2026-06-10",
    end_date="2026-07-15",
    is_active=True
)

print("Competições criadas com sucesso!")