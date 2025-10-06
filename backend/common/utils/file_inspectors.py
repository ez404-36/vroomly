import importlib
import os
from pathlib import Path
from typing import Iterable, Any


def is_python_file(file_path: Path) -> bool:
	"""Проверяет, является ли файл Python файлом"""
	return file_path.suffix == '.py' and file_path.name != '__init__.py'


def get_all_python_files(
		root_dir: str | Path,
		only_names: str | Iterable[str] | None = None,
) -> list[Path]:
	"""Получает все Python файлы в проекте"""
	python_files = []

	if not only_names:
		_only_names = ()
	elif isinstance(only_names, str):
		_only_names = (only_names,)
	else:
		_only_names = only_names

	for root, dirs, files in os.walk(root_dir):
		# Пропускаем служебные директории
		dirs[:] = [
			d for d in dirs
			if not d.startswith('.') and d not in [
				'__pycache__', '.venv', '.env', 'tests', 'src', 'migrations'
			]
		]

		module_name = root.split('/')[-1]

		is_root_match = module_name in only_names

		for file in files:
			file_path = Path(root) / file
			if is_python_file(file_path):
				if only_names and file_path.stem not in only_names and not is_root_match:
					continue
				python_files.append(file_path)

	return python_files


def path_to_module_name(path: Path, start="apps") -> str:
	path_parts = path.parts
	models_file_module_path = '.'.join(path_parts[path_parts.index(start):])
	return models_file_module_path.removesuffix('.py')


def import_class(path_to_class: str) -> Any:
	"""
	Извлекает класс из модуля. Путь до класса записывается через точку.
	Пример: apps.users.models.User
	"""
	path_chunks = path_to_class.split(".")
	module_name = ".".join(path_chunks[:-1])
	module = importlib.import_module(module_name)
	return getattr(module, path_chunks[-1], None)
