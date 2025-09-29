# Salve como: generate_secret_key.py

from django.core.management.utils import get_random_secret_key

print("\n🔑 GERANDO NOVA SECRET_KEY\n")
print("=" * 70)

# Gerar 3 chaves para você escolher
for i in range(3):
    key = get_random_secret_key()
    print(f"\nOpção {i+1}:")
    print(key)

print("\n" + "=" * 70)
print("💡 Copie uma das chaves acima e cole em seu .env")
print("   SECRET_KEY=sua_chave_aqui")