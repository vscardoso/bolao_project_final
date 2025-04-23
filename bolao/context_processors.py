from django.conf import settings

def inactivity_timeout(request):
    """Adiciona configuração de timeout de inatividade aos templates."""
    return {
        'INACTIVITY_TIMEOUT': getattr(settings, 'INACTIVITY_TIMEOUT', 30)
    }