from django import template

register = template.Library()


@register.filter
def format_number(value):
    """1561540575620 → $1.56T, 36636361440 → $36.64B"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return value

    if value >= 1_000_000_000_000:
        return f'${value / 1_000_000_000_000:.2f}T'
    elif value >= 1_000_000_000:
        return f'${value / 1_000_000_000:.2f}B'
    elif value >= 1_000_000:
        return f'${value / 1_000_000:.2f}M'
    elif value >= 1_000:
        return f'${value / 1_000:.2f}K'
    else:
        return f'${value:.2f}'


@register.filter
def format_price(value):
    """Fiyat formatı: 77974.00 → $77,974.00"""
    try:
        value = float(value)
        return f'${value:,.2f}'
    except (TypeError, ValueError):
        return value


@register.filter
def format_currency(value):
    """Genel para formatı: 156100.00 → $156,100.00"""
    try:
        value = float(value)
        return f'${value:,.2f}'
    except (TypeError, ValueError):
        return value


@register.filter
def format_quantity(value):
    """8.00000000 → 8 veya 0.00500000 → 0.005"""
    try:
        f = float(value)
        if f == int(f):
            return f'{int(f):,}'
        return f'{f:.8f}'.rstrip('0')
    except (TypeError, ValueError):
        return value


@register.filter
def index(lst, i):
    """Liste indexleme: {{ matrix|index:0 }}"""
    try:
        return lst[i]
    except (IndexError, TypeError):
        return []


@register.filter
def split(value, delimiter):
    """String split: {{ 'a,b,c'|split:',' }}"""
    try:
        return value.split(delimiter)
    except (AttributeError, TypeError):
        return []