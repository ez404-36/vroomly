import ast
import datetime
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from common.utils.file_inspectors import get_all_python_files
from core.constants import BACKEND_DIR

# Путь к фронтенду для генерации TypeScript файлов
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"


class EnumCollector:
    """Собирает Enum из Python кода"""

    def __init__(self, project_root: str | Path, use_erasable_syntax: bool = True):
        self.project_root = Path(project_root)
        self.enums: Dict[str, Dict] = {}  # name -> {python_code, file}
        self.use_erasable_syntax = use_erasable_syntax

    def get_all_python_files(self) -> List[Path]:
        """Получает все Python файлы в проекте"""
        return get_all_python_files(self.project_root)

    def extract_enum_class(self, node: ast.ClassDef, content: str) -> Dict | None:
        """Извлекает информацию об Enum классе"""
        # Проверяем, что класс наследуется от Enum (включая IntEnum, IntFlag)
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in ('Enum', 'IntEnum', 'IntFlag'):
                start_line = node.lineno - 1
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                lines = content.split('\n')
                enum_code = '\n'.join(lines[start_line:end_line])
                return {
                    'name': node.name,
                    'code': enum_code,
                    'file': '',
                }
            # Проверяем множественное наследование (например ChoicesMixin, IntEnum)
            if isinstance(base, ast.Tuple):
                for elt in base.elts:
                    if isinstance(elt, ast.Name) and elt.id in ('Enum', 'IntEnum', 'IntFlag'):
                        start_line = node.lineno - 1
                        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
                        lines = content.split('\n')
                        enum_code = '\n'.join(lines[start_line:end_line])
                        return {
                            'name': node.name,
                            'code': enum_code,
                            'file': '',
                        }
        return None

    def extract_enums_from_file(self, file_path: Path) -> List[Dict]:
        """Извлекает все Enum классы из файла"""
        enums = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    enum_info = self.extract_enum_class(node, content)
                    if enum_info:
                        enum_info['file'] = str(file_path)
                        enums.append(enum_info)

        except Exception as e:
            print(f"Ошибка при извлечении Enum из {file_path}: {e}")

        return enums

    def collect_all_enums(self):
        """Собирает все Enum из проекта"""
        python_files = self.get_all_python_files()
        print(f"Найдено {len(python_files)} Python файлов для поиска Enum")

        for file_path in python_files:
            enums = self.extract_enums_from_file(file_path)
            for enum_info in enums:
                if enum_info['name'] not in self.enums:
                    self.enums[enum_info['name']] = enum_info
                    print(f"Найден Enum: {enum_info['name']} в {file_path}")

    def _value_to_ts(self, value: Any) -> str:
        """Конвертирует Python значение в TypeScript"""
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, int):
            return str(value)
        if isinstance(value, str):
            # Экранируем спецсимволы и кавычки
            escaped = value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
            return f"'{escaped}'"
        return repr(value)

    def _to_camel_case(self, name: str) -> str:
        """Конвертирует имя из UPPER_SNAKE_CASE в camelCase"""
        parts = name.split('_')
        if len(parts) == 1:
            return name.lower()
        return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])

    def _to_snake_case(self, name: str) -> str:
        """Конвертирует имя из PascalCase или camelCase в snake_case"""
        # Вставляем _ перед каждой заглавной буквой и переводим в нижний регистр
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def generate_ts_enum(  # noqa: PLR0912, PLR0915
        self, enum_info: Dict, use_erasable_syntax: bool | None = None
    ) -> str | None:
        """Генерирует TypeScript enum из Python Enum"""
        name = enum_info['name']
        python_code = enum_info['code']

        # Используем переданный параметр или значение из экземпляра
        if use_erasable_syntax is None:
            use_erasable_syntax = self.use_erasable_syntax

        # Парсим через AST для точного извлечения значений
        member_data: List[Tuple[str, str]] = []  # (camelCase_name, value_str)
        seen_names: set[str] = set()

        try:
            tree = ast.parse(python_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == name:
                    for item in node.body:
                        member_name = None
                        value_str = ''

                        if isinstance(item, ast.Assign):
                            # Enum members use simple assignment
                            targets = getattr(item, 'targets', [item.target if hasattr(item, 'target') else None])
                            if not targets:
                                continue
                            target = targets[0]
                            if isinstance(target, ast.Name):
                                member_name = target.id
                                if item.value:
                                    value_str = self._get_value_str(item.value)
                            # Multi-target assignment like: A = B = value
                            elif isinstance(target, ast.Tuple):
                                for t in target.elts:
                                    if isinstance(t, ast.Name):
                                        member_name = t.id
                                        if item.value:
                                            value_str = self._get_value_str(item.value)
                                        break

                        elif isinstance(item, ast.AnnAssign):
                            # Annotated assignment (less common in enums)
                            if isinstance(item.target, ast.Name):
                                member_name = item.target.id
                                if item.value:
                                    value_str = self._get_value_str(item.value)

                        if not member_name:
                            continue

                        # Пропускаем служебные поля
                        if member_name in ('name', 'value', '_name_', '_value_', '__labels__'):
                            continue
                        if member_name.startswith('_'):
                            continue

                        # Конвертируем имя в camelCase
                        ts_member_name = self._to_camel_case(member_name)

                        # Избегаем дубликатов
                        if ts_member_name in seen_names:
                            continue
                        seen_names.add(ts_member_name)

                        # Сохраняем данные члена enum
                        member_data.append((ts_member_name, value_str))

        except Exception as e:
            print(f"Ошибка при генерации TypeScript enum {name}: {e}")
            return None

        if not member_data:
            return None

        # Формируем вывод в зависимости от режима
        if use_erasable_syntax:
            # String literal union: export type Status = 'pending' | 'active';
            values = []
            for ts_name, value_str in member_data:
                if value_str.isdigit() or value_str.replace('.', '').replace('-', '').isdigit():
                    values.append(f"'{ts_name}'")
                else:
                    values.append(f"'{value_str}'")
            return f"export type {name} = {' | '.join(values)};"
        else:
            # Classic enum: export enum Status { pending = 1, active = 2 }
            members = []
            for ts_name, value_str in member_data:
                if value_str.isdigit():
                    members.append(f"    {ts_name} = {value_str},")
                elif value_str.replace('.', '').replace('-', '').isdigit():
                    members.append(f"    {ts_name} = {value_str},")
                else:
                    members.append(f"    {ts_name} = '{value_str}',")
            return f"export enum {name} {{\n" + '\n'.join(members) + "\n}"

    def _get_value_str(self, value_node: ast.AST) -> str:
        """Извлекает строковое представление значения из AST узла"""
        if isinstance(value_node, ast.Constant):
            return str(value_node.value)
        if isinstance(value_node, ast.BinOp):
            # Для IntFlag с битовыми операциями
            result = self._eval_binop(value_node)
            return str(result) if result else '0'
        if isinstance(value_node, ast.Name):
            return value_node.id
        if isinstance(value_node, ast.Attribute):
            # Для доступа к атрибутам модуля
            if isinstance(value_node.value, ast.Name):
                return f"{value_node.value.id}.{value_node.attr}"
        return ''

    def _eval_binop(self, node: ast.BinOp) -> str:
        """Вычисляет бинарное выражение (например, 1 | 16) для IntFlag"""
        try:
            def get_num(n: ast.AST) -> int | None:
                if isinstance(n, ast.Constant) and isinstance(n.value, (int, str)):
                    return int(n.value)
                if isinstance(n, ast.BinOp):
                    left = get_num(n.left)
                    right = get_num(n.right)
                    if left is not None and right is not None:
                        if isinstance(n.op, ast.BitOr):
                            return left | right
                        if isinstance(n.op, ast.BitAnd):
                            return left & right
                return None

            result = get_num(node)
            return str(result) if result is not None else '0'
        except Exception:
            return '0'

    def run(self):
        """Запускает процесс сбора Enum"""
        print("Начало сбора Enum...")
        self.collect_all_enums()
        print(f"Найдено {len(self.enums)} Enum")

    def write_ts_file(self) -> None:
        """Генерирует TypeScript файл с Enum"""
        if not self.enums:
            print("Нет Enum для генерации в TypeScript")
            return

        output_dir = FRONTEND_DIR / "src" / "types"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "enums.ts"

        format_note = "string literal union" if self.use_erasable_syntax else "classic enum"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("// Автоматически сгенерированный файл с Enum\n")
            f.write(f"// Дата генерации: {datetime.datetime.now()}\n")
            f.write(f"// Формат: {format_note}\n")
            f.write(f"// Количество: {len(self.enums)}\n\n")

            for enum_name in sorted(self.enums.keys()):
                enum_info = self.enums[enum_name]
                ts_code = self.generate_ts_enum(enum_info)
                if ts_code:
                    f.write(f"// {enum_name} (из {os.path.basename(enum_info['file'])})\n")
                    f.write(f"{ts_code}\n\n")

        print(f"TypeScript Enum файл сохранен: {output_file}")

    def generate_python_enum(self, enum_info: Dict) -> str | None:  # noqa: PLR0912
        """Генерирует Python Enum код для включения в generated_models.py"""
        name = enum_info['name']
        python_code = enum_info['code']

        # Парсим через AST для точного извлечения значений
        members = []

        try:
            tree = ast.parse(python_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == name:
                    for item in node.body:
                        member_name = None
                        value_str = ''

                        if isinstance(item, ast.Assign):
                            targets = getattr(item, 'targets', [item.target if hasattr(item, 'target') else None])
                            if not targets:
                                continue
                            target = targets[0]
                            if isinstance(target, ast.Name):
                                member_name = target.id
                                if item.value:
                                    value_str = self._get_value_str(item.value)
                            elif isinstance(target, ast.Tuple):
                                for t in target.elts:
                                    if isinstance(t, ast.Name):
                                        member_name = t.id
                                        if item.value:
                                            value_str = self._get_value_str(item.value)
                                        break

                        elif isinstance(item, ast.AnnAssign):
                            if isinstance(item.target, ast.Name):
                                member_name = item.target.id
                                if item.value:
                                    value_str = self._get_value_str(item.value)

                        if not member_name:
                            continue

                        if member_name in ('name', 'value', '_name_', '_value_', '__labels__'):
                            continue
                        if member_name.startswith('_'):
                            continue

                        ts_member_name = member_name

                        if value_str.isdigit():
                            members.append(f"    {ts_member_name} = {value_str},")
                        elif value_str.replace('.', '').replace('-', '').isdigit():
                            members.append(f"    {ts_member_name} = {value_str},")
                        else:
                            members.append(f"    {ts_member_name} = '{value_str}',")

        except Exception as e:
            print(f"Ошибка при генерации Python enum {name}: {e}")
            return None

        if not members:
            return None

        return f"class {name}(Enum):\n" + '\n'.join(members)


class LiteralCollector:
    """Собирает Literal type aliases из Python кода"""

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.literals: Dict[str, Dict] = {}  # name -> {values, file}

    def get_all_python_files(self) -> List[Path]:
        """Получает все Python файлы в проекте"""
        return get_all_python_files(self.project_root)

    def _extract_literal_values(self, node: ast.Subscript) -> List[str]:
        """Извлекает значения из Literal[...]"""
        values = []

        # Subscript для Literal[..., ...] - slice содержит Tuple
        slice_node = node.slice
        if isinstance(slice_node, ast.Tuple):
            for elt in slice_node.elts:
                val = self._extract_single_value(elt)
                if val is not None:
                    values.append(val)
        else:
            # Одиночное значение
            val = self._extract_single_value(slice_node)
            if val is not None:
                values.append(val)

        return values

    def _extract_single_value(self, node: ast.AST) -> str | None:  # noqa: PLR0911
        """Извлекает одиночное значение из AST узла"""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f"'{node.value}'"
            elif isinstance(node.value, (int, float, bool)):
                return str(node.value).lower() if isinstance(node.value, bool) else str(node.value)
            elif node.value is None:
                return 'null'
        elif isinstance(node, ast.Str):  # noqa: PLR0913, deprecated  # Python < 3.8
            return f"'{node.s}'"
        elif isinstance(node, ast.Num):  # noqa: PLR0913, deprecated  # Python < 3.8
            return str(node.n)
        elif isinstance(node, ast.NameConstant):  # noqa: PLR0913, deprecated  # Python < 3.8
            return str(node.value).lower()
        elif isinstance(node, ast.Name):
            # Константы типа True, False, None
            if node.id in ('True', 'False'):
                return node.id.lower()
            elif node.id == 'None':
                return 'null'
        return None

    def extract_literal_alias(self, node: ast.TypeAlias) -> Dict | None:
        """Извлекает Literal type alias"""
        # Проверяем, что это Literal[...]
        if isinstance(node.value, ast.Subscript):
            subscript = node.value
            # Проверяем, что это Literal
            if isinstance(subscript.value, ast.Name) and subscript.value.id == 'Literal':
                values = self._extract_literal_values(subscript)
                if values:
                    return {
                        'name': node.name.id,
                        'values': values,
                        'file': '',
                    }
        return None

    def extract_literal_alias_from_assign(self, node: ast.Assign, content: str) -> Dict | None:
        """Извлекает Literal type alias из старого стиля присваивания"""
        if not node.targets:
            return None

        target = node.targets[0]
        if not isinstance(target, ast.Name):
            return None

        name = target.id

        # Проверяем, что значение - это Subscript с Literal
        if isinstance(node.value, ast.Subscript):
            subscript = node.value
            # Проверяем, что база - Literal
            if isinstance(subscript.value, ast.Name) and subscript.value.id == 'Literal':
                values = self._extract_literal_values(subscript)
                if values:
                    return {
                        'name': name,
                        'values': values,
                        'file': '',
                    }
        return None

    def extract_literals_from_file(self, file_path: Path) -> List[Dict]:
        """Извлекает все Literal type aliases из файла"""
        literals = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Python 3.12+ style: type X = Literal[...]
                if isinstance(node, ast.TypeAlias):
                    literal_info = self.extract_literal_alias(node)
                    if literal_info:
                        literal_info['file'] = str(file_path)
                        literals.append(literal_info)

                # Старый стиль: X = Literal[...]
                elif isinstance(node, ast.Assign):
                    literal_info = self.extract_literal_alias_from_assign(node, content)
                    if literal_info:
                        literal_info['file'] = str(file_path)
                        literals.append(literal_info)

        except Exception as e:
            print(f"Ошибка при извлечении Literal из {file_path}: {e}")

        return literals

    def collect_all_literals(self):
        """Собирает все Literal type aliases из проекта"""
        python_files = self.get_all_python_files()
        print(f"Найдено {len(python_files)} Python файлов для поиска Literal")

        for file_path in python_files:
            literals = self.extract_literals_from_file(file_path)
            for literal_info in literals:
                if literal_info['name'] not in self.literals:
                    self.literals[literal_info['name']] = literal_info
                    print(f"Найден Literal: {literal_info['name']} в {file_path}")

    def generate_ts_literal(self, literal_info: Dict) -> str | None:
        """Генерирует TypeScript type alias из Literal"""
        name = literal_info['name']
        values = literal_info['values']

        if not values:
            return None

        # Для одиночного значения - простой type
        if len(values) == 1:
            return f"export type {name} = {values[0]};"

        # Для нескольких значений - объединение
        return f"export type {name} = {' | '.join(values)};"

    def run(self):
        """Запускает процесс сбора Literal"""
        print("Начало сбора Literal...")
        self.collect_all_literals()
        print(f"Найдено {len(self.literals)} Literal")

    def generate_python_literal(self, literal_info: Dict) -> str | None:
        """Генерирует Python Literal type alias код"""
        name = literal_info['name']
        values = literal_info['values']

        if not values:
            return None

        # Преобразуем TypeScript значения обратно в Python формат
        python_values = []
        for val in values:
            if val.startswith("'") and val.endswith("'"):
                python_values.append(f'"{val[1:-1]}"')
            elif val in ('true', 'false'):
                python_values.append(val.capitalize())
            elif val == 'null':
                python_values.append('None')
            else:
                python_values.append(val)

        if len(python_values) == 1:
            return f"{name}: Literal = {python_values[0]}"
        return f"{name}: Literal = ({', '.join(python_values)})"

    def write_ts_file(self) -> None:
        """Генерирует TypeScript файл с Literal типами"""
        if not self.literals:
            print("Нет Literal для генерации в TypeScript")
            return

        output_dir = FRONTEND_DIR / "src" / "types"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "literals.ts"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("// Автоматически сгенерированный файл с Literal типами\n")
            f.write(f"// Дата генерации: {datetime.datetime.now()}\n")
            f.write(f"// Количество: {len(self.literals)}\n\n")

            for literal_name in sorted(self.literals.keys()):
                literal_info = self.literals[literal_name]
                ts_code = self.generate_ts_literal(literal_info)
                if ts_code:
                    f.write(f"// {literal_name} (из {os.path.basename(literal_info['file'])})\n")
                    f.write(f"{ts_code}\n\n")

        print(f"TypeScript Literal файл сохранен: {output_file}")


class BaseModelCollector:
    def __init__(
        self,
        project_root: str | Path,
        output_file: str | Path,
        enums: Dict | None = None,
        literals: Dict | None = None,
    ):
        self.project_root = Path(project_root)
        self.output_file = Path(output_file)
        self.models: Dict[str, Dict] = {}  # name -> {code, file, dependencies}
        self.custom_types: Dict[str, Dict] = {}  # name -> {code, file, dependencies}
        self.imports: Set[str] = set()
        self.processed_files: Set[str] = set()
        self.base_model_classes: Set[str] = {'BaseModel', 'APIModel'}
        self.enums = enums or {}
        self.literals = literals or {}

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
                target = getattr(child, 'target', None)
                if target is not None and hasattr(target, 'id'):
                    print(f"[warning] Необработанный тип в {class_node.name}: {target.id}")

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

    def write_combined_file(self):  # noqa: PLR0915
        """Записывает все модели в один файл"""
        # Фильтруем импорты, оставляя только нужные
        filtered_imports = set()
        for imp in self.imports:
            # Оставляем импорты pydantic, typing и стандартные модули
            if any(keyword in imp for keyword in ['pydantic', 'typing', 'datetime', 'decimal', 'uuid', 'enum']):
                filtered_imports.add(imp)

        # Убираем импорты типов, которые теперь определены в этом файле
        enum_names = set(self.enums.keys())
        literals_names = set(self.literals.keys())

        def should_keep_import(imp: str) -> bool:
            """Проверяет, нужно ли оставить импорт"""
            # Убираем импорты модулей apps.* и core.* - они не нужны для pydantic2ts
            if 'from apps.' in imp or 'from core.' in imp:
                return False
            # Убираем импорты типов, которые теперь определены в файле
            for name in enum_names | literals_names:
                if f'import {name}' in imp or f'import .{name}' in imp or f', {name}' in imp:
                    return False
            return True

        filtered_imports = {imp for imp in filtered_imports if should_keep_import(imp)}

        # Добавляем обязательный импорт BaseModel
        filtered_imports.add("from pydantic import BaseModel")
        filtered_imports.add("from fastapi_utils.api_model import APIModel")

        # Добавляем импорт для Enum
        if self.enums:
            filtered_imports.add("from enum import Enum")

        # Добавляем импорт для TypeAlias
        if self.literals:
            filtered_imports.add("from typing import TypeAlias")

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
            f.write(f'Найдено {len(self.models)} моделей, {len(self.enums)} Enum, {len(self.literals)} Literal\n')
            f.write('Сгенерировано автоматически\n')
            f.write('"""\n\n')

            # Записываем импорты
            for imp in sorted(filtered_imports):
                f.write(f'{imp}\n')

            f.write('\n\n')

            # Записываем Enum
            if self.enums:
                f.write('# ' + '=' * 50 + '\n')
                f.write('# ENUM\n')
                f.write('# ' + '=' * 50 + '\n\n')

                for enum_name in sorted(self.enums.keys()):
                    enum_info = self.enums[enum_name]
                    f.write(f'# Enum: {enum_name} (из {os.path.basename(enum_info["file"])})\n')
                    # Используем enum_code напрямую, так как это уже Python код
                    # Убираем docstring для pydantic2ts
                    enum_code = self._clean_enum_for_pydantic2ts(enum_info['code'], enum_name)
                    f.write(enum_code)
                    f.write('\n\n')

            # Записываем Literal
            if self.literals:
                f.write('# ' + '=' * 50 + '\n')
                f.write('# LITERAL TYPES\n')
                f.write('# ' + '=' * 50 + '\n\n')

                for literal_name in sorted(self.literals.keys()):
                    literal_info = self.literals[literal_name]
                    f.write(f'# Literal: {literal_name} (из {os.path.basename(literal_info["file"])})\n')
                    literal_code = self._generate_literal_code(literal_info)
                    f.write(literal_code)
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

    def _clean_enum_for_pydantic2ts(self, code: str, enum_name: str) -> str:  # noqa: PLR0912
        """Извлекает только значения Enum из кода"""
        lines = code.split('\n')
        result_lines = []
        in_docstring = False

        for line in lines:
            stripped = line.strip()

            # Пропускаем пустые строки в начале
            if not result_lines and not stripped:
                continue

            # Пропускаем строку с объявлением класса
            if stripped.startswith(f'class {enum_name}'):
                result_lines.append(f'class {enum_name}(Enum):')
                continue

            # Обработка docstring
            has_docstring_marker = '"""' in stripped or "'''" in stripped

            if has_docstring_marker:
                # Проверяем, открывает или закрывает ли """ docstring
                if in_docstring:
                    # Мы внутри docstring - закрываем его
                    in_docstring = False
                else:
                    # Мы снаружи - открываем docstring
                    # Проверяем, однострочный ли docstring
                    # Однострочный: """content""" (без закрывающего открывающего)
                    # Ищем позиции """
                    marker = '"""' if '"""' in stripped else "'''"
                    first_pos = stripped.find(marker)
                    last_pos = stripped.rfind(marker)

                    if first_pos != last_pos:
                        # Есть и открытие, и закрытие - однострочный docstring
                        # Ничего не меняем, пропускаем строку
                        pass
                    else:
                        # Только открытие - начинаем многострочный docstring
                        in_docstring = True

                # В любом случае пропускаем эту строку
                continue

            if in_docstring:
                # Внутри docstring - пропускаем
                continue

            # Пропускаем комментарии
            if stripped.startswith('#'):
                continue

            # Пропускаем __labels__ и другие служебные атрибуты
            if stripped.startswith('__'):
                continue

            # Добавляем только строки с присваиванием значений
            if '=' in stripped and not stripped.startswith('class '):
                # Убираем комментарии в конце строки
                clean_line = line.split('#')[0].rstrip()
                if clean_line.strip():
                    result_lines.append(clean_line)

        # Если класс пустой, добавляем pass
        if len(result_lines) == 1:
            result_lines.append('    pass')

        return '\n'.join(result_lines)

    def _generate_literal_code(self, literal_info: Dict) -> str:
        """Генерирует Python код для Literal type alias"""
        name = literal_info['name']
        values = literal_info['values']

        # Преобразуем TypeScript значения в Python формат
        python_values = []
        for val in values:
            if val.startswith("'") and val.endswith("'"):
                python_values.append(f'"{val[1:-1]}"')
            elif val in ('true', 'false'):
                python_values.append(val.capitalize())
            elif val == 'null':
                python_values.append('None')
            else:
                python_values.append(val)

        inner = ', '.join(python_values)
        return f"{name}: TypeAlias = Literal[{inner}]"

    def run(self):
        """Запускает процесс сбора моделей"""
        print("Начало сбора Pydantic моделей...")
        self.collect_models()
        print(f"Найдено {len(self.models)} уникальных моделей")
        self.write_combined_file()
        print(f"Модели сохранены в файл: {self.output_file}")


def main(enums: Dict | None = None, literals: Dict | None = None) -> None:
    """Главная функция для запуска сбора моделей."""
    project_root = BACKEND_DIR
    output_file = BACKEND_DIR / "src" / "generated_models.py"

    collector = BaseModelCollector(project_root, output_file, enums=enums, literals=literals)
    collector.run()


if __name__ == "__main__":
    # Собираем Enum
    enum_collector = EnumCollector(BACKEND_DIR)
    enum_collector.run()

    # Собираем Literal
    literal_collector = LiteralCollector(BACKEND_DIR)
    literal_collector.run()

    # Собираем все в generated_models.py
    main(enums=enum_collector.enums, literals=literal_collector.literals)

    # Генерируем TypeScript файлы для Enum и Literal
    enum_collector.write_ts_file()
    literal_collector.write_ts_file()

    # Генерируем TypeScript модели через pydantic2ts
    subprocess.run("pydantic2ts --module src.generated_models --output /frontend/src/types/schemas.ts".split())
