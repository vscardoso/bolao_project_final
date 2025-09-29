# Script para gerar senha segura para MySQL
import secrets
import string

def generate_secure_password(length=16):
    """Gera uma senha segura com letras, números e símbolos"""
    # Definir caracteres permitidos (evitando símbolos problemáticos para MySQL)
    letters = string.ascii_letters
    digits = string.digits
    symbols = "!@#$%^*+-=[]{}|;:,.<>?"
    
    # Garantir pelo menos um de cada tipo
    password = [
        secrets.choice(letters.upper()),  # Uma maiúscula
        secrets.choice(letters.lower()),  # Uma minúscula  
        secrets.choice(digits),           # Um número
        secrets.choice(symbols)           # Um símbolo
    ]
    
    # Preencher o resto aleatoriamente
    all_chars = letters + digits + symbols
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Embaralhar a senha
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

print("🔐 GERANDO SENHAS SEGURAS PARA MYSQL")
print("=" * 50)

print("\n💾 Senhas para MySQL:")
for i in range(3):
    password = generate_secure_password(16)
    print(f"Opção {i+1}: {password}")

print("\n🔑 Senhas para outros usos:")
for i in range(2):
    password = generate_secure_password(20)
    print(f"Extra {i+1}: {password}")

print("\n" + "=" * 50)
print("💡 Escolha uma senha e use nos comandos:")
print("   ALTER USER 'bolao_user'@'localhost' IDENTIFIED BY 'nova_senha';")
print("   E atualize o .env com: DB_PASSWORD=nova_senha")