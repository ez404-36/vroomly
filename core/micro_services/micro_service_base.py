import os
import sys


class MicroService:
    """
    Родительский класс для всех микросервисов.
    Хранит в себе имя сервиса и добавляет корневую директорию в PYTHONPATH
    """

    name: str

    def __init__(self, service_name: str):
        self.name = service_name


def init_service(service_name: str) -> MicroService:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    return MicroService(service_name)


def get_service_name() -> str:
    """
    Получает имя сервиса из service.py текущего микро-сервиса
    """
    try:
        from service import service
        if not isinstance(service, MicroService):
            raise ValueError("service должен быть сущностью MicroService")
        return service.name
    except ImportError:
        raise ImportError(
            "Не удалось импортировать service.py. Убедитесь, что файл существует и содержит переменную service."
        )
    except AttributeError:
        raise AttributeError("Переменная service не определена в service.py.")
