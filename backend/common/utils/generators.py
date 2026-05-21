def generate_code(string: str) -> str:
    """
    Генерирует универсальный код объекта по его имени в формате.

    Примеры:
    * Foo Bar -> FOO_BAR
    * Ivan -> IVAN
    * Baz & Co -> BAZ_AND_CO
    * Bar (ex. kek) -> BAR_EX_KEK
    """

    return (
        string.upper()
        .replace(' ', '_')
        .replace('-', '_')
        .replace('/', '_')
        .replace('.', '')
        .replace('&', 'AND')
        .replace('+', 'AND')
        .replace('(', '')
        .replace(')', '')
    )


def generate_abbreviation(string: str) -> str:
    """
    Генерирует аббревиатуру по заглавным буквам в строке.

    Примеры:
    * Volkswagen-Audi Group -> VAG
    * General Motors -> GM
    """
    return ''.join(filter(lambda char: char.isupper(), string))
