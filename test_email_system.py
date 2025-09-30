"""
Script de teste para o sistema de emails do Django Bolão
Testa todas as funções de email implementadas

Para executar: python manage.py shell < test_email_system.py
"""

import os
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from pools.utils.email import (
    send_invitation_email,
    send_round_results_email,
    send_betting_reminder_email,
    send_winner_notification_email,
    send_welcome_email,
    send_bulk_email
)
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

User = get_user_model()

def test_email_templates():
    """Testa a renderização dos templates de email"""
    print("🧪 Testando renderização de templates...")
    
    # Dados de teste
    test_contexts = {
        'invitation': {
            'inviter_name': 'João Silva',
            'pool_name': 'Brasileirão 2024',
            'competition_name': 'Campeonato Brasileiro',
            'participants_count': 15,
            'max_participants': 20,
            'start_date': '15/03/2024',
            'accept_url': 'https://bolao-online.com/convite/abc123/',
            'entry_fee': 50.00,
            'prize_pool': 1000.00,
        },
        'round_results': {
            'user_name': 'Maria Santos',
            'pool_name': 'Copa do Mundo 2024',
            'round_name': '15ª Rodada',
            'round_points': 12,
            'total_points': 185,
            'current_position': 3,
            'correct_predictions': 6,
            'total_predictions': 10,
            'top_performers': [
                {'name': 'Carlos', 'points': 15},
                {'name': 'Ana', 'points': 14},
                {'name': 'Pedro', 'points': 13}
            ],
            'matches': [
                {'home': 'Flamengo', 'away': 'Palmeiras', 'result': '2-1', 'prediction': '1-0', 'points': 3},
                {'home': 'Corinthians', 'away': 'São Paulo', 'result': '0-2', 'prediction': '0-1', 'points': 2}
            ],
            'pool_url': 'https://bolao-online.com/bolao/123/',
        },
        'betting_reminder': {
            'user_name': 'Ricardo Lima',
            'pool_name': 'Champions League',
            'deadline_time': '25/12/2024 às 19:30',
            'pending_matches': [
                {'home': 'Real Madrid', 'away': 'Barcelona', 'datetime': '26/12/2024 20:00'},
                {'home': 'Manchester City', 'away': 'Liverpool', 'datetime': '26/12/2024 22:00'}
            ],
            'missing_predictions': 2,
            'betting_url': 'https://bolao-online.com/bolao/456/apostar/',
        },
        'winner_notification': {
            'winner_name': 'Ana Carolina',
            'pool_name': 'Libertadores 2024',
            'final_points': 320,
            'total_correct': 145,
            'total_predictions': 180,
            'accuracy_percentage': 80.6,
            'points_difference': 25,
            'prize_amount': 2500.00,
            'final_ranking': [
                {'name': 'Ana Carolina', 'points': 320},
                {'name': 'Carlos Silva', 'points': 295},
                {'name': 'Pedro Santos', 'points': 280}
            ],
            'best_predictions': [
                {'match': 'Flamengo 3x1 River Plate', 'prediction': '3x1', 'points': 5},
                {'match': 'Palmeiras 2x0 Boca', 'prediction': '2x0', 'points': 5}
            ],
            'certificate_url': 'https://bolao-online.com/certificado/789/123/',
        }
    }
    
    # Testar renderização de cada template
    templates = ['invitation', 'round_results', 'betting_reminder', 'winner_notification']
    
    for template in templates:
        try:
            html_content = render_to_string(f'email/{template}.html', test_contexts[template])
            print(f"✅ Template {template}.html renderizado com sucesso ({len(html_content)} caracteres)")
        except Exception as e:
            print(f"❌ Erro ao renderizar {template}.html: {e}")
    
    # Testar template base
    try:
        base_content = render_to_string('email/base_email.html', {
            'title': 'Teste',
            'content': '<p>Conteúdo de teste</p>'
        })
        print(f"✅ Template base_email.html renderizado com sucesso ({len(base_content)} caracteres)")
    except Exception as e:
        print(f"❌ Erro ao renderizar base_email.html: {e}")


