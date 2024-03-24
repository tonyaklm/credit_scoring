from datetime import date, datetime


def calculate_age(birth_date_str: str) -> int:
    """Calculates age from birthdate til now"""
    birth_date = datetime.strptime(birth_date_str, '%d.%m.%Y')
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def check_between(min_value, max_value, real_value) -> bool:
    """Checks if value in given interval"""
    try:
        return min_value <= real_value <= max_value
    except TypeError:
        return False
