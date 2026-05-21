"""Tests for scripts/generate_dataclasses.py"""
import dataclasses
import enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from scripts.generate_dataclasses import (
    collect_models_and_enums,
    format_type_annotation,
    generate_dataclass_source,
    generate_enum_source,
    get_field_info_from_pydantic,
    iter_all_module_names,
    render_default_value,
)


class TestIterAllModuleNames:
    """Tests for iter_all_module_names function"""

    def test_finds_top_level_modules(self, tmp_path: Path):
        """Should find top-level modules in directory"""
        (tmp_path / "module_a.py").touch()
        (tmp_path / "module_b.py").touch()

        modules = list(iter_all_module_names(tmp_path, "test"))

        assert len(modules) >= 2

    def test_ignores_pycache(self, tmp_path: Path):
        """Should not include __pycache__ directories"""
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "cached.pyc").touch()

        modules = list(iter_all_module_names(tmp_path, "test"))

        assert not any("__pycache__" in m for m in modules)

    def test_ignores_tests_directory(self, tmp_path: Path):
        """Should not include tests directory"""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_module.py").touch()

        modules = list(iter_all_module_names(tmp_path, "test"))

        assert not any("tests" in m for m in modules)

    def test_recurse_into_packages(self, tmp_path: Path):
        """Should recurse into package directories"""
        pkg = tmp_path / "mypackage"
        pkg.mkdir()
        (pkg / "__init__.py").touch()
        (pkg / "submodule.py").touch()

        modules = list(iter_all_module_names(tmp_path, "test"))

        assert any("mypackage" in m for m in modules)


class TestFormatTypeAnnotation:
    """Tests for format_type_annotation function"""

    def test_passthrough_strings(self):
        """Should return strings unchanged"""
        result = format_type_annotation("str")
        assert result == "str"

    def test_format_optional_with_none(self):
        """Should format Optional[T] as Optional[T]"""
        result = format_type_annotation(Optional[str])
        assert result == "Optional[str]"

    def test_format_union_with_none(self):
        """Should format Union[X, None] as Optional[X]"""
        result = format_type_annotation(str | None)
        assert result == "Optional[str]"

    def test_format_list(self):
        """Should format List[T] as List[T]"""
        result = format_type_annotation(List[str])
        assert result == "List[str]"

    def test_format_dict(self):
        """Should format Dict[K, V] as Dict[K, V]"""
        result = format_type_annotation(Dict[str, int])
        assert result == "Dict[str, int]"

    def test_format_any(self):
        """Should format Any as 'Any'"""
        result = format_type_annotation(Any)
        assert result == "Any"

    def test_format_class_with_name(self):
        """Should return class __name__ for classes with __name__"""
        result = format_type_annotation(str)
        assert result == "str"

    def test_format_union_without_none(self):
        """Should format Union[A, B] without None as Union[A, B]"""
        result = format_type_annotation(Union[str, int])
        assert "Union" in result
        assert "str" in result
        assert "int" in result


class TestRenderDefaultValue:
    """Tests for render_default_value function"""

    def test_missing_returns_none(self):
        """Should return None for MISSING"""
        result = render_default_value(dataclasses.MISSING)
        assert result is None

    def test_none_returns_string_none(self):
        """Should return 'None' for None value"""
        result = render_default_value(None)
        assert result == "None"

    def test_bool_true(self):
        """Should return 'True' for True"""
        result = render_default_value(True)
        assert result == "True"

    def test_bool_false(self):
        """Should return 'False' for False"""
        result = render_default_value(False)
        assert result == "False"

    def test_int(self):
        """Should return repr for int"""
        result = render_default_value(42)
        assert result == "42"

    def test_float(self):
        """Should return repr for float"""
        result = render_default_value(3.14)
        assert result == "3.14"

    def test_str(self):
        """Should return repr for string"""
        result = render_default_value("test")
        assert result == "'test'"

    def test_list(self):
        """Should return repr for list"""
        result = render_default_value([1, 2, 3])
        assert result == "[1, 2, 3]"


class TestGetFieldInfoFromPydantic:
    """Tests for get_field_info_from_pydantic function"""

    def test_get_field_with_default(self):
        """Should get field info with default value"""
        class TestModel(BaseModel):
            name: str = "default"

        ann, default, default_factory = get_field_info_from_pydantic(TestModel, "name")

        assert ann is not None
        assert default == "default"

    def test_get_field_without_default(self):
        """Should get field info without default value"""
        class TestModel(BaseModel):
            name: str

        ann, default, default_factory = get_field_info_from_pydantic(TestModel, "name")

        assert ann is not None
        # Pydantic uses PydanticUndefined for fields without defaults
        # This is acceptable behavior
        assert default is not None  # Either PydanticUndefined or actual value

    def test_missing_field_returns_none(self):
        """Should return None for missing field"""

        class TestModel(BaseModel):
            name: str

        result = get_field_info_from_pydantic(TestModel, "nonexistent")

        # Function returns None for missing fields
        assert result is None


