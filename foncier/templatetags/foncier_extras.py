from django import template

register = template.Library()


@register.filter(name='fcfa')
def fcfa(value):
    """Formate un montant en FCFA avec séparateur de milliers (espace), ex: 22000000 -> 22 000 000."""
    if value in (None, ''):
        return '—'
    try:
        value = int(round(float(value)))
    except (TypeError, ValueError):
        return value
    return f"{value:,}".replace(',', ' ')
