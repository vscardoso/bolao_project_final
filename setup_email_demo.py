#!/usr/bin/env python3
"""
DEMONSTRAÇÃO PRÁTICA - Configuração Gmail SMTP
Execute este script para configurar email rapidamente

Autor: Sistema Django Bolão
Data: 29/09/2025
"""

import os
import subprocess
import sys
from pathlib import Path

def print_header():
    """Exibe cabeçalho"""
    print("📧" + "="*60 + "📧")
    print("📧  CONFIGURAÇÃO GMAIL SMTP - DJANGO BOLÃO         📧")
    print("📧" + "="*60 + "📧")
    print()

def print_instructions():
    """Exibe instruções passo a passo"""
    print("🎯 PRÉ-REQUISITOS GMAIL")
    print("-" * 40)
    print()
    print("1. 📱 ATIVAR VERIFICAÇÃO EM 2 ETAPAS:")
    print("   https://myaccount.google.com/security")
    print()
    print("2. 🔑 GERAR SENHA DE APP:")
    print("   https://myaccount.google.com/apppasswords")
    print("   • Selecione 'Email'")
    print("   • Digite 'Django Bolao'") 
    print("   • Copie a senha de 16 caracteres")
    print()
    print("3. ⚙️ CONFIGURAR NO PROJETO:")
    print("   • Execute: python configure_gmail.py")
    print("   • Informe seu email Gmail")
    print("   • Cole a senha de app")
    print()
    print("4. 🧪 TESTAR FUNCIONAMENTO:")
    print("   • Execute: python test_email.py")
    print("   • Verifique se o email chegou")
    print()

def check_files():
    """Verifica se os arquivos necessários existem"""
    files_to_check = [
        'configure_gmail.py',
        'test_email.py',
        'bolao_config/settings.py',
        '.env.example'
    ]
    
    print("📋 VERIFICAÇÃO DE ARQUIVOS")
    print("-" * 30)
    
    all_exists = True
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_exists = False
    
    print()
    return all_exists

def main():
    """Função principal de demonstração"""
    print_header()
    
    # Verificar arquivos
    if not check_files():
        print("❌ Alguns arquivos estão faltando!")
        print("💡 Certifique-se de executar no diretório do projeto")
        return
    
    # Exibir instruções
    print_instructions()
    
    # Menu de opções
    print("🔧 AÇÕES DISPONÍVEIS")
    print("-" * 30)
    print("1. 📖 Ver guia completo (email_setup_guide.md)")
    print("2. ⚙️ Configurar Gmail agora (configure_gmail.py)")
    print("3. 🧪 Testar email (test_email.py)")
    print("4. 📝 Ver configurações atuais")
    print("5. ❌ Sair")
    print()
    
    while True:
        try:
            choice = input("Escolha uma opção (1-5): ").strip()
            
            if choice == '1':
                print("\n📖 Abrindo guia completo...")
                if sys.platform.startswith('win'):
                    os.startfile('email_setup_guide.md')
                else:
                    subprocess.run(['open', 'email_setup_guide.md'], check=False)
                
            elif choice == '2':
                print("\n⚙️ Executando configuração Gmail...")
                subprocess.run([sys.executable, 'configure_gmail.py'])
                
            elif choice == '3':
                print("\n🧪 Executando teste de email...")
                subprocess.run([sys.executable, 'test_email.py'])
                
            elif choice == '4':
                print("\n📝 CONFIGURAÇÕES ATUAIS:")
                print("-" * 40)
                
                # Verificar .env
                env_path = Path('.env')
                if env_path.exists():
                    with open(env_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'EMAIL_HOST_USER=' in content:
                        for line in content.split('\n'):
                            if line.startswith('EMAIL_'):
                                if 'PASSWORD' in line:
                                    print(f"✅ {line.split('=')[0]}=****** (protegida)")
                                else:
                                    print(f"✅ {line}")
                    else:
                        print("❌ Configurações de email não encontradas no .env")
                        print("💡 Execute a opção 2 para configurar")
                else:
                    print("❌ Arquivo .env não encontrado")
                    print("💡 Execute a opção 2 para criar")
                
            elif choice == '5':
                print("\n👋 Até logo!")
                break
                
            else:
                print("❌ Opção inválida. Escolha 1-5.")
            
            print("\n" + "-"*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()