import os
import sys
import importlib
import inspect
import subprocess
import django
from django.urls import get_resolver
from django.apps import apps
from io import StringIO
from contextlib import redirect_stdout

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

def header(text):
    """Formatar cabeçalho para o output."""
    return f"\n{'='*80}\n{text}\n{'='*80}\n"

def collect_file_content(filepath):
    """Coletar conteúdo de um arquivo."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    return f"Arquivo não encontrado: {filepath}"

def get_project_structure():
    """Obter a estrutura de diretórios do projeto."""
    result = []
    for root, dirs, files in os.walk('.'):
        # Excluir diretórios de ambiente virtual e cache
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 4 * level
        result.append(f"{indent}{os.path.basename(root)}/")
        for file in files:
            if file.endswith(('.py', '.html', '.js', '.css')):
                result.append(f"{indent}    {file}")
    return '\n'.join(result)

def get_urls():
    """Obter todas as URLs configuradas."""
    resolver = get_resolver()
    url_patterns = []
    
    def extract_patterns(resolver, prefix=''):
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'url_patterns'):
                extract_patterns(pattern, prefix + str(pattern.pattern))
            else:
                url_patterns.append(f"{prefix}{pattern.pattern} → {pattern.callback.__module__}.{pattern.callback.__name__}")
    
    extract_patterns(resolver)
    return '\n'.join(url_patterns)

def get_models_info():
    """Obter informações sobre todos os modelos."""
    result = []
    for model in apps.get_models():
        result.append(f"Modelo: {model.__name__} ({model.__module__})")
        result.append("  Campos:")
        for field in model._meta.fields:
            result.append(f"    {field.name}: {field.__class__.__name__}")
        result.append("  Métodos:")
        for name, method in inspect.getmembers(model, inspect.isfunction):
            if not name.startswith('__'):
                result.append(f"    {name}")
        result.append("")
    return '\n'.join(result)

def run_test_with_details(test_path):
    """Executar um teste específico com detalhes completos."""
    result = subprocess.run(
        [sys.executable, 'manage.py', 'test', test_path, '-v', '3'],
        capture_output=True,
        text=True
    )
    return result.stdout + result.stderr

def main():
    """Função principal para coletar todas as informações."""
    project_info = {}
    
    # Coletar estrutura do projeto
    project_info['structure'] = get_project_structure()
    
    # Coletar conteúdo dos arquivos principais
    project_info['models_pools'] = collect_file_content('pools/models.py')
    project_info['models_users'] = collect_file_content('users/models.py')
    project_info['views_pools'] = collect_file_content('pools/views.py')
    project_info['forms_pools'] = collect_file_content('pools/forms.py')
    project_info['tests_pools'] = collect_file_content('pools/tests.py')
    project_info['urls_pools'] = collect_file_content('pools/urls.py')
    project_info['urls_main'] = collect_file_content('bolao_config/urls.py')
    
    # Coletar informações do sistema
    project_info['all_urls'] = get_urls()
    project_info['models_info'] = get_models_info()
    
    # Executar testes específicos que estão falhando
    failing_tests = [
        'pools.tests.BetFormTests.test_bet_form_widget_attrs',
        'pools.tests.BetModelTest.test_bet_points_earned',
        'pools.tests.BetModelTest.test_bet_str_representation',
        'pools.tests.PointCalculationTests.test_bet_points_draw'
    ]
    
    for test in failing_tests:
        test_name = test.split('.')[-1]
        project_info[f'test_{test_name}'] = run_test_with_details(test)
    
    # Imprimir todas as informações coletadas
    print(header("INFORMAÇÕES DETALHADAS DO PROJETO BOLÃO ONLINE"))
    
    for key, value in project_info.items():
        print(header(key.upper().replace('_', ' ')))
        print(value)
    
    print("\n\nCopie e cole todo este output para compartilhar com o assistente.")

if __name__ == "__main__":
    main()