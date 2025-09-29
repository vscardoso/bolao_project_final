# Execute este script para extrair as configurações atuais do settings.py
# Salve como: inspect_current_config.py

import os
import sys
from pathlib import Path

print("🔍 ANÁLISE DAS CONFIGURAÇÕES ATUAIS\n")
print("=" * 70)

# Adicionar o diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    # Importar settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
    import django
    django.setup()
    
    from django.conf import settings
    
    # 1. SECRET_KEY
    print("\n🔑 SECRET_KEY:")
    print(f"   Atual: {settings.SECRET_KEY[:20]}... (truncada)")
    print("   ⚠️  NUNCA compartilhe a chave completa!")
    
    # 2. DEBUG
    print(f"\n🐛 DEBUG:")
    print(f"   Valor: {settings.DEBUG}")
    if settings.DEBUG:
        print("   ⚠️  PERIGO: Debug ativo em produção!")
    
    # 3. ALLOWED_HOSTS
    print(f"\n🌐 ALLOWED_HOSTS:")
    print(f"   Valores: {settings.ALLOWED_HOSTS}")
    
    # 4. DATABASE
    print(f"\n💾 DATABASE:")
    db = settings.DATABASES['default']
    print(f"   Engine: {db.get('ENGINE', 'N/A')}")
    print(f"   Nome: {db.get('NAME', 'N/A')}")
    print(f"   Host: {db.get('HOST', 'N/A')}")
    print(f"   Port: {db.get('PORT', 'N/A')}")
    print(f"   User: {db.get('USER', 'N/A')}")
    print(f"   Password: {'***' if db.get('PASSWORD') else 'NÃO CONFIGURADO'}")
    
    # 5. EMAIL
    print(f"\n📧 EMAIL:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {getattr(settings, 'EMAIL_HOST', 'NÃO CONFIGURADO')}")
    print(f"   Port: {getattr(settings, 'EMAIL_PORT', 'NÃO CONFIGURADO')}")
    print(f"   User: {getattr(settings, 'EMAIL_HOST_USER', 'NÃO CONFIGURADO')}")
    print(f"   Password: {'***' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NÃO CONFIGURADO'}")
    print(f"   TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
    
    # 6. API KEYS
    print(f"\n🔌 API KEYS:")
    football_api = getattr(settings, 'FOOTBALL_DATA_API_KEY', None)
    if football_api:
        print(f"   Football-Data.org: {football_api[:10]}... (truncada)")
    else:
        print(f"   Football-Data.org: NÃO CONFIGURADO")
    
    # 7. STATIC/MEDIA
    print(f"\n📁 ARQUIVOS:")
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'NÃO CONFIGURADO')}")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    print("\n" + "=" * 70)
    print("✅ Análise concluída!")
    
except Exception as e:
    print(f"\n❌ Erro ao analisar configurações: {e}")
    print("\n💡 Vamos extrair diretamente do settings.py...")
    
    # Fallback: ler settings.py como texto
    settings_file = project_dir / 'bolao_config' / 'settings.py'
    if settings_file.exists():
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n📄 Configurações encontradas em settings.py:")
        
        # Procurar SECRET_KEY
        import re
        secret_match = re.search(r"SECRET_KEY\s*=\s*['\"]([^'\"]+)['\"]", content)
        if secret_match:
            print(f"   SECRET_KEY: {secret_match.group(1)[:20]}...")
        
        # Procurar DATABASE
        if 'mysql' in content.lower():
            print("   DATABASE: MySQL detectado")
        elif 'postgresql' in content.lower():
            print("   DATABASE: PostgreSQL detectado")
        elif 'sqlite' in content.lower():
            print("   DATABASE: SQLite detectado")