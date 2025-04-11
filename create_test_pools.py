import os
import sys
import django
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random
import unicodedata
import re

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
from pools.models import Pool, Competition, Participation
from django.contrib.auth import get_user_model
User = get_user_model()

# Função para criar usuários de teste
def create_test_users():
    usuarios = [
        {'username': 'joao123', 'first_name': 'João', 'email': 'joao@example.com'},
        {'username': 'maria456', 'first_name': 'Maria', 'email': 'maria@example.com'},
        {'username': 'pedro789', 'first_name': 'Pedro', 'email': 'pedro@example.com'},
        {'username': 'ana_silva', 'first_name': 'Ana', 'email': 'ana@example.com'},
        {'username': 'carlos44', 'first_name': 'Carlos', 'email': 'carlos@example.com'},
    ]
    
    created_users = []
    for u in usuarios:
        user, created = User.objects.get_or_create(
            username=u['username'],
            defaults={
                'email': u['email'],
                'first_name': u['first_name'],
                'is_active': True
            }
        )
        if created:
            user.set_password('senha123')
            user.save()
            print(f"✓ Usuário criado: {user.username}")
        else:
            print(f"• Usuário já existe: {user.username}")
        
        created_users.append(user)
    
    return created_users

# Função para criar slugs
def slugify(text):
    """
    Convert spaces to hyphens, remove characters that aren't alphanumerics,
    underscores, or hyphens, convert to lowercase, and strip leading and trailing whitespace.
    """
    # Normalize unicode characters to ASCII
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    # Convert to lowercase, replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace consecutive whitespace with single hyphen
    text = re.sub(r'[\s_-]+', '-', text)
    # Strip whitespace from start and end
    return text.strip('-')

# Função para criar bolões de teste
def create_test_pools(users):
    # Obter a competição existente ou criar uma nova
    competition, _ = Competition.objects.get_or_create(
        name="Copa do Mundo 2026",
        defaults={
            'description': 'Competição mundial de futebol',
            'start_date': timezone.now() + timedelta(days=30),
            'end_date': timezone.now() + timedelta(days=60),
        }
    )
    
    # Lista de bolões de exemplo - CAMPOS CORRIGIDOS
    boloes = [
        {
            'name': 'Bolão da Galera',
            'description': 'Bolão para os amigos do trabalho acompanharem os jogos juntos! 1º lugar: 60%, 2º lugar: 30%, 3º lugar: 10%.',
            'entry_fee': 25.00,
            'visibility': 'public',
            'status': 'open',
        },
        {
            'name': 'Super Bolão 2026',
            'description': 'O melhor bolão para a Copa do Mundo 2026! Prêmios incríveis. Prêmio único para o campeão.',
            'entry_fee': 50.00,
            'visibility': 'public',
            'status': 'open',
        },
        {
            'name': 'Bolão dos Craques',
            'description': 'Só para os verdadeiros entendedores de futebol! Premiação dividida entre os 3 primeiros.',
            'entry_fee': 30.00,
            'visibility': 'public',
            'status': 'open',
        },
        {
            'name': 'Bolão VIP',
            'description': 'Para quem quer apostar alto e ganhar prêmios exclusivos. Troféu personalizado + 100% do valor arrecadado.',
            'entry_fee': 100.00,
            'visibility': 'public',
            'status': 'open',
        },
        {
            'name': 'Palpiteiros FC',
            'description': 'Um bolão descontraído para quem curte dar palpites sem compromisso. Cerveja e churrasco para os vencedores!',
            'entry_fee': 10.00,
            'visibility': 'public',
            'status': 'open',
        },
    ]
    
    current_user = User.objects.get(username='victorc')
    created_pools = []
    
    for i, bolao in enumerate(boloes):
        owner = users[i % len(users)]  # Distribui entre os usuários criados
        
        # Não criar bolões para o usuário atual - eles já têm seus próprios
        if owner == current_user:
            continue
        
        pool, created = Pool.objects.get_or_create(
            name=bolao['name'],
            owner=owner,
            defaults={
                'competition': competition,
                'description': bolao['description'],
                'entry_fee': bolao['entry_fee'],
                'visibility': bolao['visibility'],
                'status': bolao['status'],
                'slug': f"{slugify(bolao['name'])}-{random.randint(1000, 9999)}"
            }
        )
        
        if created:
            print(f"✓ Bolão criado: {pool.name} (Dono: {owner.username})")
            
            # Adicionar o dono como participante automaticamente
            Participation.objects.get_or_create(
                user=owner,
                pool=pool,
                defaults={'payment_status': 'paid'}
            )
            
            # Adicionar aleatoriamente o usuário atual como participante em alguns bolões
            if i % 2 == 0:  # Para metade dos bolões
                participation, p_created = Participation.objects.get_or_create(
                    user=current_user,
                    pool=pool,
                    defaults={'payment_status': 'paid'}
                )
                
                if p_created:
                    print(f"  → Você ({current_user.username}) foi adicionado como participante!")
        else:
            print(f"• Bolão já existe: {pool.name}")
        
        created_pools.append(pool)
    
    return created_pools

# Executar funções com controle de transação
with transaction.atomic():
    print("\n=== Criando usuários de teste ===")
    users = create_test_users()
    
    print("\n=== Criando bolões de teste ===")
    pools = create_test_pools(users)
    
    print("\n=== Resumo ===")
    print(f"✓ {len(users)} usuários verificados/criados")
    print(f"✓ {len(pools)} bolões verificados/criados")
    
    # Verificar bolões em que o usuário atual participa
    current_user = User.objects.get(username='victorc')
    participations = Participation.objects.filter(user=current_user).exclude(pool__owner=current_user)
    print(f"\nVocê participa de {participations.count()} bolões criados por outras pessoas")
    
    # Verificar bolões disponíveis para participar
    available_pools = Pool.objects.filter(
        visibility='public',
        status='open'
    ).exclude(
        participation__user=current_user
    ).distinct()
    print(f"Existem {available_pools.count()} bolões disponíveis para participar")
    
print("\nScript concluído! Volte à página de bolões para ver os resultados.")