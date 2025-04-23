"""
Script para criar bolões de teste para o ambiente de desenvolvimento
"""

import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from pools.models import Pool, Competition, Sport

User = get_user_model()

# Inspecionar o modelo Pool para conhecer seus campos
print("\n=== Inspecionando o modelo Pool ===")
pool_fields = [field.name for field in Pool._meta.get_fields()]
print(f"Campos disponíveis: {pool_fields}")

# Obter usuário para ser o dono dos bolões de teste
try:
    admin_user = User.objects.get(username='admin')
except User.DoesNotExist:
    admin_user = User.objects.filter(is_superuser=True).first()

if not admin_user:
    print("⚠️ Nenhum usuário admin encontrado. Usando o primeiro usuário disponível.")
    admin_user = User.objects.first()

if not admin_user:
    print("❌ Não foi possível encontrar um usuário. Crie pelo menos um usuário antes de executar este script.")
    exit(1)

# Obter alguns usuários para adicionar como participantes
all_users = list(User.objects.exclude(id=admin_user.id)[:10])

# Nomes criativos para os bolões
pool_names = [
    "Bolão Copa do Mundo 2026", "Champions League 2025", "Copa América 2025",
    "Brasileirão Série A", "Premier League 2025", "La Liga 2025", 
    "NBA Finals 2026", "Super Bowl LX", "Copa do Brasil 2025",
    "Eurocopa 2028", "Mundial de Clubes 2025", "Formula 1 2025"
]

# Obter ou criar esportes
sport_names = ["Futebol", "Basquete", "Tênis", "UFC", "Formula 1", "Vôlei"]
sports = {}

for sport_name in sport_names:
    sport, created = Sport.objects.get_or_create(name=sport_name)
    sports[sport_name] = sport
    if created:
        print(f"✓ Esporte criado: {sport_name}")

# Datas de início e fim para os bolões
start_dates = [
    timezone.now(),                       # Bolões iniciando hoje
    timezone.now() + timedelta(days=5),   # Bolões futuros
    timezone.now() + timedelta(days=15),
    timezone.now() + timedelta(days=30)
]

print(f"🏆 Iniciando criação de 50 bolões de teste...")
created_count = 0

for i in range(50):
    name = f"{pool_names[i % len(pool_names)]} {i+1}"
    sport_name = random.choice(sport_names)
    sport = sports[sport_name]
    start_date = random.choice(start_dates)
    end_date = start_date + timedelta(days=random.randint(30, 180))
    
    # Criar competição
    competition = Competition.objects.create(
        name=f"{sport_name} 2025-{i}",
        sport=sport,
        start_date=start_date,
        end_date=end_date
    )
    
    # Criar o bolão - usando apenas campos válidos básicos
    pool_data = {
        'name': name,
        'owner': admin_user,
        'competition': competition,
        'description': f"Este é um bolão de teste para {sport_name}. Use para realizar testes do sistema.",
    }
    
    # Adicionar campos opcionais se existirem no modelo
    if 'is_public' in pool_fields:
        pool_data['is_public'] = random.choice([True, False])
    if 'public' in pool_fields:
        pool_data['public'] = random.choice([True, False])
    if 'private' in pool_fields:
        pool_data['private'] = random.choice([False, True])
    
    if 'allow_late_entry' in pool_fields:
        pool_data['allow_late_entry'] = random.choice([True, False])
    if 'late_entries_allowed' in pool_fields:
        pool_data['late_entries_allowed'] = random.choice([True, False])
    
    if 'entry_fee' in pool_fields:
        pool_data['entry_fee'] = random.choice([0, 10, 20, 50, 100])
    if 'fee' in pool_fields:
        pool_data['fee'] = random.choice([0, 10, 20, 50, 100])
    
    if 'prize_description' in pool_fields:
        pool_data['prize_description'] = f"Prêmio teste: R$ {random.randint(100, 5000)},00"
    if 'prize' in pool_fields:
        pool_data['prize'] = f"Prêmio teste: R$ {random.randint(100, 5000)},00"
    
    # Criar o bolão com os campos válidos
    pool = Pool.objects.create(**pool_data)
    
    # Adicionar alguns participantes aleatórios
    if 'participants' in pool_fields and all_users:
        num_participants = random.randint(0, len(all_users))
        participants = random.sample(all_users, num_participants)
        for participant in participants:
            pool.participants.add(participant)
    
    created_count += 1
    if created_count % 10 == 0:
        print(f"✓ {created_count} bolões criados...")

print(f"✅ Criação concluída! {created_count} bolões de teste foram adicionados ao sistema.")
print("Você pode começar seus testes do Sistema de Bolões agora.")