# cleanup_frontend.py

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_frontend():
    """Limpeza e reorganização completa do frontend"""
    
    project_root = Path('.')
    backup_dir = project_root / f'backups/frontend_cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("LIMPEZA E REORGANIZAÇÃO DO FRONTEND")
    print("=" * 80)
    
    # 1. BACKUP dos arquivos que vamos remover
    print("\n1. Criando backup...")
    
    files_to_backup = [
        'templates/base_old.html',
        'templates/base_modern.html',
        'templates/base_redirect.html',
        'templates/core/home_modern.html',
        'templates/pools/ranking_debug.html',
        'templates/pools/bet_form_example.html',
        'templates/pools/bet_form_simple.html',
    ]
    
    for file_path in files_to_backup:
        full_path = project_root / file_path
        if full_path.exists():
            dest = backup_dir / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(full_path, dest)
            print(f"  Backup: {file_path}")
    
    # 2. REMOVER duplicatas e versões antigas
    print("\n2. Removendo arquivos duplicados/antigos...")
    
    for file_path in files_to_backup:
        full_path = project_root / file_path
        if full_path.exists():
            full_path.unlink()
            print(f"  Removido: {file_path}")
    
    # 3. CONSOLIDAR templates duplicados (pools/templates → templates)
    print("\n3. Consolidando templates duplicados...")
    
    pools_template_dir = project_root / 'pools' / 'templates' / 'pools'
    main_template_dir = project_root / 'templates' / 'pools'
    
    if pools_template_dir.exists():
        for template in pools_template_dir.glob('*.html'):
            # Se não existe no principal, mover
            dest = main_template_dir / template.name
            if not dest.exists():
                shutil.copy2(template, dest)
                print(f"  Consolidado: {template.name}")
        
        # Fazer backup e remover pools/templates
        shutil.copytree(pools_template_dir, backup_dir / 'pools_templates', dirs_exist_ok=True)
        shutil.rmtree(project_root / 'pools' / 'templates')
        print(f"  ✓ Removido pools/templates/ (backup criado)")
    
    # 4. CRIAR base.html moderna com Bootstrap
    print("\n4. Criando base.html moderna...")
    
    base_html = """{% load static %}
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Sistema de bolão online para competições de futebol">
    <title>{% block title %}Bolão Online{% endblock %}</title>
    
    <!-- Bootstrap 5.3 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --info: #3b82f6;
            --dark: #1f2937;
            --light: #f9fafb;
        }
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        body {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            background: var(--light);
        }
        
        /* Navbar */
        .navbar {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .navbar-brand {
            font-weight: 700;
            font-size: 1.5rem;
            letter-spacing: -0.5px;
        }
        
        .navbar-brand:hover {
            transform: scale(1.05);
            transition: transform 0.2s;
        }
        
        /* Main content */
        main {
            flex: 1;
            padding: 2rem 0;
        }
        
        /* Cards */
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        
        /* Buttons */
        .btn {
            border-radius: 8px;
            font-weight: 500;
            padding: 0.5rem 1.5rem;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            border: none;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* Footer */
        footer {
            background: white;
            border-top: 1px solid #e5e7eb;
            padding: 2rem 0;
            margin-top: 4rem;
        }
        
        /* Alerts */
        .alert {
            border: none;
            border-radius: 8px;
        }
        
        /* Forms */
        .form-control, .form-select {
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            padding: 0.75rem 1rem;
        }
        
        .form-control:focus, .form-select:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">
                <i class="fas fa-trophy"></i> Bolão Online
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'dashboard' %}">
                                <i class="fas fa-chart-line me-1"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'pool_list' %}">
                                <i class="fas fa-list me-1"></i> Bolões
                            </a>
                        </li>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="fas fa-user-circle me-1"></i> {{ user.username }}
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><a class="dropdown-item" href="{% url 'profile' %}"><i class="fas fa-user me-2"></i> Perfil</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{% url 'logout' %}"><i class="fas fa-sign-out-alt me-2"></i> Sair</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'login' %}">Entrar</a>
                        </li>
                        <li class="nav-item">
                            <a class="btn btn-light btn-sm ms-2" href="{% url 'register' %}">Cadastrar</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Messages -->
    {% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            <i class="fas fa-{% if message.tags == 'success' %}check-circle{% elif message.tags == 'error' %}exclamation-circle{% else %}info-circle{% endif %} me-2"></i>
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5><i class="fas fa-trophy text-primary"></i> Bolão Online</h5>
                    <p class="text-muted">Crie bolões e dispute com seus amigos.</p>
                </div>
                <div class="col-md-6 text-md-end">
                    <p class="mb-0 text-muted">&copy; 2025 Bolão Online. Todos os direitos reservados.</p>
                </div>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>"""
    
    base_path = project_root / 'templates' / 'base.html'
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base_html)
    print(f"  ✓ base.html moderna criada com Bootstrap 5")
    
    # 5. CORRIGIR settings.py
    print("\n5. Corrigindo settings.py...")
    
    settings_path = project_root / 'bolao_config' / 'settings.py'
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings_content = f.read()
    
    # Adicionar TEMPLATES['DIRS'] se não existir
    if "'DIRS': [BASE_DIR / 'templates']" not in settings_content:
        settings_content = settings_content.replace(
            "'DIRS': [],",
            "'DIRS': [BASE_DIR / 'templates'],"
        )
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(settings_content)
        print(f"  ✓ TEMPLATES['DIRS'] configurado")
    else:
        print(f"  ✓ TEMPLATES['DIRS'] já estava configurado")
    
    # RESUMO
    print("\n" + "=" * 80)
    print("RESUMO DA LIMPEZA")
    print("=" * 80)
    print(f"✓ Backup criado em: {backup_dir}")
    print(f"✓ {len(files_to_backup)} arquivos antigos removidos")
    print(f"✓ Templates consolidados em templates/")
    print(f"✓ base.html moderna com Bootstrap 5 criada")
    print(f"✓ settings.py corrigido")
    print("\n" + "=" * 80)
    print("PRÓXIMOS PASSOS:")
    print("=" * 80)
    print("1. python manage.py collectstatic --noinput")
    print("2. python manage.py check")
    print("3. python manage.py runserver")
    print("4. Testar: http://127.0.0.1:8000/")
    print("=" * 80)

if __name__ == '__main__':
    cleanup_frontend()