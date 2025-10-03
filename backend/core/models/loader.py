import logging
from pathlib import Path

from core.models import AutoSchemaBase

base = AutoSchemaBase

logger = logging.getLogger(__name__)


def path_to_module_name(path: Path, start="apps") -> str:
    path_parts = path.parts
    models_file_module_path = '.'.join(path_parts[path_parts.index(start):])
    return models_file_module_path.removesuffix('.py')


def load_all_models() -> (set[str], list[str]):
    """
    Сканирует директорию apps/ и загружает модели из всех apps/<service>/models/*
    :return: Загруженные модели, ошибки
    """
    apps_dir = Path(__file__).parent.parent.parent / "apps"
    if not apps_dir.exists():
        raise FileNotFoundError("Директория apps/ не найдена")

    loaded_models = set()
    errors = []

    for service_dir in apps_dir.iterdir():
        if not service_dir.is_dir():
            continue

        service_name = service_dir.name
        root_models_dir = service_dir / "models"

        def load_models_in_module(models_dir: Path):
            if not models_dir.exists():
                return

            for model_file in models_dir.iterdir():
                if model_file.is_dir():
                    load_models_in_module(model_file)
                else:
                    file_name = model_file.stem
                    if (
                        file_name.startswith("__")
                        and file_name.endswith("__")
                        or model_file.suffix != ".py"
                    ):
                        continue
                    try:
                        models_file_module = path_to_module_name(model_file)
                        # Собираем все объекты, которые могут быть моделями
                        for name in filter(
                            lambda var: var != base.__name__, dir(models_file_module)
                        ):
                            obj = getattr(models_file_module, name)

                            if name in loaded_models:
                                errors.append(
                                    f'Model {name} already loaded before (current path: {models_file_module})'
                                )
                                continue

                            if (
                                isinstance(obj, type)
                                and issubclass(obj, base)
                                and obj is not base
                                and not name.endswith("Abstract")
                            ):
                                obj.metadata  # Регистрируем модель
                                loaded_models.add(name)
                    except ImportError as e:
                        logger.warning(
                            f"Предупреждение: Не удалось загрузить модели для сервиса {service_name}: {e}"
                        )
                        continue

        load_models_in_module(root_models_dir)
    return loaded_models, errors
