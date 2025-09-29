# substituir_imports.py

import os
import re
from pathlib import Path

def replace_imports_in_file(file_path):
    """Substitui imports de bets por pools em um arquivo"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Substituições
        replacements = [
            (r'from bets\.models import', 'from pools.models import'),
            (r'from pools import models', 'from pools import models'),
            (r'import bets\.models', 'import pools.models'),
            (r'bets\.models\.', 'pools.models.'),
            (r'bets\.views\.', 'pools.views.'),
            (r'bets\.forms\.', 'pools.forms.'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Se houve mudanças, salvar
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False


def main():
    """Processa todos os arquivos .py do projeto"""
    
    ignore_dirs = {'venv', '__pycache__', '.git', 'migrations', 'backups'}
    
    files_changed = 0
    files_processed = 0
    
    for py_file in Path('.').rglob('*.py'):
        if any(ignored in py_file.parts for ignored in ignore_dirs):
            continue
        
        files_processed += 1
        if replace_imports_in_file(py_file):
            files_changed += 1
            print(f"✅ Atualizado: {py_file}")
    
    print(f"\n📊 Resumo:")
    print(f"   Arquivos processados: {files_processed}")
    print(f"   Arquivos modificados: {files_changed}")
    print(f"\n💡 Revise as mudanças com: git diff")


if __name__ == '__main__':
    print("🔄 Substituindo imports de bets por pools...\n")
    
    # Confirmação
    response = input("⚠️  Isso vai modificar arquivos. Continuar? (s/N): ")
    if response.lower() != 's':
        print("❌ Operação cancelada")
        exit(0)
    
    main()