from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filtro personalizado para acessar itens de dicionário no template
    Uso: {{ dict|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    """
    Filtro para subtração
    Uso: {{ value|subtract:arg }}
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """
    Filtro para multiplicação
    Uso: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """
    Filtro para divisão
    Uso: {{ value|divide:arg }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return value