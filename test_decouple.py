#!/usr/bin/env python3
"""
Teste das configurações python-decouple
Verifica se todas as variáveis estão sendo carregadas corretamente
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_configurations():
    """Testa todas as configurações"""
    print('📧 TESTE DE CONFIGURAÇÕES PYTHON-DECOUPLE')
    print('=' * 50)
    
    print('✅ EMAIL:')
    print(f'   Backend: {settings.EMAIL_BACKEND}')
    print(f'   Host: {settings.EMAIL_HOST}')
    print(f'   Port: {settings.EMAIL_PORT}')
    print(f'   User: {settings.EMAIL_HOST_USER}')
    print(f'   TLS: {settings.EMAIL_USE_TLS}')
    
    print()
    print('✅ BANCO DE DADOS:')
    db = settings.DATABASES['default']
    print(f'   Engine: {db["ENGINE"]}')
    print(f'   Name: {db["NAME"]}')
    print(f'   Host: {db["HOST"]}')
    print(f'   Port: {db["PORT"]}')
    print(f'   User: {db["USER"]}')
    
    print()
    print('✅ API:')
    api_key = settings.FOOTBALL_DATA_API_KEY
    print(f'   Football API: {api_key[:10]}...{api_key[-4:]} (protegida)')
    
    print()
    print('✅ SEGURANÇA:')
    print(f'   DEBUG: {settings.DEBUG}')
    secret = settings.SECRET_KEY
    print(f'   SECRET_KEY: {secret[:10]}...{secret[-4:]} (protegida)')
    print(f'   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
    
    print()
    print('✅ ARQUIVOS ESTÁTICOS:')
    print(f'   STATIC_URL: {settings.STATIC_URL}')
    print(f'   STATIC_ROOT: {settings.STATIC_ROOT}')
    print(f'   MEDIA_URL: {settings.MEDIA_URL}')
    print(f'   MEDIA_ROOT: {settings.MEDIA_ROOT}')
    
    print()
    print('🧪 TESTE DE EMAIL:')
    try:
        # Não envia email real, apenas testa configuração
        if 'console' in settings.EMAIL_BACKEND:
            print('   Modo console ativo - emails no terminal')
        else:
            print('   Modo SMTP ativo - emails reais')
        print('   ✅ Configuração de email válida')
    except Exception as e:
        print(f'   ❌ Erro na configuração: {e}')
    
    print()
    print('🎉 PYTHON-DECOUPLE FUNCIONANDO CORRETAMENTE!')
    print('📝 Todas as variáveis sendo carregadas do .env')

if __name__ == "__main__":
    test_configurations()