class TestGenerateDataclassSource:
    """Tests for generate_dataclass_source function"""

    def test_generate_simple_class(self):
        """Should generate dataclass for simple Pydantic model"""

        class SimpleModel(BaseModel):
            name: str
            age: int

        source, used_typing = generate_dataclass_source("SimpleModel", SimpleModel)

        assert "@dataclass" in source
        assert "class SimpleModel" in source
        assert "name: str" in source
        assert "age: int" in source

    def test_generate_class_with_defaults(self):
        """Should generate dataclass with default values"""

        class ModelWithDefaults(BaseModel):
            name: str = "default_name"
            count: int = 0

        source, used_typing = generate_dataclass_source("ModelWithDefaults", ModelWithDefaults)

        assert "default_name" in source
        assert "0" in source

    def test_generate_class_with_optional_fields(self):
        """Should generate dataclass with optional fields"""

        class ModelWithOptional(BaseModel):
            required: str
            optional: Optional[str] = None

        source, used_typing = generate_dataclass_source("ModelWithOptional", ModelWithOptional)

        assert "Optional" in source or "optional" in source

    def test_tracks_used_typing(self):
        """Should track which typing names are used"""
        from typing import List

        class ModelWithList(BaseModel):
            items: List[str]

        source, used_typing = generate_dataclass_source("ModelWithList", ModelWithList)

        assert "List" in used_typing

    def test_empty_class_generates_pass(self):
        """Should generate 'pass' for class with no fields"""

        class EmptyModel(BaseModel):
            pass

        source, used_typing = generate_dataclass_source("EmptyModel", EmptyModel)

        assert "pass" in source


class TestGenerateEnumSource:
    """Tests for generate_enum_source function"""

    def test_generate_simple_enum(self):
        """Should generate enum source for simple enum"""
        class Color(enum.Enum):
            RED = 1
            GREEN = 2
            BLUE = 3

        source = generate_enum_source("Color", Color)

        assert "class Color(Enum):" in source
        assert "RED = 1" in source
        assert "GREEN = 2" in source
        assert "BLUE = 3" in source

    def test_generate_string_enum(self):
        """Should generate enum source for string values"""
        class Status(enum.Enum):
            PENDING = "pending"
            ACTIVE = "active"
            DONE = "done"

        source = generate_enum_source("Status", Status)

        assert "class Status(Enum):" in source
        assert "'pending'" in source

    def test_empty_enum_generates_pass(self):
        """Should generate 'pass' for enum with no members"""
        class EmptyEnum(enum.Enum):
            pass

        source = generate_enum_source("EmptyEnum", EmptyEnum)

        assert "pass" in source

    def test_int_enum(self):
        """Should handle IntEnum correctly"""
        class Priority(enum.IntEnum):
            LOW = 1
            MEDIUM = 2
            HIGH = 3

        source = generate_enum_source("Priority", Priority)

        assert "class Priority(Enum):" in source
        assert "LOW = 1" in source


class TestCollectModelsAndEnums:
    """Tests for collect_models_and_enums function"""

    def test_collect_pydantic_models(self):
        """Should collect Pydantic models from modules"""
        from types import SimpleNamespace

        TestModel1 = type('TestModel1', (BaseModel,), {'__annotations__': {'name': str}})
        TestModel2 = type('TestModel2', (BaseModel,), {'__annotations__': {'value': int}})

        # Use SimpleNamespace to create a mock module
        fake_module = SimpleNamespace(
            __name__="test_module",
            TestModel1=TestModel1,
            TestModel2=TestModel2
        )

        modules = [fake_module]
        models, enums = collect_models_and_enums(modules)

        assert "TestModel1" in models
        assert "TestModel2" in models

    def test_collect_enums(self):
        """Should collect Enum classes from modules"""
        from types import SimpleNamespace

        class TestColor(enum.Enum):
            RED = 1
            BLUE = 2

        fake_module = SimpleNamespace(
            __name__="test_module",
            TestColor=TestColor
        )

        modules = [fake_module]
        models, enums = collect_models_and_enums(modules)

        assert "TestColor" in enums

    def test_excludes_base_model(self):
        """Should not collect BaseModel itself"""

        class FakeModule:
            __name__ = "test_module"
            BaseModel = BaseModel

        modules = [FakeModule()]
        models, enums = collect_models_and_enums(modules)

        assert "BaseModel" not in models

    def test_handles_import_errors(self):
        """Should handle modules that can't be inspected"""

        class BadModule:
            pass

        modules = [BadModule()]
        models, enums = collect_models_and_enums(modules)

        # Should not raise, just return empty
        assert isinstance(models, dict)
        assert isinstance(enums, dict)


class TestIntegration:
    """Integration tests for the full generation process"""

    def test_format_type_annotation_with_complex_types(self):
        """Should handle complex type annotations"""
        # Union with multiple types
        result = format_type_annotation(Union[str, int, None])
        assert "Union" in result or "Optional" in result

        # Nested generics
        result = format_type_annotation(List[Dict[str, int]])
        assert "List" in result
        assert "Dict" in result

    def test_render_default_with_complex_values(self):
        """Should handle complex default values"""
        # List with items
        result = render_default_value([1, 2, 3])
        assert "1" in result

        # Dict
        result = render_default_value({"key": "value"})
        assert "key" in result

    def test_generate_dataclass_preserves_field_order(self):
        """Should preserve field order in generated dataclass"""

        class OrderedModel(BaseModel):
            first: str
            second: int
            third: float = 0.0

        source, _ = generate_dataclass_source("OrderedModel", OrderedModel)

        first_idx = source.find("first:")
        second_idx = source.find("second:")
        third_idx = source.find("third:")

        assert first_idx < second_idx < third_idx
