#!/usr/bin/env python3
"""
Script para implementar melhorias de segurança no Django
Cria arquivo .env e atualiza settings.py para usar variáveis de ambiente
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key():
    """Gera uma nova SECRET_KEY segura"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for _ in range(50))

def create_env_file():
    """Cria arquivo .env com configurações seguras"""
    project_dir = Path(__file__).parent
    env_file = project_dir / '.env'
    
    # Ler configurações atuais do settings.py
    settings_file = project_dir / 'bolao_config' / 'settings.py'
    
    env_content = f"""# Configurações de Ambiente do Django
# Gerado automaticamente em 29/09/2025

# Segurança
SECRET_KEY={generate_secret_key()}
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados
DB_NAME=bolao_online
DB_USER=bolao_user
DB_PASSWORD=senha_super_segura_nova
DB_HOST=localhost
DB_PORT=3306

# APIs
FOOTBALL_DATA_API_KEY=bd9aef7e419a40e2b95c6d345c634c1c

# Email (desenvolvimento)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=naoresponda@bolaoonline.com

# Email (produção - comentado)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=seu-email@provedor.com
# EMAIL_HOST_PASSWORD=sua-senha-de-app

# Sessão
SESSION_COOKIE_AGE=7200
INACTIVITY_TIMEOUT=30
"""
    
    if env_file.exists():
        backup_file = project_dir / '.env.backup'
        env_file.rename(backup_file)
        print(f"✅ Backup do .env existente criado: {backup_file}")
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Arquivo .env criado: {env_file}")
    return env_file

def create_secure_settings():
    """Cria nova versão do settings.py usando variáveis de ambiente"""
    project_dir = Path(__file__).parent
    settings_file = project_dir / 'bolao_config' / 'settings.py'
    
    secure_settings = '''"""
Django settings for bolao_config project.
Versão segura usando variáveis de ambiente.
Gerado automaticamente em 29/09/2025.
"""

from pathlib import Path
import os
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Aplicações do projeto
    'pools',
    'users',
    'core',
    # Aplicações terceiras
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bolao_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bolao.context_processors.inactivity_timeout',
            ],
        },
    },
]

WSGI_APPLICATION = 'bolao_config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

# Login and Authentication
LOGIN_REDIRECT_URL = 'users:dashboard'
LOGOUT_REDIRECT_URL = 'core:home'
ACCOUNT_LOGOUT_ON_GET = True

# Email configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='naoresponda@bolaoonline.com')

# Session configuration
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=7200, cast=int)
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
INACTIVITY_TIMEOUT = config('INACTIVITY_TIMEOUT', default=30, cast=int)

# Security settings (uncomment for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Debug Toolbar (only in development)
if DEBUG:
    INTERNAL_IPS = ['127.0.0.1']

# API Keys
FOOTBALL_DATA_API_KEY = config('FOOTBALL_DATA_API_KEY')
'''
    
    # Backup do settings.py atual
    backup_file = settings_file.with_suffix('.py.backup')
    if settings_file.exists():
        settings_file.rename(backup_file)
        print(f"✅ Backup do settings.py criado: {backup_file}")
    
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write(secure_settings)
    
    print(f"✅ Novo settings.py seguro criado: {settings_file}")

def create_requirements_update():
    """Atualiza requirements.txt com nova dependência"""
    project_dir = Path(__file__).parent
    req_file = project_dir / 'requirements.txt'
    
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'python-decouple' not in content:
            with open(req_file, 'a', encoding='utf-8') as f:
                f.write('\\npython-decouple==3.8\\n')
            print("✅ python-decouple adicionado ao requirements.txt")
    else:
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write('python-decouple==3.8\\n')
        print("✅ requirements.txt criado com python-decouple")

def create_gitignore_update():
    """Atualiza .gitignore para não versionear .env"""
    project_dir = Path(__file__).parent
    gitignore_file = project_dir / '.gitignore'
    
    gitignore_content = '''# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal

# Arquivos de configuração sensíveis
.env
.env.local
.env.*.local

# Media files
media/

# Static files (coletados)
staticfiles/

# Coverage reports
htmlcov/
.coverage
.coverage.*

# pytest
.pytest_cache/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Backup files
*.backup
'''
    
    with open(gitignore_file, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print(f"✅ .gitignore atualizado: {gitignore_file}")

def main():
    """Função principal"""
    print("🔒 IMPLEMENTANDO MELHORIAS DE SEGURANÇA")
    print("=" * 50)
    
    try:
        # 1. Criar arquivo .env
        env_file = create_env_file()
        
        # 2. Criar settings.py seguro
        create_secure_settings()
        
        # 3. Atualizar requirements.txt
        create_requirements_update()
        
        # 4. Atualizar .gitignore
        create_gitignore_update()
        
        print("\\n🎉 MELHORIAS IMPLEMENTADAS COM SUCESSO!")
        print("=" * 50)
        print("\\n📋 PRÓXIMOS PASSOS:")
        print("1. pip install python-decouple")
        print("2. Edite o arquivo .env com suas configurações")
        print("3. Teste o projeto: python manage.py check")
        print("4. Atualize a senha do banco de dados")
        print("5. Configure ALLOWED_HOSTS para produção")
        print("\\n⚠️  IMPORTANTE:")
        print("- Backups foram criados (.backup)")
        print("- NUNCA versione o arquivo .env")
        print("- Teste em desenvolvimento antes de usar em produção")
        
    except Exception as e:
        print(f"\\n❌ Erro: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())