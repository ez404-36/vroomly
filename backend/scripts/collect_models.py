import datetime
import os
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple

from common.utils.utils import get_all_python_files


class BaseModelCollector:
    def __init__(self, project_root: str, output_file: str):
        self.project_root = Path(project_root)
        self.output_file = Path(output_file)
        self.models: Dict[str, Dict] = {}  # name -> {code, file, dependencies}
        self.imports: Set[str] = set()
        self.processed_files: Set[str] = set()
        self.base_model_classes: Set[str] = {'BaseModel', 'APIModel'}

    def get_all_python_files(self) -> List[Path]:
        """Получает все Python файлы в проекте"""
        return get_all_python_files(self.project_root)

    @staticmethod
    def extract_imports_from_code(code: str) -> Set[str]:
        """Извлекает импорты из кода"""
        imports = set()
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(f"import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module = node.module
                        names = [alias.name for alias in node.names]
                        if names:
                            imports.add(f"from {module} import {', '.join(names)}")
        except Exception as e:
            print(f'[error] Не удалось извлечь импорты: {e}')
        return imports

    def is_base_model_class(self, class_node: ast.ClassDef, content: str) -> Tuple[bool, Set[str]]:
        """Проверяет, является ли класс Pydantic моделью (прямо или косвенно)"""
        dependencies = set()

        # Проверяем прямые базовые классы
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                # Прямое наследование от BaseModel
                if base_name == 'BaseModel':
                    return True, dependencies
                # Наследование от известной Pydantic модели
                elif base_name in self.base_model_classes:
                    dependencies.add(base_name)
                    return True, dependencies
            elif isinstance(base, ast.Attribute):
                if base.attr == 'BaseModel':
                    return True, dependencies

        # Если не нашли прямое наследование, проверяем все базовые классы рекурсивно
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                if base_name in self.models:
                    dependencies.add(base_name)
                    return True, dependencies

        return False, dependencies

    def extract_all_models(self, file_path: Path) -> List[Dict]:
        """Извлекает все классы из файла для последующего анализа"""
        classes = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Извлекаем код класса
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1

                    lines = content.split('\n')
                    class_code = '\n'.join(lines[start_line:end_line])

                    classes.append({
                        'name': node.name,
                        'code': class_code,
                        'node': node,
                        'file': str(file_path),
                        'imports': self.extract_imports_from_code(content),
                        'content': content
                    })

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

        return classes

    def collect_all_classes(self):
        """Собирает все классы из проекта для анализа"""
        python_files = self.get_all_python_files()
        all_classes = []

        for file_path in python_files:
            classes = self.extract_all_models(file_path)
            all_classes.extend(classes)
            self.processed_files.add(str(file_path))

        return all_classes

    def find_pydantic_models(self, all_classes: List[Dict]):
        """Находит все Pydantic модели среди всех классов"""
        # Первый проход: находим прямые наследники BaseModel
        for class_info in all_classes:
            class_node = class_info['node']
            is_base_model, deps = self.is_base_model_class(class_node, class_info['content'])

            if is_base_model:
                self.models[class_info['name']] = {
                    'code': class_info['code'],
                    'file': class_info['file'],
                    'imports': class_info['imports'],
                    'dependencies': deps
                }
                self.base_model_classes.add(class_info['name'])
                self.imports.update(class_info['imports'])

        # Второй проход: находим классы, наследующиеся от известных Pydantic моделей
        changed = True
        while changed:
            changed = False
            for class_info in all_classes:
                if class_info['name'] in self.models:
                    continue

                class_node = class_info['node']
                is_base_model, deps = self.is_base_model_class(class_node, class_info['content'])

                if is_base_model:
                    # Проверяем, что все зависимости уже в моделях
                    if all(dep in self.models for dep in deps):
                        self.models[class_info['name']] = {
                            'code': class_info['code'],
                            'file': class_info['file'],
                            'imports': class_info['imports'],
                            'dependencies': deps
                        }
                        self.base_model_classes.add(class_info['name'])
                        self.imports.update(class_info['imports'])
                        changed = True
                        print(f"Найдена модель через наследование: {class_info['name']}")

    def sort_models_by_dependencies(self) -> List[str]:
        """Сортирует модели по зависимостям (сначала базовые, потом производные)"""
        sorted_models = []
        visited = set()

        def visit(_model_name):
            if _model_name in visited:
                return
            visited.add(_model_name)

            if _model_name in self.models:
                for dep in self.models[_model_name]['dependencies']:
                    if dep in self.models:
                        visit(dep)

                sorted_models.append(_model_name)

        for model_name in self.models:
            visit(model_name)

        return sorted_models

    def collect_models(self):
        """Собирает все модели из проекта"""
        python_files = self.get_all_python_files()
        print(f"Найдено {len(python_files)} Python файлов для обработки")

        # Собираем все классы
        all_classes = self.collect_all_classes()
        print(f"Найдено {len(all_classes)} классов для анализа")

        # Находим Pydantic модели
        self.find_pydantic_models(all_classes)

        print(f"Итоговое количество Pydantic моделей: {len(self.models)}")

    def write_combined_file(self):
        """Записывает все модели в один файл"""
        # Фильтруем импорты, оставляя только нужные
        filtered_imports = set()
        for imp in self.imports:
            # Оставляем импорты pydantic, typing и стандартные модули
            if any(keyword in imp for keyword in ['pydantic', 'typing', 'datetime', 'decimal', 'uuid', 'enum']):
                filtered_imports.add(imp)

        # Добавляем обязательный импорт BaseModel
        filtered_imports.add("from pydantic import BaseModel")
        filtered_imports.add("from fastapi_utils.api_model import APIModel")

        # Сортируем модели по зависимостям
        sorted_model_names = self.sort_models_by_dependencies()

        Path(self.output_file).unlink(missing_ok=True)
        Path(self.output_file).parent.mkdir(exist_ok=True, parents=True)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Записываем заголовок
            f.write('"""\n')
            f.write('Автоматически сгенерированный файл со всеми Pydantic моделями\n')
            f.write(f"Дата генерации: {datetime.datetime.now()}\n")
            f.write(f'Собрано из {len(self.processed_files)} файлов\n')
            f.write(f'Найдено {len(self.models)} моделей\n')
            f.write('Сгенерировано автоматически\n')
            f.write('"""\n\n')

            # Записываем импорты
            for imp in sorted(filtered_imports):
                f.write(f'{imp}\n')

            f.write('\n\n')

            # Записываем модели в правильном порядке
            for model_name in sorted_model_names:
                model_data = self.models[model_name]
                f.write(f'# Модель: {model_name} (из {os.path.basename(model_data["file"])})\n')
                f.write(model_data['code'])
                f.write('\n\n')
                f.write('#' + '=' * 50 + '\n\n')

    def run(self):
        """Запускает процесс сбора моделей"""
        print("Начало сбора Pydantic моделей...")
        self.collect_models()
        print(f"Найдено {len(self.models)} уникальных моделей")
        self.write_combined_file()
        print(f"Модели сохранены в файл: {self.output_file}")


def main():
    project_root = "."
    output_file = "src/generated_models.py"

    collector = BaseModelCollector(project_root, output_file)
    collector.run()


if __name__ == "__main__":
    main()
    subprocess.run("uv run pydantic2ts --module src.generated_models --output /frontend/src/types/schemas.ts".split())
