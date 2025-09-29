#!/usr/bin/env python3
"""
Script para alternar entre modos de email
Facilita mudança entre SMTP e Console

Autor: Sistema Django Bolão
Data: 29/09/2025
"""

import os
from pathlib import Path

def show_current_config():
    """Mostra configuração atual"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ Arquivo .env não encontrado")
        return
    
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📧 CONFIGURAÇÃO ATUAL DE EMAIL")
    print("=" * 40)
    
    for line in content.split('\n'):
        if line.startswith('EMAIL_BACKEND'):
            backend = line.split('=')[1].strip()
            if 'smtp' in backend.lower():
                print("🌐 Modo: SMTP (emails reais)")
            elif 'console' in backend.lower():
                print("🖥️  Modo: Console (desenvolvimento)")
            else:
                print(f"❓ Modo: {backend}")
        elif line.startswith('EMAIL_HOST_USER'):
            user = line.split('=')[1].strip()
            print(f"📧 Email: {user}")
        elif line.startswith('EMAIL_HOST='):
            host = line.split('=')[1].strip()
            print(f"🌐 Host: {host}")

def switch_to_console():
    """Muda para modo console (desenvolvimento)"""
    env_path = Path('.env')
    
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Comentar linha SMTP e descomentar console
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith('EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend'):
            new_lines.append(f'# {line}')
        elif line.startswith('# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend'):
            new_lines.append('EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend')
        else:
            new_lines.append(line)
    
    # Se não encontrou linha console, adicionar
    if 'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend' not in '\n'.join(new_lines):
        # Procurar seção de email e adicionar
        for i, line in enumerate(new_lines):
            if 'EMAIL (Gmail SMTP)' in line:
                new_lines.insert(i+3, 'EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend')
                break
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Configurado para modo CONSOLE (desenvolvimento)")
    print("📝 Emails serão exibidos no terminal, não enviados")

def switch_to_smtp():
    """Muda para modo SMTP (produção)"""
    env_path = Path('.env')
    
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Descomentar linha SMTP e comentar console
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith('# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend'):
            new_lines.append(line[2:])  # Remove #
        elif line.startswith('EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend'):
            new_lines.append(f'# {line}')
        else:
            new_lines.append(line)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Configurado para modo SMTP (produção)")
    print("⚠️  LEMBRE-SE: Precisa de senha de app válida para funcionar")

def update_gmail_password():
    """Atualiza senha do Gmail"""
    print("🔐 ATUALIZAÇÃO DE SENHA GMAIL")
    print("-" * 30)
    print("💡 Cole aqui a senha de app de 16 caracteres gerada no Gmail")
    print("📱 Gere em: https://myaccount.google.com/apppasswords")
    print()
    
    new_password = input("Nova senha de app: ").strip()
    
    if len(new_password.replace(' ', '')) != 16:
        print("❌ Senha deve ter 16 caracteres")
        return
    
    env_path = Path('.env')
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir senha
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if line.startswith('EMAIL_HOST_PASSWORD='):
            new_lines.append(f'EMAIL_HOST_PASSWORD={new_password}')
        else:
            new_lines.append(line)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Senha atualizada com sucesso!")
    print("🧪 Execute: python test_email.py")

def main():
    """Menu principal"""
    print("📧 GERENCIADOR DE CONFIGURAÇÃO DE EMAIL")
    print("=" * 50)
    print()
    
    show_current_config()
    print()
    
    print("🔧 OPÇÕES DISPONÍVEIS:")
    print("1. 🖥️  Modo Console (desenvolvimento)")
    print("2. 🌐 Modo SMTP (produção)")
    print("3. 🔐 Atualizar senha Gmail")
    print("4. 🧪 Testar email")
    print("5. 📋 Ver configuração")
    print("6. ❌ Sair")
    print()
    
    while True:
        try:
            choice = input("Escolha (1-6): ").strip()
            
            if choice == '1':
                switch_to_console()
                
            elif choice == '2':
                switch_to_smtp()
                
            elif choice == '3':
                update_gmail_password()
                
            elif choice == '4':
                print("🧪 Executando teste...")
                os.system('python test_email.py')
                
            elif choice == '5':
                print()
                show_current_config()
                
            elif choice == '6':
                print("👋 Até logo!")
                break
                
            else:
                print("❌ Opção inválida")
            
            print("\n" + "-"*40 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break

if __name__ == "__main__":
    main()