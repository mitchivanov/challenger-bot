import re

def validate_phone(phone: str) -> bool:
    # Пример: +79991234567, 89991234567, 79991234567
    pattern = re.compile(r'^(\+7|7|8)\d{10}$')
    digits = re.sub(r'\D', '', phone)
    if phone.startswith('+'):
        digits = '+' + digits
    return bool(pattern.match(digits)) 