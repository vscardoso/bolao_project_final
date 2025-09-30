"""
Sistema de emails para o Django Bolão - VERSÃO DEFINITIVA
Usando APENAS TEXTO PURO para garantir 100% entregabilidade

TESTADO E APROVADO: 29/09/2025 11:21
- Emails texto puro: ✅ CHEGAM  
- Emails HTML: ❌ NÃO CHEGAM

Esta versão substitui completamente o sistema anterior
"""

# Importar todas as funções do sistema TEXT-ONLY
from .email_text_only import (
    send_text_welcome_email as send_welcome_email,
    send_text_invitation_email as send_invitation_email,
    send_text_results_email as send_round_results_email,
    send_text_reminder_email as send_betting_reminder_email,
    send_text_winner_email as send_winner_notification_email,
)

# Re-exportar para manter compatibilidade com código existente
__all__ = [
    'send_welcome_email',
    'send_invitation_email', 
    'send_round_results_email',
    'send_betting_reminder_email',
    'send_winner_notification_email',
]

# Função de teste para validar funcionamento
def test_email_system():
    """Testa o sistema de email definitivo"""
    from .email_text_only import send_test_email_now
    return send_test_email_now()

# Aliases para compatibilidade
send_invitation_email_original = send_invitation_email
send_round_results_email_original = send_round_results_email
send_betting_reminder_email_original = send_betting_reminder_email
send_winner_notification_email_original = send_winner_notification_email