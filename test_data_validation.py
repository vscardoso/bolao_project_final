import os
import django
import random
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from pools.models import Sport, Competition, Pool, Match, Bet, Participation

User = get_user_model()

def test_pool_creation_limits():
    """Testa os limites de criação de bolões"""
    print("=== Testando limites de criação de bolões ===")
    
    # Criar usuário de teste se não existir
    user, created = User.objects.get_or_create(
        username="testuser", 
        defaults={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    # Criar esporte e competição
    sport, _ = Sport.objects.get_or_create(name="Futebol")
    competition, _ = Competition.objects.get_or_create(
        name="Teste Competição",
        sport=sport,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + datetime.timedelta(days=90),
        is_active=True
    )
    
    # Testar nome muito longo
    try:
        pool = Pool(
            name="A" * 200,  # Nome muito longo
            owner=user,
            competition=competition,
            entry_fee=10
        )
        pool.full_clean()  # Validar antes de salvar
        print("❌ FALHA: Aceitou nome de bolão muito longo!")
    except ValidationError:
        print("✅ OK: Rejeitou nome de bolão muito longo")
    
    # Testar valor negativo de entry_fee
    try:
        pool = Pool(
            name="Teste Bolão",
            owner=user,
            competition=competition,
            entry_fee=-10  # Valor negativo
        )
        pool.full_clean()
        print("❌ FALHA: Aceitou valor negativo para entry_fee!")
    except ValidationError:
        print("✅ OK: Rejeitou valor negativo para entry_fee")

def test_bet_validation():
    """Testa as validações de apostas"""
    print("\n=== Testando validações de apostas ===")
    
    # Criar objetos necessários
    user, _ = User.objects.get_or_create(username="betuser")
    sport, _ = Sport.objects.get_or_create(name="Teste")
    competition, _ = Competition.objects.get_or_create(
        name="Competição Teste", 
        sport=sport,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + datetime.timedelta(days=30),
    )
    pool, _ = Pool.objects.get_or_create(
        name="Bolão Teste",
        owner=user,
        competition=competition
    )
    
    # Partida no futuro
    future_match = Match.objects.create(
        competition=competition,
        home_team="Time A",
        away_team="Time B",
        start_time=timezone.now() + datetime.timedelta(days=1)
    )
    
    # Partida no passado
    past_match = Match.objects.create(
        competition=competition,
        home_team="Time C",
        away_team="Time D",
        start_time=timezone.now() - datetime.timedelta(hours=2),
        finished=True,
        home_score=2,
        away_score=1
    )
    
    # Testar aposta válida (partida futura)
    try:
        bet = Bet(
            user=user,
            match=future_match,
            pool=pool,
            home_score_bet=3,
            away_score_bet=1
        )
        bet.full_clean()
        print("✅ OK: Aceitou aposta em partida futura")
    except ValidationError as e:
        print(f"❌ FALHA: Rejeitou aposta válida: {e}")
    
    # Testar apostas com scores negativos
    try:
        bet = Bet(
            user=user,
            match=future_match,
            pool=pool,
            home_score_bet=-1,  # Score negativo
            away_score_bet=1
        )
        bet.full_clean()
        print("❌ FALHA: Aceitou score negativo!")
    except ValidationError:
        print("✅ OK: Rejeitou score negativo")

def test_stress_unique_constraints():
    """Testa restrições de unicidade sob estresse"""
    print("\n=== Testando restrições de unicidade ===")
    
    # Criar objetos base
    user = User.objects.get_or_create(username="stressuser")[0]
    sport = Sport.objects.get_or_create(name="Estresse")[0]
    competition = Competition.objects.get_or_create(
        name="Competição Estresse",
        sport=sport,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + datetime.timedelta(days=30),
    )[0]
    
    # Criar múltiplos bolões com nomes similares
    names = ["Estresse", "Estresse2", "Estresse_", "Estresse 2"]
    pools = []
    
    for name in names:
        try:
            pool = Pool.objects.create(
                name=name,
                owner=user,
                competition=competition
            )
            pools.append(pool)
            print(f"✅ Criou bolão: {name} -> slug: {pool.slug}")
        except Exception as e:
            print(f"❌ FALHA ao criar bolão {name}: {e}")
    
    # Verificar se os slugs são únicos
    slugs = [p.slug for p in pools]
    if len(slugs) == len(set(slugs)):
        print("✅ OK: Todos os slugs são únicos")
    else:
        print("❌ FALHA: Slugs duplicados detectados")

if __name__ == "__main__":
    test_pool_creation_limits()
    test_bet_validation()
    test_stress_unique_constraints()