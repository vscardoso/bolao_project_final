import os
import re
from pathlib import Path
from collections import defaultdict

def find_bets_imports(root_dir='.'):
    """Encontra todas as referências ao app bets no código"""
    
    # Padrões a procurar
    patterns = [
        r'from\s+bets\.models\s+import',
        r'from\s+bets\s+import',
        r'import\s+bets',
        r'bets\.models\.',
        r'bets\.views\.',
        r'bets\.forms\.',
        r'bets\.admin\.',
        r"['\"]bets['\"]",  # String literal 'bets'
    ]
    
    # Diretórios a ignorar
    ignore_dirs = {
        'venv', '__pycache__', '.git', 'node_modules', 
        'staticfiles', 'media', 'migrations', '.vscode',
        'backups'
    }
    
    results = defaultdict(list)
    stats = {
        'total_files': 0,
        'affected_files': 0,
        'total_occurrences': 0
    }
    
    root_path = Path(root_dir)
    
    for py_file in root_path.rglob('*.py'):
        # Pular diretórios ignorados
        if any(ignored in py_file.parts for ignored in ignore_dirs):
            continue
            
        stats['total_files'] += 1
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            file_matches = []
            
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    if re.search(pattern, line):
                        file_matches.append({
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern
                        })
                        stats['total_occurrences'] += 1
            
            if file_matches:
                results[str(py_file)] = file_matches
                stats['affected_files'] += 1
                
        except Exception as e:
            print(f"⚠️  Erro ao ler {py_file}: {e}")
    
    return results, stats


def print_report(results, stats):
    """Imprime relatório formatado"""
    
    print("=" * 80)
    print("🔍 RELATÓRIO DE AUDITORIA - App Bets")
    print("=" * 80)
    print()
    
    # Estatísticas
    print("📊 Estatísticas:")
    print(f"   Total de arquivos .py analisados: {stats['total_files']}")
    print(f"   Arquivos com referências a bets: {stats['affected_files']}")
    print(f"   Total de ocorrências encontradas: {stats['total_occurrences']}")
    print()
    
    if not results:
        print("✅ Nenhuma referência ao app bets encontrada!")
        return
    
    # Detalhes por arquivo
    print("📄 Arquivos afetados:")
    print("-" * 80)
    
    for file_path, matches in sorted(results.items()):
        print(f"\n📁 {file_path}")
        print(f"   {len(matches)} ocorrência(s)")
        
        for match in matches[:5]:  # Mostrar no máximo 5 por arquivo
            print(f"   Linha {match['line']:4d}: {match['content'][:70]}")
        
        if len(matches) > 5:
            print(f"   ... e mais {len(matches) - 5} ocorrência(s)")
    
    print()
    print("=" * 80)
    
    # Sugestões
    print("\n💡 Próximos passos sugeridos:")
    print("   1. Revisar cada arquivo listado acima")
    print("   2. Substituir imports: bets.models → pools.models")
    print("   3. Atualizar referências em settings.py (INSTALLED_APPS)")
    print("   4. Remover app bets/ do projeto")
    print("   5. Executar testes para validar mudanças")


def generate_sed_commands(results):
    """Gera comandos sed para substituição automática"""
    
    print("\n🔧 Comandos para substituição automática:")
    print("-" * 80)
    
    replacements = [
        ("from bets.models import", "from pools.models import"),
        ("from bets import", "from pools import"),
        ("import bets.models", "import pools.models"),
        ("bets.models.", "pools.models."),
    ]
    
    for old, new in replacements:
        # Linux/Mac
        print(f"\n# Substituir '{old}' por '{new}'")
        print(f"find . -name '*.py' -type f -not -path '*/venv/*' -not -path '*/__pycache__/*' \\")
        print(f"  -exec sed -i 's/{old}/{new}/g' {{}} \\;")
        
        # Windows PowerShell alternativo
        print(f"\n# Windows PowerShell:")
        print(f"Get-ChildItem -Recurse -Filter '*.py' | Where-Object {{$_.FullName -notmatch 'venv|__pycache__'}} | ForEach-Object {{")
        print(f"    (Get-Content $_.FullName) -replace '{old}', '{new}' | Set-Content $_.FullName")
        print(f"}}")


if __name__ == '__main__':
    print("🔍 Iniciando auditoria de referências ao app bets...\n")
    
    results, stats = find_bets_imports()
    print_report(results, stats)
    generate_sed_commands(results)
    
    # Salvar relatório em arquivo
    output_file = 'bets_audit_report.txt'
    import sys
    original_stdout = sys.stdout
    with open(output_file, 'w', encoding='utf-8') as f:
        sys.stdout = f
        print_report(results, stats)
        generate_sed_commands(results)
    sys.stdout = original_stdout
    
    print(f"\n💾 Relatório completo salvo em: {output_file}")
