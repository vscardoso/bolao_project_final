#!/usr/bin/env python3
"""
Script para configurar Gmail SMTP no Django Bolão
Facilita a configuração de email para produção

Autor: Sistema Django Bolão
Data: 29/09/2025
"""

import os
import re
from pathlib import Path
from getpass import getpass

def validate_gmail(email):
    """Valida se é um email Gmail válido"""
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

def validate_app_password(password):
    """Valida formato da senha de app (16 chars, pode ter espaços)"""
    # Remove espaços e verifica se tem 16 caracteres
    clean_password = password.replace(' ', '')
    return len(clean_password) == 16 and clean_password.isalnum()

def update_env_file(email, app_password):
    """Atualiza o arquivo .env com configurações de email"""
    env_path = Path('.env')
    
    # Ler .env atual
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # Remover configurações antigas de email
    lines = content.split('\n')
    new_lines = []
    in_email_section = False
    
    for line in lines:
        if line.startswith('# Email Configuration'):
            in_email_section = True
            continue
        elif line.startswith('EMAIL_') or line.startswith('DEFAULT_FROM_EMAIL'):
            continue
        elif line.strip() == "" and in_email_section:
            in_email_section = False
            continue
        elif not in_email_section:
            new_lines.append(line)
    
    # Remover linhas vazias no final
    while new_lines and new_lines[-1].strip() == "":
        new_lines.pop()
    
    # Configurações de email
    email_config = f"""
# Email Configuration (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={app_password}
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL={email}"""
    
    # Combinar conteúdo
    new_content = '\n'.join(new_lines) + email_config + '\n'
    
    # Salvar .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def update_env_example():
    """Atualiza o arquivo .env.example com exemplo de configuração"""
    env_example_path = Path('.env.example')
    
    if env_example_path.exists():
        with open(env_example_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # Verificar se já existe configuração de email
    if 'EMAIL_BACKEND' not in content:
        email_example = """
# Email Configuration (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your_email@gmail.com"""
        
        with open(env_example_path, 'a', encoding='utf-8') as f:
            f.write(email_example + '\n')

def main():
    """Função principal"""
    print("📧 CONFIGURAÇÃO DE EMAIL GMAIL")
    print("=" * 50)
    print()
    
    print("🔧 Este script irá configurar Gmail SMTP para o Django Bolão")
    print()
    print("📋 Pré-requisitos:")
    print("   ✅ Conta Gmail ativa")
    print("   ✅ Verificação em 2 etapas ativada")
    print("   ✅ Senha de app gerada no Gmail")
    print()
    
    # Confirmar pré-requisitos
    response = input("Você já tem uma senha de app do Gmail? (s/n): ").lower().strip()
    if response not in ['s', 'sim', 'y', 'yes']:
        print()
        print("🔗 Links importantes:")
        print("   📱 Ativar 2FA: https://myaccount.google.com/security")
        print("   🔑 Gerar senha: https://myaccount.google.com/apppasswords")
        print()
        print("❌ Configure os pré-requisitos primeiro e execute novamente.")
        return False
    
    print()
    print("📝 COLETA DE INFORMAÇÕES")
    print("-" * 30)
    
    # Solicitar email
    while True:
        email = input("Digite seu email Gmail: ").strip()
        if validate_gmail(email):
            break
        else:
            print("❌ Email inválido. Use um email Gmail válido (@gmail.com)")
    
    # Solicitar senha de app
    while True:
        print("\n🔐 Digite a senha de app (16 caracteres):")
        print("   💡 Formato: xxxx xxxx xxxx xxxx ou xxxxxxxxxxxxxxxx")
        app_password = getpass("Senha de app: ").strip()
        
        if validate_app_password(app_password):
            break
        else:
            print("❌ Senha inválida. Deve ter 16 caracteres alfanuméricos.")
    
    print()
    print("💾 SALVANDO CONFIGURAÇÕES")
    print("-" * 30)
    
    try:
        # Atualizar .env
        update_env_file(email, app_password)
        print("✅ Arquivo .env atualizado com sucesso")
        
        # Atualizar .env.example
        update_env_example()
        print("✅ Arquivo .env.example atualizado")
        
        print()
        print("🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 30)
        print(f"📧 Email: {email}")
        print("🔐 Senha: ****** (protegida)")
        print()
        print("📋 Próximos passos:")
        print("   1. Reiniciar servidor Django")
        print("   2. Executar teste de email: python test_email.py")
        print("   3. Verificar funcionamento")
        print()
        print("💡 Dica: Execute 'python test_email.py' para testar agora!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar configurações: {e}")
        return False

if __name__ == "__main__":
    main()