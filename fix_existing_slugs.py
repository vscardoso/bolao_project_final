import os
import sys
import django
import unicodedata
import re
from django.db import transaction

# Configuração básica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
for item in os.listdir(BASE_DIR):
    if os.path.isdir(os.path.join(BASE_DIR, item)) and os.path.exists(os.path.join(BASE_DIR, item, 'settings.py')):
        settings_module = f"{item}.settings"
        break
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup()

from pools.models import Pool

def slugify(text):
    """Converte texto em um slug válido"""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

# Corrige os slugs de todos os bolões
with transaction.atomic():
    pools = Pool.objects.all()
    fixed_count = 0
    
    for pool in pools:
        base_name = slugify(pool.name)
        # Mantenha o número existente se houver
        num_match = re.search(r'-(\d+)$', pool.slug)
        suffix = num_match.group(1) if num_match else str(random.randint(1000, 9999))
        
        new_slug = f"{base_name}-{suffix}"
        if new_slug != pool.slug:
            old_slug = pool.slug
            pool.slug = new_slug
            pool.save(update_fields=['slug'])
            print(f"Slug corrigido: '{old_slug}' → '{new_slug}'")
            fixed_count += 1
    
    print(f"\nTotal: {fixed_count} slugs corrigidos")