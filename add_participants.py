import os
import sys
import django
from django.db import transaction
import random
from faker import Faker

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
from pools.models import Pool, Participation
from django.contrib.auth import get_user_model
User = get_user_model()

# Configurar Faker para gerar nomes brasileiros
fake = Faker('pt_BR')

def add_participants_to_pool():
    # Encontrar o bolão Palpiteiros FC
    try:
        pool = Pool.objects.get(name__icontains="Palpiteiros FC")
        print(f"Bolão encontrado: {pool.name} (ID: {pool.id})")
    except Pool.DoesNotExist:
        print("Bolão 'Palpiteiros FC' não encontrado!")
        return
    except Pool.MultipleObjectsReturned:
        pool = Pool.objects.filter(name__icontains="Palpiteiros FC").first()
        print(f"Múltiplos bolões encontrados. Usando: {pool.name} (ID: {pool.id})")
    
    # Número de participantes a adicionar
    num_participants = 20
    
    # Lista para armazenar os usuários criados
    created_users = []
    
    # Criar usuários fictícios e adicioná-los como participantes
    with transaction.atomic():
        # Primeiro criar os usuários
        for i in range(1, num_participants + 1):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}_{random.randint(100, 999)}"
            
            # Verificar se o username já existe
            while User.objects.filter(username=username).exists():
                username = f"{first_name.lower()}_{random.randint(100, 999)}"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{username}@example.com",
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('senha123')
                user.save()
                print(f"✓ Criado usuário: {user.username} ({user.first_name} {user.last_name})")
            else:
                print(f"• Usuário já existe: {user.username}")
            
            created_users.append(user)
        
        # Agora adicionar os usuários como participantes
        participation_count = 0
        points_distribution = [300, 280, 250, 220, 200, 180, 160, 140, 120, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 5]
        
        for i, user in enumerate(created_users):
            # Verificar se o usuário já participa
            participation, created = Participation.objects.get_or_create(
                user=user,
                pool=pool,
                defaults={
                    'payment_status': 'paid',
                    'payment_method': random.choice(['pix', 'credit_card', 'bank_transfer']),
                    'points': points_distribution[i] if i < len(points_distribution) else 0
                }
            )
            
            if created:
                print(f"✓ Adicionado {user.username} ao bolão com {participation.points} pontos")
                participation_count += 1
            else:
                print(f"• {user.username} já participa do bolão")
        
        print(f"\n✅ Adicionados {participation_count} novos participantes ao bolão '{pool.name}'")
        print(f"Total de participantes: {pool.participation_set.count()}")

if __name__ == "__main__":
    print("Adicionando participantes ao bolão Palpiteiros FC...")
    add_participants_to_pool()
    print("\nProcesso concluído!")