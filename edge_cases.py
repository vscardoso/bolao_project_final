import os
import django
import datetime
import random
from django.utils import timezone
from django.db.utils import IntegrityError

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from pools.models import Sport, Competition, Pool, Match, Bet, Participation
from pools.forms import BetForm
from django import forms

User = get_user_model()

def test_edge_cases():
    print("=== Testando condições de borda e casos extremos ===")
    
    # Criar objetos básicos para testes
    user = User.objects.get_or_create(username="edgeuser")[0]
    sport = Sport.objects.get_or_create(name="EdgeSport")[0]
    competition = Competition.objects.get_or_create(
        name="Edge Competition",
        sport=sport,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + datetime.timedelta(days=30),
        is_active=True
    )[0]
    
    pool = Pool.objects.get_or_create(
        name="Edge Pool",
        owner=user,
        competition=competition,
        status='open'
    )[0]
    
    # Adicionar usuário como participante
    Participation.objects.get_or_create(
        user=user,
        pool=pool,
        defaults={"payment_status": "paid"}
    )
    
    # CASO 1: Partida começa exatamente no momento atual
    print("\n--- Caso 1: Partida começa exatamente agora ---")
    now_match = Match.objects.create(
        competition=competition,
        home_team="Now Home",
        away_team="Now Away",
        start_time=timezone.now()
    )
    
    # Tentar criar uma aposta para esta partida
    bet = Bet(
        user=user,
        match=now_match,
        pool=pool,
        home_score_bet=1,
        away_score_bet=1
    )
    
    try:
        bet.full_clean()
        bet.save()
        print("❌ FALHA: Sistema permitiu apostar em partida que já começou")
    except Exception as e:
        print(f"✅ OK: Sistema rejeitou aposta: {e}")
    
    # CASO 2: Pontuação extremamente alta
    print("\n--- Caso 2: Aposta com pontuação extremamente alta ---")
    future_match = Match.objects.create(
        competition=competition,
        home_team="Future Home",
        away_team="Future Away",
        start_time=timezone.now() + datetime.timedelta(days=1)
    )
    
    high_score_bet = Bet(
        user=user,
        match=future_match,
        pool=pool,
        home_score_bet=100,
        away_score_bet=100
    )
    
    try:
        high_score_bet.full_clean()
        high_score_bet.save()
        print("⚠️ AVISO: Sistema aceitou apostas com pontuações extremamente altas")
    except Exception as e:
        print(f"Sistema rejeitou aposta com pontuação alta: {e}")
    
    # CASO 3: Múltiplos usuários apostando no mesmo segundo
    print("\n--- Caso 3: Múltiplos usuários apostando simultaneamente ---")
    
    # Criar mais usuários
    users = []
    for i in range(5):
        new_user = User.objects.get_or_create(username=f"concurrent{i}")[0]
        Participation.objects.get_or_create(
            user=new_user,
            pool=pool,
            defaults={"payment_status": "paid"}
        )
        users.append(new_user)
    
    # Criar uma partida para todos apostarem
    concurrent_match = Match.objects.create(
        competition=competition,
        home_team="Concurrent Home",
        away_team="Concurrent Away",
        start_time=timezone.now() + datetime.timedelta(days=1)
    )
    
    # Tentar criar apostas simultaneamente (simulado)
    success_count = 0
    for user in users:
        try:
            bet = Bet.objects.create(
                user=user,
                match=concurrent_match,
                pool=pool,
                home_score_bet=1,
                away_score_bet=2
            )
            success_count += 1
        except IntegrityError:
            print(f"Falha ao criar aposta para {user.username}")
    
    print(f"✅ {success_count} de {len(users)} apostas criadas com sucesso")
    
    # CASO 4: Teste de formulário com dados inválidos
    print("\n--- Caso 4: Formulário com dados inválidos ---")
    
    # Criar um match simulado para o formulário
    class MockMatch:
        def __init__(self):
            self.home_team = "Mock Home"
            self.away_team = "Mock Away"
    
    mock_match = MockMatch()
    
    # Testar vários cenários de dados inválidos
    invalid_data_scenarios = [
        {},  # Dados vazios
        {"home_score_bet": "abc"},  # Texto em vez de número
        {"home_score_bet": -1, "away_score_bet": 0},  # Valor negativo
        {"home_score_bet": "", "away_score_bet": ""}  # Strings vazias
    ]
    
    for i, invalid_data in enumerate(invalid_data_scenarios):
        form = BetForm(data=invalid_data)
        if form.is_valid():
            print(f"❌ FALHA: Formulário aceitou dados inválidos no cenário {i+1}")
        else:
            print(f"✅ OK: Formulário rejeitou dados inválidos no cenário {i+1}")
    
    # CASO 5: Teste de cancelamento de partida
    print("\n--- Caso 5: Cancelamento de partida ---")
    
    canceled_match = Match.objects.create(
        competition=competition,
        home_team="Canceled Home",
        away_team="Canceled Away",
        start_time=timezone.now() + datetime.timedelta(days=1)
    )
    
    # Criar algumas apostas
    for user in users[:3]:
        Bet.objects.create(
            user=user,
            match=canceled_match,
            pool=pool,
            home_score_bet=random.randint(0, 3),
            away_score_bet=random.randint(0, 3)
        )
    
    # Verificar o número de apostas antes
    bets_before = Bet.objects.filter(match=canceled_match).count()
    
    # Simular cancelamento (excluindo a partida)
    try:
        canceled_match.delete()
        
        # Verificar se as apostas foram excluídas (comportamento CASCADE)
        bets_after = Bet.objects.filter(match=canceled_match).count()
        
        if bets_after == 0:
            print(f"✅ OK: Todas as apostas ({bets_before}) foram excluídas quando a partida foi cancelada")
        else:
            print(f"❌ FALHA: Ainda existem {bets_after} apostas após cancelamento da partida")
    except Exception as e:
        print(f"❌ FALHA ao cancelar partida: {e}")

if __name__ == "__main__":
    test_edge_cases()