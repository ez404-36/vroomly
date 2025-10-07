import datetime
import os
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple

from common.utils.file_inspectors import get_all_python_files
from core.constants import BACKEND_DIR


class BaseModelCollector:
    def __init__(self, project_root: str | Path, output_file: str | Path):
        self.project_root = Path(project_root)
        self.output_file = Path(output_file)
        self.models: Dict[str, Dict] = {}  # name -> {code, file, dependencies}
        self.custom_types: Dict[str, Dict] = {}  # name -> {code, file, dependencies}
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

    def extract_custom_types_from_code(self, content: str, file_path: Path) -> List[Dict]:
        """Извлекает кастомные типы (type aliases) из кода"""
        custom_types = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Обрабатываем type aliases (Python 3.12+)
                if isinstance(node, ast.TypeAlias):
                    type_name = node.name.id
                    start_line = node.lineno - 1
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1

                    lines = content.split('\n')
                    type_code = '\n'.join(lines[start_line:end_line])

                    custom_types.append({
                        'name': type_name,
                        'code': type_code,
                        'file': str(file_path),
                        'imports': self.extract_imports_from_code(content)
                    })

                # Обрабатываем старые style type aliases (присваивание)
                elif isinstance(node, ast.Assign):
                    if (node.targets and
                            isinstance(node.targets[0], ast.Name) and
                            isinstance(node.value, (ast.Subscript, ast.BinOp, ast.Name, ast.Attribute))):

                        # Проверяем, похоже ли это на объявление типа
                        target_name = node.targets[0].id
                        if target_name.isupper():  # Обычно типы называют в UPPER_CASE
                            start_line = node.lineno - 1
                            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1

                            lines = content.split('\n')
                            type_code = '\n'.join(lines[start_line:end_line])

                            # Проверяем, содержит ли код аннотацию типа
                            if any(keyword in type_code for keyword in ['Union', 'List', 'Dict', 'Optional', 'Any']):
                                custom_types.append({
                                    'name': target_name,
                                    'code': type_code,
                                    'file': str(file_path),
                                    'imports': self.extract_imports_from_code(content)
                                })

        except Exception as e:
            print(f"Ошибка при извлечении кастомных типов из {file_path}: {e}")

        return custom_types

    def normalize_indentation(self, code: str) -> str:
        """Нормализует отступы, заменяя табы на пробелы"""
        lines = code.split('\n')
        normalized_lines = []

        for line in lines:
            # Заменяем табы на 4 пробела
            normalized_line = line.replace('\t', '    ')
            normalized_lines.append(normalized_line)

        return '\n'.join(normalized_lines)

    def get_pydantic_models_in_annotation(self, class_node: ast.ClassDef) -> set[str]:
        annotated_models = set()

        def check_is_base_class_and_add_to_output(annotation_value: str | None):
            _val = annotation_value or ""
            if _val in self.base_model_classes:
                annotated_models.add(_val)
            if _val.endswith("Schema"):
                annotated_models.add(_val)
                self.base_model_classes.add(_val)

        for child in class_node.body:   # type: ast.AnnAssign
            annotation = getattr(child, 'annotation', None)
            if not annotation:
                continue

            if isinstance(annotation, ast.Name):
                check_is_base_class_and_add_to_output(getattr(annotation, "id", None))

            elif isinstance(annotation, ast.Subscript):
                check_is_base_class_and_add_to_output(getattr(annotation.slice, "id", ""))
                check_is_base_class_and_add_to_output(getattr(annotation.value, "id", ""))

            elif isinstance(annotation, ast.BinOp):
                check_is_base_class_and_add_to_output(getattr(annotation.left, "id", ""))
                check_is_base_class_and_add_to_output(getattr(annotation.right, "id", ""))
            else:
                print(f"[warning] Необработанный тип в {class_node.name}: {child.target.id}")

        return annotated_models

    def is_base_model_class(self, class_node: ast.ClassDef, content: str) -> Tuple[bool, Set[str]]:
        """Проверяет, является ли класс Pydantic моделью (прямо или косвенно)"""
        dependencies = self.get_pydantic_models_in_annotation(class_node)

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

                    class_code = self.normalize_indentation(class_code)

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

    def collect_all_classes_and_types(self):
        """Собирает все классы и кастомные типы из проекта для анализа"""
        python_files = self.get_all_python_files()
        all_classes = []

        for file_path in python_files:
            classes = self.extract_all_models(file_path)
            all_classes.extend(classes)

            # Собираем кастомные типы
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                custom_types = self.extract_custom_types_from_code(content, file_path)

                for type_info in custom_types:
                    if type_info['name'] not in self.custom_types:
                        type_info['code'] = self.normalize_indentation(type_info['code'])
                        self.custom_types[type_info['name']] = type_info
                        self.imports.update(type_info['imports'])
                        print(f"Найден кастомный тип: {type_info['name']} в {file_path}")
            except Exception as e:
                print(f"Ошибка при сборе кастомных типов из {file_path}: {e}")

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
                    missing_deps = [dep for dep in deps if dep not in self.models]
                    if not missing_deps:
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

    def sort_models_by_dependencies2(self) -> List[str]:
        """Сортирует модели по зависимостям (сначала базовые, потом производные)"""
        # Создаем копию моделей для работы
        models_to_sort = self.models.copy()
        sorted_models = []

        # Сначала добавляем модели без зависимостей
        models_without_deps = [
            name for name, data in models_to_sort.items()
            if not data['dependencies'] or all(dep not in models_to_sort for dep in data['dependencies'])
        ]

        for model_name in models_without_deps:
            sorted_models.append(model_name)
            del models_to_sort[model_name]

        # Затем добавляем остальные модели в порядке их обнаружения
        # Это дает более предсказуемый порядок, чем строгая топологическая сортировка
        remaining_models = list(models_to_sort.keys())

        # Пытаемся упорядочить по зависимостям, но не строго
        for model_name in remaining_models:
            if model_name not in sorted_models:
                # Вставляем перед зависимостями, если это возможно
                model_deps = [dep for dep in self.models[model_name]['dependencies'] if dep in sorted_models]

                if model_deps:
                    # Находим максимальную позицию среди зависимостей
                    max_dep_index = max(sorted_models.index(dep) for dep in model_deps)
                    # Вставляем после последней зависимости
                    insert_index = max_dep_index + 1
                else:
                    # Нет зависимостей - вставляем в начало
                    insert_index = 0

                # Вставляем модель на найденную позицию
                sorted_models.insert(insert_index, model_name)

        return sorted_models

    def topological_sort(self) -> List[str]:
        """Топологическая сортировка моделей по зависимостям"""
        graph = {}
        in_degree = {}

        # Инициализируем граф и степени входа
        for model_name in self.models:
            graph[model_name] = set()
            in_degree[model_name] = 0

        # Строим граф зависимостей
        for model_name, model_info in self.models.items():
            for dep in model_info['dependencies']:
                if dep in self.models:
                    graph[dep].add(model_name)

        # Вычисляем степени входа
        for model_name in graph:
            for dependent in graph[model_name]:
                in_degree[dependent] += 1

        # Находим модели без зависимостей (степень входа = 0)
        queue = [model for model in in_degree if in_degree[model] == 0]
        sorted_models = []

        while queue:
            model = queue.pop(0)
            sorted_models.append(model)

            for dependent in graph[model]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Проверяем, все ли модели были отсортированы
        if len(sorted_models) != len(self.models):
            print("Предупреждение: Обнаружена циклическая зависимость! Модели могут быть не полностью отсортированы.")
            # Добавляем оставшиеся модели в конец
            remaining = [model for model in self.models if model not in sorted_models]
            sorted_models.extend(remaining)

        return sorted_models

    def collect_models(self):
        """Собирает все модели из проекта"""
        python_files = self.get_all_python_files()
        print(f"Найдено {len(python_files)} Python файлов для обработки")

        # Собираем все классы
        all_classes = self.collect_all_classes_and_types()
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
        sorted_model_names = self.sort_models_by_dependencies2()

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

            # Записываем кастомные типы
            if self.custom_types:
                f.write('# ' + '=' * 50 + '\n')
                f.write('# КАСТОМНЫЕ ТИПЫ\n')
                f.write('# ' + '=' * 50 + '\n\n')

                for type_name, type_info in self.custom_types.items():
                    f.write(f'# Тип: {type_name} (из {os.path.basename(type_info["file"])})\n')
                    f.write(type_info['code'])
                    f.write('\n\n')

            # Записываем модели в правильном порядке
            for model_name in sorted_model_names:
                model_data = self.models[model_name]
                f.write(f'# Модель: {model_name} (из {os.path.basename(model_data["file"])})\n')
                f.write(model_data['code'])
                f.write('\n\n')
                f.write('#' + '=' * 50 + '\n\n')

        Path(self.output_file).chmod(0o777)

    def run(self):
        """Запускает процесс сбора моделей"""
        print("Начало сбора Pydantic моделей...")
        self.collect_models()
        print(f"Найдено {len(self.models)} уникальных моделей")
        self.write_combined_file()
        print(f"Модели сохранены в файл: {self.output_file}")


def main():
    project_root = BACKEND_DIR
    output_file = BACKEND_DIR / "src" / "generated_models.py"

    collector = BaseModelCollector(project_root, output_file)
    collector.run()


if __name__ == "__main__":
    # TODO: VR-31 кодген для енамов
    main()
    subprocess.run("pydantic2ts --module src.generated_models --output /frontend/src/types/schemas.ts".split())
