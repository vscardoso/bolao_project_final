"""
Django Production Settings
IMPORTANTE: Use este arquivo em produção com as variáveis de ambiente corretas
"""

from .settings import *
import os

# ========================================
# SEGURANÇA CRÍTICA
# ========================================

# DEBUG deve ser False em produção
DEBUG = False

# Hosts permitidos - DEVE ser configurado com seu domínio real
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Secret key da produção (NUNCA use a mesma do dev)
SECRET_KEY = os.getenv('SECRET_KEY')

# ========================================
# HTTPS E SSL
# ========================================

# Redirecionar todo tráfego HTTP para HTTPS
SECURE_SSL_REDIRECT = True

# Proteção XSS do navegador
SECURE_BROWSER_XSS_FILTER = True

# Impedir MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# ========================================
# COOKIES SEGUROS
# ========================================

# Cookies só por HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Proteções adicionais de cookies
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# ========================================
# HSTS (HTTP Strict Transport Security)
# ========================================

# 1 ano em segundos
SECURE_HSTS_SECONDS = 31536000

# Incluir subdomínios
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Preload HSTS
SECURE_HSTS_PRELOAD = True

# ========================================
# PROTEÇÃO DE FRAME
# ========================================

# Prevenir clickjacking
X_FRAME_OPTIONS = 'DENY'

# ========================================
# MIDDLEWARE ADICIONAL DE SEGURANÇA
# ========================================

# Adicionar middleware de segurança no início
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
] + [m for m in MIDDLEWARE if m != 'django.middleware.security.SecurityMiddleware']

# Remover Debug Toolbar em produção
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [m for m in MIDDLEWARE if 'debug_toolbar' not in m]

# ========================================
# LOGGING
# ========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/production.log'),
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'pools': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ========================================
# ARQUIVOS ESTÁTICOS (Produção)
# ========================================

# WhiteNoise para servir arquivos estáticos
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Compressão e cache de estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========================================
# EMAIL (Produção)
# ========================================

# Configurar com SendGrid, AWS SES, ou outro SMTP real
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'naoresponda@bolaoonline.com')

# Administradores para receber emails de erro
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'admin@bolaoonline.com')),
]

# ========================================
# CACHE (Produção - Redis recomendado)
# ========================================

# Se tiver Redis configurado, use:
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# ========================================
# BANCO DE DADOS (Produção)
# ========================================

# Garantir que usa credenciais do ambiente
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}

# ========================================
# SENTRY (Error Tracking - Opcional)
# ========================================

# Descomentar após configurar Sentry
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
#
# sentry_sdk.init(
#     dsn=os.getenv('SENTRY_DSN'),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=0.1,
#     send_default_pii=True
# )

# ========================================
# COMPRESSÃO E PERFORMANCE
# ========================================

# Compressão de respostas
MIDDLEWARE.append('django.middleware.gzip.GZipMiddleware')

# Cache de templates em produção (desabilitado temporariamente)
# for template_engine in TEMPLATES:
#     if 'OPTIONS' in template_engine:
#         template_engine['OPTIONS']['loaders'] = [
#             ('django.template.loaders.cached.Loader', [
#                 'django.template.loaders.filesystem.Loader',
#                 'django.template.loaders.app_directories.Loader',
#             ]),
#         ]
