import os

def header(text):
    """Formatar cabeçalho para o output."""
    return f"\n{'='*80}\n{text}\n{'='*80}\n"

def collect_file_content(filepath):
    """Coletar conteúdo de um arquivo."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Erro ao ler arquivo {filepath}: {str(e)}"
    return f"Arquivo não encontrado: {filepath}"

def main():
    """Função principal para coletar conteúdo de arquivos."""
    core_files = [
        ('pools/models.py', "MODELS POOLS"),
        ('users/models.py', "MODELS USERS"),
        ('pools/forms.py', "FORMS POOLS"),
        ('pools/views.py', "VIEWS POOLS"),
        ('pools/tests.py', "TESTS POOLS"),
        ('pools/urls.py', "URLS POOLS"),
        ('bolao_config/urls.py', "URLS MAIN"),
    ]
    
    for filepath, title in core_files:
        print(header(title))
        print(collect_file_content(filepath))

if __name__ == "__main__":
    main()