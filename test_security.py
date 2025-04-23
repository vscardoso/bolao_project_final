import os
import django
import requests
from django.test import Client

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from pools.models import Pool, Participation

User = get_user_model()

def test_endpoint_security():
    """Testa a segurança dos endpoints"""
    print("=== Testando Segurança dos Endpoints ===")
    
    # Criar cliente sem autenticação
    client = Client()
    
    # Conjunto de URLs protegidas para testar
    protected_urls = [
        '/pools/create/',
        '/pools/my-pools/',
        '/users/profile/',
    ]
    
    # Testar acesso sem autenticação
    print("\n--- Teste de acesso sem autenticação ---")
    for url in protected_urls:
        response = client.get(url, follow=True)
        if 'login' in response.redirect_chain[-1][0]:
            print(f"✅ URL protegida corretamente: {url}")
        else:
            print(f"❌ Falha na proteção: {url} - resposta: {response.status_code}")
    
    # Criar um usuário e autenticar
    user = User.objects.get_or_create(
        username="securityuser", 
        email="security@example.com",
    )[0]
    user.set_password("testpass123")
    user.save()
    
    # Criar um segundo usuário para testar acesso a recursos de outros
    other_user = User.objects.get_or_create(
        username="otheruser", 
        email="other@example.com",
    )[0]
    other_user.set_password("testpass123")
    other_user.save()
    
    # Criar um bolão pertencente ao segundo usuário
    from pools.models import Sport, Competition
    sport = Sport.objects.get_or_create(name="SecurityTest")[0]
    competition = Competition.objects.get_or_create(
        name="Security Test Competition",
        sport=sport,
    )[0]
    
    private_pool = Pool.objects.get_or_create(
        name="Private Pool",
        owner=other_user,
        competition=competition,
        visibility="private"
    )[0]
    
    # Login com o primeiro usuário
    client.login(username="securityuser", password="testpass123")
    
    # Tentar acessar recursos do outro usuário
    print("\n--- Teste de acesso a recursos de outro usuário ---")
    
    # Tentar editar um bolão que pertence a outro usuário
    response = client.get(f'/pools/{private_pool.slug}/edit/')
    if response.status_code in [403, 404]:
        print(f"✅ Proteção correta ao editar bolão de outro usuário: {response.status_code}")
    else:
        print(f"❌ Falha na proteção ao editar bolão: {response.status_code}")

    # Tentar entrar em um bolão privado sem convite
    response = client.get(f'/pools/{private_pool.slug}/')
    if response.status_code in [403, 404, 302]:
        print(f"✅ Proteção correta ao acessar bolão privado: {response.status_code}")
    else:
        print(f"❌ Falha na proteção ao acessar bolão privado: {response.status_code}")

if __name__ == "__main__":
    test_endpoint_security()