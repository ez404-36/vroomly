#!/usr/bin/env python3
"""
generate_dataclasses.py

Сканирует проект на предмет pydantic.BaseModel и enum.Enum,
и записывает их в один файл backend/src/dataclasses.py
в виде:
 - dataclasses (@dataclass) для BaseModel (с полными аннотациями и дефолтами)
 - enum (копируются как есть)

Классы в выходном файле отсортированы в алфавитном порядке.
Работает с Pydantic v2.
"""
import builtins
import dataclasses
import enum
import importlib
import inspect
import pkgutil
import reprlib
import sys
import types
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Set,
    Tuple,
    Union,
)

from fastapi_utils.api_model import APIModel
from pydantic import BaseModel

# Настройки
BACKEND_DIR = Path(__file__).parent.parent
OUTPUT_FILE = BACKEND_DIR / "src" / "generated_dataclasses.py"

# Safety repr limiter for large defaults
_repr = reprlib.Repr()
_repr.maxother = 200


def iter_all_module_names(start_path: Path, package_name: str):
    for finder, name, ispkg in pkgutil.iter_modules([str(start_path)]):
        full = f"{package_name}.{name}"
        yield full
        if ispkg and name not in {"tests", "__pycache__", ".venv"}:
            subpath = start_path / name
            yield from iter_all_module_names(subpath, full)


def import_all_modules_from_path(path: Path):
    """
    Импортирует рекурсивно модули, возвращает set импортированных объектов модулей.
    Игнорирует ошибки импорта (логирует в stderr).
    """
    modules = []

    for child_name in ("common", "apps"):
        child_path = path / child_name
        for modname in iter_all_module_names(child_path, child_path.name):
            try:
                module = importlib.import_module(modname)
                modules.append(module)
            except Exception as e:
                # пропускаем модули, которые падают при импорте
                print(f"[import warn] cannot import {modname}: {e}", file=sys.stderr)
    return modules


def collect_models_and_enums(modules):
    """
    Возвращает две структуры:
      models_map: {ModelName: ModelClass}
      enums_map: {EnumName: EnumClass}
    по всем импортированным модулям.
    """
    models = {}
    enums_map = {}

    for module in modules:
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ in (builtins,):
                continue

            # Enums
            if inspect.isclass(obj) and issubclass(obj, enum.Enum) and obj is not enum.Enum:
                if name not in enums_map:
                    enums_map[name] = obj
                continue

            # Pydantic models
            if inspect.isclass(obj):
                try:
                    if issubclass(obj, BaseModel) and obj is not BaseModel and obj is not APIModel:
                        if name not in models:
                            models[name] = obj
                except TypeError:
                    continue

    return models, enums_map


def format_type_annotation(tp) -> str:
    """
    Преобразует объект аннотации (typing или класс) в строковое представление,
    пригодное для dataclass с from __future__ import annotations.
    Убирает полные пути у моделей, конвертирует UnionType[X, NoneType] -> Optional[X]
    """

    if isinstance(tp, str):
        return tp

    try:
        if isinstance(tp, types.UnionType):
            args = getattr(tp, "__args__", ())
            if len(args) == 2 and type(None) in args:
                other = args[0] if args[1] is type(None) else args[1]
                return f"Optional[{format_type_annotation(other)}]"
            else:
                inner = ", ".join(format_type_annotation(a) for a in args)
                return f"Union[{inner}]"
    except Exception as e:
        print(f"[error] {e}")
        pass

    origin = getattr(tp, "__origin__", None) or getattr(tp, "__orig_class__", None)
    args = getattr(tp, "__args__", ())

    # typing constructs
    if origin is Union:
        if len(args) == 2 and type(None) in args:
            other = args[0] if args[1] is type(None) else args[1]
            return f"Optional[{format_type_annotation(other)}]"
        inner = ", ".join(format_type_annotation(a) for a in args)
        return f"Union[{inner}]"

    if origin in (list, List):
        inner = format_type_annotation(args[0]) if args else "Any"
        return f"List[{inner}]"

    if origin in (dict, Dict):
        k = format_type_annotation(args[0]) if args else "Any"
        v = format_type_annotation(args[1]) if len(args) > 1 else "Any"
        return f"Dict[{k}, {v}]"

    if hasattr(tp, "__name__"):
        return tp.__name__

    if tp is Any:
        return "Any"

    return str(tp)


def render_default_value(value):
    """
    Превращает default-значение в корректный кодовый литерал.
    Если значение не серилизуется просто - используем repr с ограничением.
    """
    if value is dataclasses.MISSING:
        return None
    if value is None:
        return "None"
    if isinstance(value, (bool, int, float)):
        return repr(value)
    if isinstance(value, str):
        return repr(value)
    # lists, dicts, tuples of primitive types -> use repr
    try:
        return _repr.repr(value)
    except Exception:
        return repr(value)


