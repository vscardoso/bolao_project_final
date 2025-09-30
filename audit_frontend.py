# Salve como: audit_frontend.py

import os
from pathlib import Path
from collections import defaultdict

def audit_frontend():
    """Audita estrutura de templates, static files e URLs"""
    
    project_root = Path('.')
    
    print("=" * 80)
    print("AUDITORIA COMPLETA DO FRONTEND")
    print("=" * 80)
    
    # 1. TEMPLATES
    print("\n1. ESTRUTURA DE TEMPLATES:")
    print("-" * 80)
    
    template_dirs = []
    for app in ['templates', 'core/templates', 'pools/templates', 'users/templates', 'bets/templates']:
        path = project_root / app
        if path.exists():
            template_dirs.append(app)
            count = len(list(path.rglob('*.html')))
            print(f"  {app}: {count} arquivos HTML")
            
            # Listar arquivos
            for html_file in sorted(path.rglob('*.html')):
                print(f"    - {html_file.relative_to(project_root)}")
    
    if not template_dirs:
        print("  ⚠️ NENHUM diretório de templates encontrado!")
    
    # 2. ARQUIVOS ESTÁTICOS
    print("\n2. ARQUIVOS ESTÁTICOS:")
    print("-" * 80)
    
    static_dirs = []
    for static_path in ['static', 'staticfiles', 'core/static', 'pools/static', 'users/static']:
        path = project_root / static_path
        if path.exists():
            static_dirs.append(static_path)
            
            # Contar por tipo
            css_count = len(list(path.rglob('*.css')))
            js_count = len(list(path.rglob('*.js')))
            img_count = len(list(path.rglob('*.png'))) + len(list(path.rglob('*.jpg'))) + len(list(path.rglob('*.svg')))
            
            print(f"  {static_path}:")
            print(f"    CSS: {css_count} arquivos")
            print(f"    JS: {js_count} arquivos")
            print(f"    Imagens: {img_count} arquivos")
    
    if not static_dirs:
        print("  ⚠️ NENHUM diretório static encontrado!")
    
    # 3. VERIFICAR base.html
    print("\n3. BASE TEMPLATE:")
    print("-" * 80)
    
    base_locations = [
        'templates/base.html',
        'core/templates/base.html',
        'pools/templates/base.html'
    ]
    
    base_found = False
    for loc in base_locations:
        path = project_root / loc
        if path.exists():
            print(f"  ✓ Encontrado: {loc}")
            base_found = True
            
            # Verificar conteúdo
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            has_bootstrap = 'bootstrap' in content.lower()
            has_static = '{% load static %}' in content or "{% load static %}" in content
            has_blocks = '{% block content %}' in content
            
            print(f"    Bootstrap: {'✓' if has_bootstrap else '✗'}")
            print("    {% load static %}: " + ('✓' if has_static else '✗'))
            print("    {% block content %}: " + ('✓' if has_blocks else '✗'))
    
    if not base_found:
        print("  ✗ NENHUM base.html encontrado!")
    
    # 4. VERIFICAR URLs
    print("\n4. CONFIGURAÇÃO DE URLS:")
    print("-" * 80)
    
    url_files = ['bolao_config/urls.py', 'core/urls.py', 'pools/urls.py', 'users/urls.py']
    
    for url_file in url_files:
        path = project_root / url_file
        if path.exists():
            print(f"  ✓ {url_file}")
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar imports importantes
            has_auth_urls = 'django.contrib.auth.urls' in content
            has_static_urls = 'django.conf.urls.static' in content
            
            if url_file == 'bolao_config/urls.py':
                print(f"    Auth URLs: {'✓' if has_auth_urls else '✗'}")
                print(f"    Static URLs: {'✓' if has_static_urls else '✗'}")
        else:
            print(f"  ✗ {url_file} não encontrado")
    
    # 5. VERIFICAR settings.py
    print("\n5. CONFIGURAÇÕES (settings.py):")
    print("-" * 80)
    
    settings_path = project_root / 'bolao_config' / 'settings.py'
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_templates_dir = "BASE_DIR / 'templates'" in content or "'DIRS': [BASE_DIR / 'templates']" in content
        has_static_url = 'STATIC_URL' in content
        has_staticfiles_dirs = 'STATICFILES_DIRS' in content
        has_media = 'MEDIA_URL' in content
        
        print(f"  TEMPLATES['DIRS']: {'✓' if has_templates_dir else '✗'}")
        print(f"  STATIC_URL: {'✓' if has_static_url else '✗'}")
        print(f"  STATICFILES_DIRS: {'✓' if has_staticfiles_dirs else '✗'}")
        print(f"  MEDIA_URL/MEDIA_ROOT: {'✓' if has_media else '✗'}")
    
    # 6. APPS INSTALADOS
    print("\n6. APPS COM TEMPLATES/STATIC:")
    print("-" * 80)
    
    apps_with_frontend = set()
    for app in ['core', 'pools', 'users', 'bets']:
        has_templates = (project_root / app / 'templates').exists()
        has_static = (project_root / app / 'static').exists()
        
        if has_templates or has_static:
            apps_with_frontend.add(app)
            print(f"  {app}:")
            print(f"    templates/: {'✓' if has_templates else '✗'}")
            print(f"    static/: {'✓' if has_static else '✗'}")
    
    # RECOMENDAÇÕES
    print("\n" + "=" * 80)
    print("RECOMENDAÇÕES:")
    print("=" * 80)
    
    issues = []
    
    if not base_found:
        issues.append("Criar templates/base.html com Bootstrap 5")
    
    if not template_dirs:
        issues.append("Criar estrutura de templates/")
    
    if len(template_dirs) > 2:
        issues.append(f"Consolidar templates (encontrados em {len(template_dirs)} locais diferentes)")
    
    if len(static_dirs) > 2:
        issues.append(f"Consolidar static files (encontrados em {len(static_dirs)} locais diferentes)")
    
    if 'bets' in apps_with_frontend:
        issues.append("Remover frontend do app 'bets' (já consolidado em pools)")
    
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("  Nenhum problema crítico encontrado!")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    audit_frontend()