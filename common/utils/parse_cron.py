from datetime import datetime


def parse_cron(cron_str):
    """Парсит строку cron в компоненты."""
    parts = cron_str.strip().split()
    if len(parts) != 5:
        raise ValueError("Cron строка должна содержать 5 компонентов: минута, час, день, месяц, день недели")
    return {
        'minute': parts[0],
        'hour': parts[1],
        'day': parts[2],
        'month': parts[3],
        'weekday': parts[4]
    }


def matches_cron_field(value: int, pattern: str, max_value: int=None) -> bool:
    """
    Проверяет, соответствует ли значение шаблону cron для одного поля.
    :param value: Значение времени или даты (минута, час, день, месяц, день недели)
    :param pattern: То, что указано в паттерне для этого значения
    :param max_value: Максимально возможное значение, применяемое к этому паттерну
    """
    if value > max_value:
        return False

    if pattern == '*':
        return True
    if ',' in pattern:
        return str(value) in pattern.split(',')
    if '/' in pattern:
        step = int(pattern.split('/')[1])
        return value % step == 0
    if '-' in pattern:
        start, end = map(int, pattern.split('-'))
        return start <= value <= end
    return int(pattern) == value


def can_run_now(cron_str, current_time: datetime=None) -> bool:
    """
    Проверяет, можно ли запустить задачу по расписанию cron в текущий момент.
    :param cron_str: Строка в формате cron (минута час день месяц день_недели)
    :param current_time: datetime для тестирования (если None, используется текущее время)
    """
    if current_time is None:
        current_time = datetime.now()

    cron_schedule = parse_cron(cron_str)

    checks = [
        matches_cron_field(current_time.minute, cron_schedule['minute'], 59),
        matches_cron_field(current_time.hour, cron_schedule['hour'], 23),
        matches_cron_field(current_time.day, cron_schedule['day'], 31),
        matches_cron_field(current_time.month, cron_schedule['month'], 12),
        matches_cron_field(current_time.weekday(), cron_schedule['weekday'], 6)  # 0=Понедельник, 6=Воскресенье
    ]

    return all(checks)


# Пример использования
if __name__ == "__main__":
    # Примеры cron-расписаний
    test_cases = [
        "*/5 * * * *",  # Каждые 5 минут
        "0 9 * * 1-5",  # В 9:00 по будням
        "30 14 1 * *",  # В 14:30 первого числа каждого месяца
        "0 0 * * 0",  # В полночь по воскресеньям
    ]

    now = datetime.now()
    for cron in test_cases:
        try:
            result = can_run_now(cron)
            print(f"Cron: {cron} -> Можно запустить: {result} (время: {now})")
        except ValueError as e:
            print(f"Ошибка в cron {cron}: {e}")
