from django import template

register = template.Library()

@register.filter
def sport_color(sport_name):
    """Retorna o código de cor hexadecimal para cada esporte"""
    colors = {
        'Futebol': '38b000',
        'Basquete': 'ff7b00',
        'Fórmula 1': 'd90429',
        'UFC': '212529',
        'Vôlei': '4cc9f0',
        'Tênis': '7209b7',
    }
    return colors.get(sport_name, '0077B6')

@register.filter
def sport_icon(sport_name):
    """Retorna a classe do ícone FontAwesome para cada esporte"""
    icons = {
        'Futebol': 'fas fa-futbol text-success',
        'Basquete': 'fas fa-basketball-ball text-warning',
        'Fórmula 1': 'fas fa-flag-checkered text-danger',
        'UFC': 'fas fa-fist-raised text-dark',
        'Vôlei': 'fas fa-volleyball-ball text-info',
        'Tênis': 'fas fa-table-tennis text-primary',
    }
    return icons.get(sport_name, 'fas fa-trophy text-primary')

@register.simple_tag
def placeholder_image_url(sport_name):
    """Gera a URL completa para uma imagem de placeholder do esporte"""
    return f"https://via.placeholder.com/500x250/{sport_color(sport_name)}/FFFFFF?text={sport_name}"