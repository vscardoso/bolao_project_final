import os
import django
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from pools.forms import BetForm, PoolForm
from pools.models import Sport, Competition, Pool, Match, Bet
from users.forms import UserRegisterForm, UserUpdateForm
from django.utils import timezone
import datetime

User = get_user_model()

def setup_message_middleware(request):
    """Configuração para que os messages funcionem no teste"""
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)

def test_bet_form():
    print("\n=== Testando BetForm ===")
    
    # Criar objetos necessários
    user = User.objects.get_or_create(username="formtestuser")[0]
    sport = Sport.objects.get_or_create(name="FormTest")[0]
    competition = Competition.objects.get_or_create(
        name="Form Test Competition",
        sport=sport,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + datetime.timedelta(days=30)
    )[0]
    
    match = Match.objects.get_or_create(
        competition=competition,
        home_team="Home Team",
        away_team="Away Team",
        start_time=timezone.now() + datetime.timedelta(days=1)
    )[0]
    
    pool = Pool.objects.get_or_create(
        name="Form Test Pool",
        owner=user,
        competition=competition
    )[0]
    
    # Testar formulário com dados válidos
    valid_data = {
        'home_score_bet': 2,
        'away_score_bet': 1
    }
    
    form = BetForm(data=valid_data, match=match, pool=pool)
    if form.is_valid():
        print("✅ BetForm aceita dados válidos")
    else:
        print(f"❌ BetForm rejeitou dados válidos: {form.errors}")
    
    # Testar com valores inválidos
    invalid_data_sets = [
        {'home_score_bet': -1, 'away_score_bet': 1},  # Negativo
        {'home_score_bet': 'abc', 'away_score_bet': 1},  # Não numérico
        {'home_score_bet': 1000, 'away_score_bet': 1000},  # Valores muito altos
        {'home_score_bet': '', 'away_score_bet': ''}  # Vazios
    ]
    
    for i, data in enumerate(invalid_data_sets):
        form = BetForm(data=data, match=match, pool=pool)
        if not form.is_valid():
            print(f"✅ BetForm #{i+1} rejeitou dados inválidos: {data}")
        else:
            print(f"❌ BetForm #{i+1} aceitou dados inválidos: {data}")

def test_pool_form():
    print("\n=== Testando PoolForm ===")
    
    # Criar objetos necessários
    user = User.objects.get_or_create(username="pooltestuser")[0]
    sport = Sport.objects.get_or_create(name="PoolFormTest")[0]
    competition = Competition.objects.get_or_create(
        name="Pool Form Test Competition",
        sport=sport,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + datetime.timedelta(days=30)
    )[0]
    
    # Testar formulário com dados válidos
    valid_data = {
        'name': 'Novo Bolão de Teste',
        'competition': competition.id,
        'entry_fee': 10,
        'visibility': 'public',
        'max_participants': 20,
        'description': 'Um bolão para testes de formulário'
    }
    
    form = PoolForm(data=valid_data)
    if form.is_valid():
        print("✅ PoolForm aceita dados válidos")
    else:
        print(f"❌ PoolForm rejeitou dados válidos: {form.errors}")
    
    # Testar limites e casos inválidos
    invalid_data_sets = [
        {'name': 'A' * 150, 'competition': competition.id},  # Nome muito longo
        {'name': '', 'competition': competition.id},  # Nome vazio
        {'name': 'Bolão', 'competition': 9999},  # Competition ID inválido
        {'name': 'Bolão', 'competition': competition.id, 'entry_fee': -10},  # Taxa negativa
    ]
    
    for i, data in enumerate(invalid_data_sets):
        form = PoolForm(data=data)
        if not form.is_valid():
            print(f"✅ PoolForm #{i+1} rejeitou dados inválidos como esperado")
        else:
            print(f"❌ PoolForm #{i+1} aceitou dados inválidos: {data}")

def test_user_forms():
    print("\n=== Testando Formulários de Usuário ===")
    
    # Testar formulário de registro
    register_data = {
        'username': 'newuser123',
        'email': 'newuser@example.com',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!'
    }
    
    register_form = UserRegisterForm(data=register_data)
    if register_form.is_valid():
        print("✅ UserRegisterForm aceita dados válidos")
    else:
        print(f"❌ UserRegisterForm rejeitou dados válidos: {register_form.errors}")
    
    # Testar formulário de atualização
    update_data = {
        'username': 'updateduser',
        'email': 'updated@example.com',
    }
    
    update_form = UserUpdateForm(data=update_data)
    if update_form.is_valid():
        print("✅ UserUpdateForm aceita dados válidos")
    else:
        print(f"❌ UserUpdateForm rejeitou dados válidos: {update_form.errors}")
    
    # Testar casos inválidos
    
    # 1. Nome de usuário já existente
    existing_user = User.objects.get_or_create(username='existinguser')[0]
    
    existing_data = {
        'username': 'existinguser',
        'email': 'another@example.com',
        'password1': 'TestPassword123!',
        'password2': 'TestPassword123!'
    }
    
    register_form = UserRegisterForm(data=existing_data)
    if not register_form.is_valid():
        print("✅ UserRegisterForm rejeitou nome de usuário duplicado")
    else:
        print("❌ UserRegisterForm aceitou nome de usuário duplicado")
    
    # 2. Senhas não coincidem
    mismatch_data = {
        'username': 'mismatchuser',
        'email': 'mismatch@example.com',
        'password1': 'TestPassword123!',
        'password2': 'DifferentPassword123!'
    }
    
    register_form = UserRegisterForm(data=mismatch_data)
    if not register_form.is_valid():
        print("✅ UserRegisterForm rejeitou senhas diferentes")
    else:
        print("❌ UserRegisterForm aceitou senhas diferentes")

if __name__ == "__main__":
    test_bet_form()
    test_pool_form()
    test_user_forms()