def get_field_info_from_pydantic(model_cls, field_name):
    """
    Возвращает структуру (annotation, default, default_factory) для поля,
    учитывая совместимость pydantic v1 и v2.
    """
    try:
        model_fields = getattr(model_cls, "model_fields", None)
        if model_fields is not None and field_name in model_fields:
            info = model_fields[field_name]
            # info может быть FieldInfo-like dict or pydantic.fields.ModelFieldInfo
            ann = info.get("annotation") if isinstance(info, dict) else getattr(info, "annotation", None)
            default = info.get("default", dataclasses.MISSING) if isinstance(info, dict) else getattr(info, "default", dataclasses.MISSING)
            default_factory = info.get("default_factory", None) if isinstance(info, dict) else getattr(info, "default_factory", None)
            return ann, default, default_factory

    except Exception as e:
        print(f"[error] {e}")


def generate_dataclass_source(name: str, model_cls) -> Tuple[str, Set[str]]:
    """
    Генерирует источник кода dataclass для одной pydantic-модели.
    Возвращает (source_str, set_of_typing_names_used).
    """
    lines = []
    used_typing: Set[str] = set()

    lines.append("@dataclass")
    lines.append(f"class {name}:")

    annotations = getattr(model_cls, "__annotations__", {}) or {}
    try:
        mf = getattr(model_cls, "model_fields", None)
        if mf:
            field_names = list(mf.keys())
        else:
            field_names = list(annotations.keys())
    except Exception:
        field_names = list(annotations.keys())

    if not field_names:
        lines.append("    pass")
        return "\n".join(lines), used_typing

    required_fields = []
    optional_fields = []

    for fname in field_names:
        ann, default, default_factory = get_field_info_from_pydantic(model_cls, fname)
        ann_str = format_type_annotation(ann) if ann is not None else "Any"

        # track which typing names used for imports
        for token in ("Optional", "Union", "List", "Dict", "Tuple", "Literal", "Any"):
            if token in ann_str:
                used_typing.add(token)
        # basic Any
        if ann_str == "Any":
            used_typing.add("Any")

        if default is dataclasses.MISSING or (str(default) == "PydanticUndefined"):
            default_code = None
            required_fields.append((fname, ann_str, default_code))
        else:
            if default_factory:
                default_code = f"field(default_factory={default_factory.__name__})"
            else:
                default_code = render_default_value(default)
            optional_fields.append((fname, ann_str, default_code))

    ordered_fields = required_fields + optional_fields
    for fname, ann_str, default_code in ordered_fields:
        if default_code is None:
            lines.append(f"    {fname}: {ann_str}")
        else:
            lines.append(f"    {fname}: {ann_str} = {default_code}")

    return "\n".join(lines), used_typing


def generate_enum_source(name: str, enum_cls) -> str:
    """
    Возвращает строку с источником Enum-класса.
    """
    lines = [f"class {name}(Enum):"]
    members = []
    for member in enum_cls:
        # use member.name and member.value
        members.append(f"    {member.name} = {repr(member.value)}")
    if not members:
        lines.append("    pass")
    else:
        lines.extend(members)
    return "\n".join(lines)


def main():
    """
    Сканирование всех backend-модулей и генерация dataclasses из моделей SQLAlchemy и Enum
    """

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"[info] scanning modules from {BACKEND_DIR} ...")
    modules = import_all_modules_from_path(BACKEND_DIR)
    models_map, enums_map = collect_models_and_enums(modules)

    if not models_map and not enums_map:
        print("[warn] no pydantic models or enums found.")
        return

    print(f"[info] found {len(models_map)} models and {len(enums_map)} enums")

    entries = {}  # name -> (kind, source, used_typing_set)
    for name, cls in models_map.items():
        try:
            src, used = generate_dataclass_source(name, cls)
            entries[name] = ("model", src, used)
        except Exception as e:
            print(f"[error] failed to generate dataclass for {name}: {e}", file=sys.stderr)

    for name, cls in enums_map.items():
        try:
            src = generate_enum_source(name, cls)
            entries[name] = ("enum", src, {"Enum"})
        except Exception as e:
            print(f"[error] failed to generate enum {name}: {e}", file=sys.stderr)

    # Sort entries alphabetically by name
    sorted_names = sorted(entries.keys(), key=lambda s: s.lower())

    # Determine necessary imports based on used typing tokens across all entries
    typing_needed: Set[str] = set()
    need_field = False
    need_enum = False
    for _, (kind, src, used) in [(n, entries[n]) for n in sorted_names]:
        for token in used:
            if token == "field":
                need_field = True
            elif token == "Enum":
                need_enum = True
            else:
                typing_needed.add(token)

    # Build header
    header_lines = [
        "from __future__ import annotations",
        "",
        "from datetime import date, datetime",
        "from uuid import UUID",
        "from dataclasses import dataclass" + (", field" if need_field else ""),
    ]
    if need_enum:
        header_lines.append("from enum import Enum, IntEnum, IntFlag")
    if typing_needed:
        # ensure consistent ordering
        tylist = ", ".join(sorted(typing_needed))
        header_lines.append(f"from typing import {tylist}")
    header_lines.append("")
    header_lines.append("")
    header = "\n".join(header_lines)

    # Build body
    body_lines = []
    for name in sorted_names:
        kind, src, used = entries[name]
        body_lines.append(src)
        body_lines.append("")  # blank line between classes

    final_source = header + "\n".join(body_lines)

    # Write to file
    OUTPUT_FILE.write_text(final_source, encoding="utf-8")
    print(f"[ok] wrote dataclasses to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
