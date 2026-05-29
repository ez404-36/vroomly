import importlib
import logging
from pathlib import Path

from common.utils.file_inspectors import is_python_file, path_to_module_name
from core.models import AutoSchemaBase

base = AutoSchemaBase

logger = logging.getLogger(__name__)


def load_all_models() -> tuple[set[str], list[str]]:
	"""
	Сканирует директорию apps/ и загружает модели из всех apps/<service>/models/*
	:return: Загруженные модели, ошибки
	"""
	apps_dir = Path(__file__).parent.parent.parent / 'apps'
	if not apps_dir.exists():
		raise FileNotFoundError('Директория apps/ не найдена')

	loaded_models = set()
	errors = []

	for service_dir in apps_dir.iterdir():
		if not service_dir.is_dir():
			continue

		service_name = service_dir.name
		root_models_dir = service_dir / 'models'

		def load_models_in_module(models_dir: Path):
			if not models_dir.exists():
				return

			for model_file in models_dir.iterdir():
				if model_file.is_dir():
					load_models_in_module(model_file)
				else:
					if not is_python_file(model_file):
						continue
					try:
						models_file_module = importlib.import_module(path_to_module_name(model_file))
						# Собираем все объекты, которые могут быть моделями
						for name in filter(
							lambda var: var != base.__name__ and not var.startswith('_'), dir(models_file_module)
						):
							obj = getattr(models_file_module, name)

							# Учитываем только модели, ОПРЕДЕЛЁННЫЕ в этом модуле, а не
							# импортированные в его пространство имён. Иначе реэкспортированный
							# символ (например, базовый VehicleNode, импортируемый в каждый
							# модуль-деталь JTI) ложно считается повторной загрузкой.
							if (
								not isinstance(obj, type)
								or not issubclass(obj, base)
								or obj is base
								or name.endswith('Abstract')
								or obj.__module__ != models_file_module.__name__
							):
								continue

							if name in loaded_models:
								errors.append(
									f'Model {name} already loaded before (current path: {models_file_module})'
								)
								continue

							obj.metadata  # Регистрируем модель
							loaded_models.add(name)
					except ImportError as e:
						logger.warning(f'Предупреждение: Не удалось загрузить модели для сервиса {service_name}: {e}')
						continue

		load_models_in_module(root_models_dir)
	return loaded_models, errors
