import os
import sys
import django

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

# Processar todos os bolões
pools = Pool.objects.all()
print(f"Processando {pools.count()} bolões...")

for pool in pools:
    # Verificar se o dono já é participante
    owner_participation = Participation.objects.filter(user=pool.owner, pool=pool).exists()
    
    if not owner_participation:
        # Adicionar o dono como participante
        Participation.objects.create(
            user=pool.owner,
            pool=pool,
            payment_status='paid',  # Dono não precisa pagar
            points=0  # Inicialmente sem pontos
        )
        print(f"✅ Adicionado {pool.owner.username} como participante no bolão '{pool.name}'")
    else:
        print(f"✓ {pool.owner.username} já é participante no bolão '{pool.name}'")

print("\nProcessamento concluído! Todos os donos de bolões foram adicionados como participantes.")