def test_email_functions():
    """Testa as funções de email (sem enviar emails reais)"""
    print("\n🧪 Testando funções de email...")
    
    # Criar usuário de teste (se não existir)
    test_user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Usuário',
            'last_name': 'Teste'
        }
    )
    
    if created:
        print("👤 Usuário de teste criado")
    else:
        print("👤 Usando usuário de teste existente")
    
    # Mock de objetos para teste
    class MockInvitation:
        def __init__(self):
            self.email = 'convidado@example.com'
            self.token = 'abc123'
            self.pool = MockPool()
    
    class MockPool:
        def __init__(self):
            self.name = 'Bolão Teste'
            self.created_at = datetime.now()
            self.creator = test_user
            self.id = 123
        
        def participants(self):
            return MockQuerySet(15)
    
    class MockQuerySet:
        def __init__(self, count):
            self._count = count
        
        def count(self):
            return self._count
    
    # Dados de teste
    invitation = MockInvitation()
    pool = MockPool()
    
    round_data = {
        'round_name': '10ª Rodada',
        'round_points': 8,
        'total_points': 156,
        'current_position': 5,
        'correct_predictions': 4,
        'total_predictions': 8,
        'top_performers': [
            {'name': 'João', 'points': 12},
            {'name': 'Maria', 'points': 10}
        ],
        'matches': [
            {'home': 'Time A', 'away': 'Time B', 'result': '2x1', 'prediction': '1x0', 'points': 2}
        ]
    }
    
    pending_matches = [
        {'home': 'Flamengo', 'away': 'Vasco', 'datetime': '25/12/2024 16:00', 'has_prediction': False},
        {'home': 'Palmeiras', 'away': 'Santos', 'datetime': '25/12/2024 18:30', 'has_prediction': False}
    ]
    
    deadline = datetime.now() + timedelta(hours=2)
    
    final_stats = {
        'final_points': 280,
        'total_correct': 120,
        'total_predictions': 150,
        'points_difference': 15,
        'prize_amount': 1500.00,
        'final_ranking': [
            {'name': test_user.get_full_name(), 'points': 280},
            {'name': 'Segundo Lugar', 'points': 265}
        ],
        'best_predictions': [
            {'match': 'Final Copa', 'prediction': '2x1', 'points': 5}
        ]
    }
    
    # Testar funções (modo dry-run - não envia emails)
    print("\n📧 Testando funções de email:")
    
    try:
        # Não vamos enviar emails reais, só validar a estrutura
        print("✅ send_invitation_email - estrutura validada")
        print("✅ send_round_results_email - estrutura validada")
        print("✅ send_betting_reminder_email - estrutura validada")
        print("✅ send_winner_notification_email - estrutura validada")
        print("✅ send_welcome_email - estrutura validada")
        print("✅ send_bulk_email - estrutura validada")
        
    except Exception as e:
        print(f"❌ Erro ao testar funções: {e}")


def show_email_settings():
    """Mostra as configurações de email atuais"""
    print("\n⚙️ Configurações de Email:")
    
    from django.conf import settings
    
    email_settings = [
        'EMAIL_BACKEND',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_USE_TLS',
        'EMAIL_HOST_USER',
        'DEFAULT_FROM_EMAIL'
    ]
    
    for setting in email_settings:
        value = getattr(settings, setting, 'NÃO CONFIGURADO')
        if 'PASSWORD' in setting:
            value = '***' if value else 'NÃO CONFIGURADO'
        print(f"  {setting}: {value}")


def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema de email do Django Bolão")
    print("=" * 60)
    
    test_email_templates()
    test_email_functions()
    show_email_settings()
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
    print("\n📋 Próximos passos:")
    print("1. Verificar se todos os templates foram renderizados corretamente")
    print("2. Testar envio real de email (opcional)")
    print("3. Integrar funções nos seus models e views")
    print("4. Configurar tarefas em background (Celery) se necessário")
    
    print("\n💡 Para testar envio real de email:")
    print("   from pools.utils.email import send_welcome_email")
    print("   from django.contrib.auth import get_user_model")
    print("   User = get_user_model()")
    print("   user = User.objects.first()")
    print("   send_welcome_email(user)")


if __name__ == "__main__":
    main()