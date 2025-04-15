import os
import django
import inspect

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolao_config.settings')
django.setup()

# Importar o módulo de modelos
import pools.models

# Listar todos os modelos definidos no módulo
print("Modelos encontrados em pools.models:")
for name, obj in inspect.getmembers(pools.models):
    if isinstance(obj, type) and hasattr(obj, '_meta'):
        print(f"- {name}")
        # Listar campos
        print("  Campos:")
        for field in obj._meta.fields:
            print(f"  - {field.name}: {field.__class__.__name__}")
        # Listar relacionamentos
        print("  Relacionamentos:")
        for field in obj._meta.many_to_many:
            print(f"  - {field.name}: ManyToManyField")