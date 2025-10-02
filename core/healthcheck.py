"""
Health Check Endpoint para Monitoramento
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import sys

def health_check(request):
    """
    Endpoint de health check para monitoramento.
    Retorna status da aplicação e suas dependências.
    
    URL: /health/
    """
    health_status = {
        'status': 'healthy',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'django_version': settings.VERSION if hasattr(settings, 'VERSION') else 'unknown',
        'debug': settings.DEBUG,
        'checks': {}
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'error: {str(e)}'
    
    # Check static files (apenas se STATIC_ROOT existe)
    import os
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        if os.path.exists(settings.STATIC_ROOT):
            health_status['checks']['static_files'] = 'ok'
        else:
            health_status['checks']['static_files'] = 'warning: STATIC_ROOT not found'
    
    # Status code: 200 se healthy, 503 se unhealthy
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    Endpoint de readiness check.
    Verifica se a aplicação está pronta para receber tráfego.
    
    URL: /ready/
    """
    # Verificação básica - pode ser expandida
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        return JsonResponse({'status': 'ready'}, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e)
        }, status=503)


def liveness_check(request):
    """
    Endpoint de liveness check.
    Verifica se a aplicação está viva (rodando).
    
    URL: /live/
    """
    return JsonResponse({'status': 'alive'}, status=200)
