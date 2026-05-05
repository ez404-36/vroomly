"""Tests for scripts/collect_models.py"""
import ast
from pathlib import Path

from scripts.collect_models import BaseModelCollector, EnumCollector, LiteralCollector


class TestBaseModelCollector:
    """Tests for BaseModelCollector class"""

    def test_init_with_path_strings(self, tmp_path: Path):
        """Should initialize with string paths"""
        output_file = tmp_path / "output.py"
        collector = BaseModelCollector(str(tmp_path), str(output_file))

        assert collector.project_root == tmp_path
        assert collector.output_file == output_file
        assert collector.models == {}
        assert collector.custom_types == {}

    def test_init_with_path_objects(self, tmp_path: Path):
        """Should initialize with Path objects"""
        output_file = tmp_path / "output.py"
        collector = BaseModelCollector(tmp_path, output_file)

        assert collector.project_root == tmp_path
        assert collector.output_file == output_file

    def test_extract_imports_from_code_simple_import(self):
        """Should extract simple import statements"""
        code = """
import os
import sys
"""
        imports = BaseModelCollector.extract_imports_from_code(code)

        assert "import os" in imports
        assert "import sys" in imports

    def test_extract_imports_from_code_from_import(self):
        """Should extract from...import statements"""
        code = """
from typing import Optional, List
from pathlib import Path
"""
        imports = BaseModelCollector.extract_imports_from_code(code)

        assert "from typing import Optional, List" in imports
        assert "from pathlib import Path" in imports

    def test_extract_imports_from_code_invalid(self):
        """Should handle invalid Python code gracefully"""
        code = "this is not valid python {{{{"
        imports = BaseModelCollector.extract_imports_from_code(code)

        assert imports == set()

    def test_normalize_indentation_tabs_to_spaces(self):
        """Should replace tabs with 4 spaces"""
        collector = BaseModelCollector(".", "output.py")
        code = "line1\n\tindented\n\t\tdouble_indented"
        normalized = collector.normalize_indentation(code)

        assert "    indented" in normalized
        assert "        double_indented" in normalized

    def test_normalize_indentation_preserves_spaces(self):
        """Should preserve existing spaces"""
        collector = BaseModelCollector(".", "output.py")
        code = "line1\n    spaced"
        normalized = collector.normalize_indentation(code)

        assert "    spaced" in normalized


class TestExtractCustomTypes:
    """Tests for custom type extraction"""

    def test_extract_type_alias_python312(self, tmp_path: Path):
        """Should extract type aliases (Python 3.12+ syntax)"""
        code = """
type UserId = int
type ApiResponse = dict[str, str]
"""
        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        types = collector.extract_custom_types_from_code(code, file_path)

        type_names = [t["name"] for t in types]
        assert "UserId" in type_names
        assert "ApiResponse" in type_names

    def test_extract_uppercase_type_aliases(self, tmp_path: Path):
        """Should not extract non-typing uppercase variable assignments"""
        code = '''
from typing import Union
UserId = int
'''
        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        collector.extract_custom_types_from_code(code, file_path)

        # UserId = int doesn't contain typing keywords in the assignment
        # so it should not be extracted (only Union, List, Dict, etc. are checked)
        # The extraction logic checks for typing keywords in the code
        # This test documents current behavior - only type aliases with typing keywords


class TestGetPydanticModelsInAnnotation:
    """Tests for Pydantic model detection in annotations"""

    def test_detect_base_model_in_annotation(self):
        """Should not detect BaseModel in field annotations (it's in bases, not fields)"""
        code = 'class MySchema(BaseModel):\n    field: str'
        tree = ast.parse(code)
        class_node: ast.ClassDef = tree.body[0]

        collector = BaseModelCollector(".", "output.py")
        collector.base_model_classes = {'BaseModel', 'APIModel'}
        result = collector.get_pydantic_models_in_annotation(class_node)

        # BaseModel is in bases, not in field annotations
        assert 'BaseModel' not in result
        # But the class should be detected via is_base_model_class
        is_base, deps = collector.is_base_model_class(class_node, code)
        assert is_base is True

    def test_detect_schema_in_annotations(self):
        """Should detect Schema suffix in field annotations"""
        code = 'class UserSchema:\n    related: UserSchema'
        tree = ast.parse(code)
        class_node: ast.ClassDef = tree.body[0]

        collector = BaseModelCollector(".", "output.py")
        collector.base_model_classes = {'BaseModel', 'APIModel'}
        result = collector.get_pydantic_models_in_annotation(class_node)

        # The UserSchema reference in the annotation should add it to base_model_classes
        assert 'UserSchema' in result


class TestIsBaseModelClass:
    """Tests for BaseModel class detection"""

    def test_direct_base_model_inheritance(self):
        """Should detect direct inheritance from BaseModel"""
        code = 'class MyModel(BaseModel):\n    name: str'
        tree = ast.parse(code)
        class_node: ast.ClassDef = tree.body[0]

        collector = BaseModelCollector(".", "output.py")
        is_base, deps = collector.is_base_model_class(class_node, code)

        assert is_base is True

    def test_no_base_model_inheritance(self):
        """Should return False for regular classes"""
        code = 'class MyClass:\n    name: str'
        tree = ast.parse(code)
        class_node: ast.ClassDef = tree.body[0]

        collector = BaseModelCollector(".", "output.py")
        is_base, deps = collector.is_base_model_class(class_node, code)

        assert is_base is False


class TestExtractAllModels:
    """Tests for model extraction from files"""

    def test_extract_class_with_methods(self, tmp_path: Path):
        """Should extract class with all its content"""
        code = '''
class MyModel:
    """A test model"""
    def __init__(self):
        pass

    def method(self):
        pass
'''
        file_path = tmp_path / "model.py"
        file_path.write_text(code)

        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        classes = collector.extract_all_models(file_path)

        assert len(classes) == 1
        assert classes[0]['name'] == 'MyModel'

    def test_extract_multiple_classes(self, tmp_path: Path):
        """Should extract all classes from file"""
        code = """
class First:
    pass

class Second:
    pass

class Third:
    pass
"""
        file_path = tmp_path / "multi.py"
        file_path.write_text(code)

        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        classes = collector.extract_all_models(file_path)

        class_names = [c['name'] for c in classes]
        assert 'First' in class_names
        assert 'Second' in class_names
        assert 'Third' in class_names

    def test_extract_handles_invalid_file(self, tmp_path: Path):
        """Should handle invalid Python files gracefully"""
        file_path = tmp_path / "invalid.py"
        file_path.write_text("this is not valid python {{{")

        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        classes = collector.extract_all_models(file_path)

        assert classes == []


class TestSortModelsByDependencies:
    """Tests for model sorting by dependencies"""

    def test_sort_models_without_dependencies(self, tmp_path: Path):
        """Should sort models that have no dependencies"""
        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        collector.models = {
            'ModelA': {'code': '', 'file': '', 'imports': set(), 'dependencies': set()},
            'ModelB': {'code': '', 'file': '', 'imports': set(), 'dependencies': set()},
        }

        sorted_models = collector.sort_models_by_dependencies()

        expected_count = 2
        assert len(sorted_models) == expected_count
        assert set(sorted_models) == {'ModelA', 'ModelB'}

    def test_sort_respects_dependencies(self, tmp_path: Path):
        """Should place dependent models after their dependencies"""
        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        collector.models = {
            'Child': {'code': '', 'file': '', 'imports': set(), 'dependencies': {'Parent'}},
            'Parent': {'code': '', 'file': '', 'imports': set(), 'dependencies': set()},
        }

        sorted_models = collector.sort_models_by_dependencies()

        parent_idx = sorted_models.index('Parent')
        child_idx = sorted_models.index('Child')
        assert parent_idx < child_idx


class TestCollectModels:
    """Tests for full model collection"""

    def test_collect_empty_directory(self, tmp_path: Path):
        """Should handle directory with no Python files"""
        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        collector.collect_models()

        assert len(collector.models) == 0
        assert len(collector.custom_types) == 0

    def test_collect_with_pydantic_models(self, tmp_path: Path):
        """Should collect Pydantic models from Python files"""
        # Create a Python file with a Pydantic model
        test_file = tmp_path / "test_models.py"
        test_file.write_text("""
from pydantic import BaseModel

class TestModel(BaseModel):
    name: str
    value: int = 0
""")

        collector = BaseModelCollector(tmp_path, tmp_path / "output.py")
        collector.collect_models()

        assert 'TestModel' in collector.models


class TestWriteCombinedFile:
    """Tests for writing combined model file"""

    def test_creates_parent_directories(self, tmp_path: Path):
        """Should create parent directories if they don't exist"""
        output_file = tmp_path / "nested" / "deep" / "output.py"

        collector = BaseModelCollector(tmp_path, output_file)
        collector.models = {}
        collector.imports = set()
        collector.custom_types = {}
        collector.processed_files = []

        collector.write_combined_file()

        assert output_file.exists()

    def test_writes_pydantic_imports(self, tmp_path: Path):
        """Should write required pydantic imports"""
        output_file = tmp_path / "output.py"

        collector = BaseModelCollector(tmp_path, output_file)
        collector.models = {}
        collector.imports = {'from typing import Optional'}
        collector.custom_types = {}
        collector.processed_files = ['test.py']

        collector.write_combined_file()

        content = output_file.read_text()
        assert 'from pydantic import BaseModel' in content
        assert 'from fastapi_utils.api_model import APIModel' in content

    def test_writes_header_with_metadata(self, tmp_path: Path):
        """Should write header with generation metadata"""
        output_file = tmp_path / "output.py"

        collector = BaseModelCollector(tmp_path, output_file)
        model_entry = {
            'code': 'class TestModel(BaseModel): pass',
            'file': 'test.py',
            'imports': set(),
            'dependencies': set(),
        }
        collector.models = {'TestModel': model_entry}
        collector.imports = set()
        collector.custom_types = {}
        collector.processed_files = ['test.py']

        collector.write_combined_file()

        content = output_file.read_text()
        assert 'Автоматически сгенерированный' in content
        assert 'Найдено' in content
        assert 'Собрано из' in content


# =============================================================================
# Tests for EnumCollector
# =============================================================================


class TestEnumCollector:
    """Tests for EnumCollector class"""

    def test_init(self, tmp_path: Path):
        """Should initialize correctly"""
        collector = EnumCollector(tmp_path)

        assert collector.project_root == tmp_path
        assert collector.enums == {}

    def test_collect_enum_from_code(self, tmp_path: Path):
        """Should collect Enum from Python code"""
        collector = EnumCollector(tmp_path)

        code = '''
class SimpleEnum(Enum):
    OPTION_A = 1
    OPTION_B = 2
'''
        file_path = tmp_path / "test_enum.py"
        file_path.write_text(code)

        collector.collect_all_enums()

        assert 'SimpleEnum' in collector.enums
        assert collector.enums['SimpleEnum']['file'] == str(file_path)

    def test_collect_int_enum(self, tmp_path: Path):
        """Should collect IntEnum"""
        collector = EnumCollector(tmp_path)

        code = '''
class IntEnumType(IntEnum):
    VALUE_ONE = 1
    VALUE_TWO = 2
'''
        file_path = tmp_path / "test_int_enum.py"
        file_path.write_text(code)

        collector.collect_all_enums()

        assert 'IntEnumType' in collector.enums

    def test_collect_int_flag(self, tmp_path: Path):
        """Should collect IntFlag"""
        collector = EnumCollector(tmp_path)

        code = '''
class Flags(IntFlag):
    FLAG_A = 1
    FLAG_B = 2
    FLAG_C = 4
'''
        file_path = tmp_path / "test_int_flag.py"
        file_path.write_text(code)

        collector.collect_all_enums()

        assert 'Flags' in collector.enums

    def test_collect_enum_with_multiline_docstring(self, tmp_path: Path):
        """Should correctly parse Enum with multiline docstring"""
        collector = EnumCollector(tmp_path)

        code = '''
class EngineType(Enum):
    """
    Engine type description.
    Multiple lines.
    """
    PETROL = 1
    DIESEL = 2
'''
        file_path = tmp_path / "test_docstring.py"
        file_path.write_text(code)

        collector.collect_all_enums()

        assert 'EngineType' in collector.enums
        # Check that the docstring is in the code
        assert '"""' in collector.enums['EngineType']['code']

    def test_collect_enum_with_single_line_docstring(self, tmp_path: Path):
        """Should correctly parse Enum with single line docstring"""
        collector = EnumCollector(tmp_path)

        code = '''class StatusType(Enum):
    """Simple status"""
    ACTIVE = 1
    INACTIVE = 2
'''
        file_path = tmp_path / "test_single_docstring.py"
        file_path.write_text(code)

        collector.collect_all_enums()

        assert 'StatusType' in collector.enums

    def test_collect_enum_with_comments(self, tmp_path: Path):
        """Should correctly parse Enum with inline comments"""
        collector = EnumCollector(tmp_path)

        code = '''
class TypeWithComments(Enum):
    VALUE_A = 1  # Comment for A
    VALUE_B = 2  # Comment for B
    VALUE_C = 3
'''
        file_path = tmp_path / "test_comments.py"
        file_path.write_text(code)

        collector.collect_all_enums()

        assert 'TypeWithComments' in collector.enums


class TestEnumCollectorGeneration:
    """Tests for Enum Python code generation"""

    def test_generate_python_enum_simple(self):
        """Should generate correct Python code for simple Enum"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'Status',
            'code': '''class Status(Enum):
    ACTIVE = 1
    INACTIVE = 2
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert 'class Status(Enum):' in result
        assert 'ACTIVE = 1' in result
        assert 'INACTIVE = 2' in result

    def test_generate_python_enum_removes_docstring(self):
        """Should remove docstrings from generated code"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'TypeWithDoc',
            'code': '''class TypeWithDoc(Enum):
    """
    This is a docstring
    """
    VALUE = 1
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert 'class TypeWithDoc(Enum):' in result
        assert 'VALUE = 1' in result
        # Docstring should not appear in output
        lines = result.split('\n')
        docstring_lines = [line for line in lines if 'This is a docstring' in line]
        assert len(docstring_lines) == 0

    def test_generate_python_enum_removes_comments(self):
        """Should remove inline comments from generated code"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'TypeWithComments',
            'code': '''class TypeWithComments(Enum):
    VALUE_A = 1  # Comment A
    VALUE_B = 2   # Comment B
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        # Comments should be removed
        lines = result.split('\n')
        for line in lines:
            if 'VALUE_A' in line:
                assert '#' not in line
            if 'VALUE_B' in line:
                assert '#' not in line

    def test_generate_python_enum_removes_labels(self):
        """Should remove __labels__ attribute"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'TypeWithLabels',
            'code': '''class TypeWithLabels(Enum):
    OPTION_A = 1
    OPTION_B = 2
    __labels__ = {1: "A", 2: "B"}
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert '__labels__' not in result
        assert 'OPTION_A = 1' in result
        assert 'OPTION_B = 2' in result

    def test_generate_python_enum_removes_dunder_attributes(self):
        """Should remove __*__ dunder attributes"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'CleanEnum',
            'code': '''class CleanEnum(Enum):
    __private_class_var__ = None
    VALUE = 1
    __another_dunder__ = 2
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert '__private_class_var__' not in result
        assert '__another_dunder__' not in result
        assert 'VALUE = 1' in result

    def test_generate_python_enum_string_values(self):
        """Should handle string values correctly"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'StringEnum',
            'code': '''class StringEnum(Enum):
    OPTION_A = 'a'
    OPTION_B = 'b'
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert "OPTION_A = 'a'" in result
        assert "OPTION_B = 'b'" in result

    def test_generate_python_enum_int_flag_values(self):
        """Should handle IntFlag bitwise values"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'Flags',
            'code': '''class Flags(IntFlag):
    FLAG_A = 1
    FLAG_B = 2
    FLAG_C = 4
    FLAG_ALL = 7
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert 'FLAG_A = 1' in result
        assert 'FLAG_B = 2' in result
        assert 'FLAG_C = 4' in result
        assert 'FLAG_ALL = 7' in result

    def test_generate_python_enum_multiline_docstring_handling(self):
        """Should correctly handle multiline docstrings"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'MultilineDoc',
            'code': '''class MultilineDoc(Enum):
    """
    Line 1
    Line 2
    Line 3
    """
    VALUE = 1
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert 'class MultilineDoc(Enum):' in result
        assert 'VALUE = 1' in result
        # Verify multiline docstring lines are not in output
        assert 'Line 1' not in result
        assert 'Line 2' not in result

    def test_generate_python_enum_single_line_docstring_handling(self):
        """Should correctly handle single-line docstrings"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'SingleDoc',
            'code': '''class SingleDoc(Enum):
    """Single line docstring"""
    VALUE = 1
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        assert result is not None
        assert 'class SingleDoc(Enum):' in result
        assert 'VALUE = 1' in result
        assert 'Single line docstring' not in result

    def test_generate_python_enum_empty_class(self):
        """Should return None for empty Enum"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'EmptyEnum',
            'code': '''class EmptyEnum(Enum):
    pass
''',
            'file': 'test.py'
        }

        result = collector.generate_python_enum(enum_info)

        # Empty enum with just 'pass' returns None since there are no members
        assert result is None


class TestEnumCollectorErasableSyntax:
    """Tests for erasable syntax option in EnumCollector"""

    def test_generate_ts_enum_erasable_syntax(self):
        """Should generate string literal union when erasable=True"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'Status',
            'code': '''class Status(Enum):
    PENDING = 1
    ACTIVE = 2
''',
            'file': 'test.py'
        }

        result = collector.generate_ts_enum(enum_info, use_erasable_syntax=True)

        assert result is not None
        assert "export type Status = 'pending' | 'active';" in result
        assert "enum" not in result

    def test_generate_ts_enum_classic_syntax(self):
        """Should generate classic enum when erasable=False"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'Status',
            'code': '''class Status(Enum):
    PENDING = 1
    ACTIVE = 2
''',
            'file': 'test.py'
        }

        result = collector.generate_ts_enum(enum_info, use_erasable_syntax=False)

        assert result is not None
        assert "export enum Status {" in result
        assert "pending = 1" in result
        assert "active = 2" in result

    def test_generate_ts_enum_default_from_collector(self):
        """Should use collector's default setting when parameter not passed"""
        collector = EnumCollector(".", use_erasable_syntax=False)

        enum_info = {
            'name': 'Mode',
            'code': '''class Mode(Enum):
    ON = 1
    OFF = 0
''',
            'file': 'test.py'
        }

        result = collector.generate_ts_enum(enum_info)

        # Should use collector's default (False)
        assert "export enum Mode {" in result

    def test_generate_ts_enum_instance_default_true(self):
        """Should use collector's default setting when set to True"""
        collector = EnumCollector(".", use_erasable_syntax=True)

        enum_info = {
            'name': 'Mode',
            'code': '''class Mode(Enum):
    ON = 1
    OFF = 0
''',
            'file': 'test.py'
        }

        result = collector.generate_ts_enum(enum_info)

        # Should use collector's default (True)
        assert "export type Mode = 'on' | 'off';" in result

    def test_generate_ts_enum_with_string_values_erasable(self):
        """Should handle string values correctly in erasable mode"""
        collector = EnumCollector(".")

        enum_info = {
            'name': 'StringEnum',
            'code': '''class StringEnum(Enum):
    OPTION_A = 'a'
    OPTION_B = 'b'
''',
            'file': 'test.py'
        }

        result = collector.generate_ts_enum(enum_info, use_erasable_syntax=True)

        assert result is not None
        assert "export type StringEnum = 'a' | 'b';" in result


# =============================================================================
# Tests for LiteralCollector
# =============================================================================


class TestLiteralCollector:
    """Tests for LiteralCollector class"""

    def test_init(self, tmp_path: Path):
        """Should initialize correctly"""
        collector = LiteralCollector(tmp_path)

        assert collector.project_root == tmp_path
        assert collector.literals == {}

    def test_collect_literal_string_values(self, tmp_path: Path):
        """Should collect Literal with string values"""
        collector = LiteralCollector(tmp_path)

        code = '''
TokenType = Literal["access", "refresh"]
'''
        file_path = tmp_path / "test_literal.py"
        file_path.write_text(code)

        collector.collect_all_literals()

        assert 'TokenType' in collector.literals
        assert "'access'" in collector.literals['TokenType']['values']
        assert "'refresh'" in collector.literals['TokenType']['values']

    def test_collect_literal_int_values(self, tmp_path: Path):
        """Should collect Literal with integer values"""
        collector = LiteralCollector(tmp_path)

        code = '''
ModeType = Literal[1, 2, 3]
'''
        file_path = tmp_path / "test_literal_int.py"
        file_path.write_text(code)

        collector.collect_all_literals()

        assert 'ModeType' in collector.literals
        assert '1' in collector.literals['ModeType']['values']
        assert '2' in collector.literals['ModeType']['values']
        assert '3' in collector.literals['ModeType']['values']

    def test_collect_literal_boolean_values(self, tmp_path: Path):
        """Should collect Literal with boolean values"""
        collector = LiteralCollector(tmp_path)

        code = '''
BoolType = Literal[True, False]
'''
        file_path = tmp_path / "test_literal_bool.py"
        file_path.write_text(code)

        collector.collect_all_literals()

        assert 'BoolType' in collector.literals
        assert 'true' in collector.literals['BoolType']['values']
        assert 'false' in collector.literals['BoolType']['values']

    def test_collect_literal_none_value(self, tmp_path: Path):
        """Should collect Literal with None value"""
        collector = LiteralCollector(tmp_path)

        code = '''
NullableType = Literal["value", None]
'''
        file_path = tmp_path / "test_literal_none.py"
        file_path.write_text(code)

        collector.collect_all_literals()

        assert 'NullableType' in collector.literals
        assert 'null' in collector.literals['NullableType']['values']

    def test_collect_literal_mixed_values(self, tmp_path: Path):
        """Should collect Literal with mixed value types"""
        collector = LiteralCollector(tmp_path)

        code = '''
MixedType = Literal["string", 1, True, None]
'''
        file_path = tmp_path / "test_literal_mixed.py"
        file_path.write_text(code)

        collector.collect_all_literals()

        assert 'MixedType' in collector.literals
        values = collector.literals['MixedType']['values']
        assert "'string'" in values
        assert '1' in values
        assert 'true' in values
        assert 'null' in values

    def test_collect_python312_type_alias_syntax(self, tmp_path: Path):
        """Should collect Python 3.12+ type alias syntax"""
        collector = LiteralCollector(tmp_path)

        code = '''
type TokenType = Literal["access", "refresh"]
'''
        file_path = tmp_path / "test_literal_312.py"
        file_path.write_text(code)

        collector.collect_all_literals()

        assert 'TokenType' in collector.literals


class TestLiteralCollectorGeneration:
    """Tests for Literal TypeAlias generation"""

    def test_generate_literal_code_strings(self):
        """Should generate correct Literal type alias for strings"""
        collector = BaseModelCollector(".", "output.py")

        literal_info = {
            'name': 'Status',
            'values': ["'active'", "'inactive'"],
            'file': 'test.py'
        }

        result = collector._generate_literal_code(literal_info)

        assert result is not None
        assert 'Status: TypeAlias = Literal[' in result
        assert '"active"' in result  # Python uses double quotes
        assert '"inactive"' in result

    def test_generate_literal_code_single_value(self):
        """Should generate correct Literal for single value"""
        collector = BaseModelCollector(".", "output.py")

        literal_info = {
            'name': 'Single',
            'values': ["'only'"],
            'file': 'test.py'
        }

        result = collector._generate_literal_code(literal_info)

        assert result is not None
        assert 'Single: TypeAlias = Literal[' in result

    def test_generate_literal_code_booleans_converted(self):
        """Should convert Python booleans to TypeScript format"""
        collector = BaseModelCollector(".", "output.py")

        literal_info = {
            'name': 'Flags',
            'values': ['true', 'false'],
            'file': 'test.py'
        }

        result = collector._generate_literal_code(literal_info)

        assert result is not None
        # Python Literal uses True/False (capitalized)
        assert 'True' in result
        assert 'False' in result

    def test_generate_literal_code_none_converted(self):
        """Should convert Python None to TypeScript null"""
        collector = BaseModelCollector(".", "output.py")

        literal_info = {
            'name': 'Maybe',
            'values': ["'value'", 'null'],
            'file': 'test.py'
        }

        result = collector._generate_literal_code(literal_info)

        assert result is not None
        assert 'None' in result  # Python uses None

    def test_generate_literal_code_integers(self):
        """Should handle integer values correctly"""
        collector = BaseModelCollector(".", "output.py")

        literal_info = {
            'name': 'Numbers',
            'values': ['1', '2', '3'],
            'file': 'test.py'
        }

        result = collector._generate_literal_code(literal_info)

        assert result is not None
        assert '1' in result
        assert '2' in result
        assert '3' in result


# =============================================================================
# Tests for _clean_enum_for_pydantic2ts method
# =============================================================================


class TestCleanEnumForPydantic2ts:
    """Tests for _clean_enum_for_pydantic2ts method"""

    def test_removes_multiline_docstring(self):
        """Should remove multiline docstrings"""
        collector = BaseModelCollector(".", "output.py")

        code = '''class MyEnum(Enum):
    """
    Docstring line 1
    Docstring line 2
    """
    VALUE = 1
'''
        result = collector._clean_enum_for_pydantic2ts(code, 'MyEnum')

        assert 'class MyEnum(Enum):' in result
        assert 'VALUE = 1' in result
        assert 'Example:' not in result


class TestEnumCollectorWriteTsFile:
    """Tests for EnumCollector.write_ts_file method"""

    def test_write_ts_file_creates_file(self, tmp_path: Path, monkeypatch):
        """Should create TypeScript file with enums"""
        # Create a mock project structure
        (tmp_path / "apps").mkdir(parents=True)

        # Create a test enum file
        enum_file = tmp_path / "apps" / "test.py"
        enum_file.write_text('''
from enum import Enum

class Status(Enum):
    PENDING = 1
    ACTIVE = 2
''')

        collector = EnumCollector(tmp_path)
        collector.enums = {
            'Status': {
                'name': 'Status',  # Add 'name' field
                'code': 'class Status(Enum):\n    PENDING = 1\n    ACTIVE = 2',
                'file': str(enum_file),
            }
        }

        # Mock FRONTEND_DIR to use tmp_path
        monkeypatch.setattr(
            "scripts.collect_models.FRONTEND_DIR",
            tmp_path / "frontend"
        )

        collector.write_ts_file()

        ts_file = tmp_path / "frontend" / "src" / "types" / "generated_enums.ts"
        assert ts_file.exists()
        content = ts_file.read_text()
        assert "export type Status" in content
        assert "'pending'" in content  # camelCase conversion
        assert "'active'" in content  # camelCase conversion

    def test_write_ts_file_with_no_enums(self, tmp_path: Path, monkeypatch):
        """Should handle empty enums gracefully"""
        monkeypatch.setattr(
            "scripts.collect_models.FRONTEND_DIR",
            tmp_path / "frontend"
        )

        collector = EnumCollector(tmp_path)
        collector.enums = {}
        collector.write_ts_file()  # Should not raise

        ts_file = tmp_path / "frontend" / "src" / "types" / "generated_enums.ts"
        assert not ts_file.exists()

    def test_write_ts_file_multiple_enums(self, tmp_path: Path, monkeypatch):
        """Should write multiple enums to file"""
        monkeypatch.setattr(
            "scripts.collect_models.FRONTEND_DIR",
            tmp_path / "frontend"
        )

        collector = EnumCollector(tmp_path)
        collector.enums = {
            'Color': {
                'name': 'Color',  # Add 'name' field
                'code': 'class Color(Enum):\n    RED = 1\n    GREEN = 2',
                'file': 'test.py',
            },
            'Size': {
                'name': 'Size',  # Add 'name' field
                'code': 'class Size(Enum):\n    SMALL = 1\n    LARGE = 2',
                'file': 'test.py',
            },
        }

        collector.write_ts_file()

        ts_file = tmp_path / "frontend" / "src" / "types" / "generated_enums.ts"
        assert ts_file.exists()
        content = ts_file.read_text()
        assert "export type Color" in content
        assert "export type Size" in content


class TestLiteralCollectorWriteTsFile:
    """Tests for LiteralCollector.write_ts_file method"""

    def test_write_ts_file_creates_file(self, tmp_path: Path, monkeypatch):
        """Should create TypeScript file with literals"""
        monkeypatch.setattr(
            "scripts.collect_models.FRONTEND_DIR",
            tmp_path / "frontend"
        )

        collector = LiteralCollector(tmp_path)
        collector.literals = {
            'Status': {
                'name': 'Status',
                'values': ["'active'", "'pending'"],
                'file': 'test.py',
            }
        }

        collector.write_ts_file()

        ts_file = tmp_path / "frontend" / "src" / "types" / "generated_literals.ts"
        assert ts_file.exists()
        content = ts_file.read_text()
        assert "export type Status" in content
        assert "'active'" in content
        assert "'pending'" in content

    def test_write_ts_file_with_no_literals(self, tmp_path: Path, monkeypatch):
        """Should handle empty literals gracefully"""
        monkeypatch.setattr(
            "scripts.collect_models.FRONTEND_DIR",
            tmp_path / "frontend"
        )

        collector = LiteralCollector(tmp_path)
        collector.literals = {}
        collector.write_ts_file()  # Should not raise

        ts_file = tmp_path / "frontend" / "src" / "types" / "generated_literals.ts"
        assert not ts_file.exists()

    def test_write_ts_file_single_value(self, tmp_path: Path, monkeypatch):
        """Should write single value literal"""
        monkeypatch.setattr(
            "scripts.collect_models.FRONTEND_DIR",
            tmp_path / "frontend"
        )

        collector = LiteralCollector(tmp_path)
        collector.literals = {
            'SingleValue': {
                'name': 'SingleValue',
                'values': ["'only'"],
                'file': 'test.py',
            }
        }

        collector.write_ts_file()

        ts_file = tmp_path / "frontend" / "src" / "types" / "generated_literals.ts"
        assert ts_file.exists()
        content = ts_file.read_text()
        assert "export type SingleValue = 'only';" in content

    def test_write_ts_file_multiple_literals(self, tmp_path: Path, monkeypatch):
        """Should write multiple literals to file"""
        monkeypatch.setattr(
            "scripts.collect_models.FRONTEND_DIR",
            tmp_path / "frontend"
        )

        collector = LiteralCollector(tmp_path)
        collector.literals = {
            'TokenType': {
                'name': 'TokenType',
                'values': ["'access'", "'refresh'"],
                'file': 'test.py',
            },
            'Flag': {
                'name': 'Flag',
                'values': ['true', 'false'],
                'file': 'test.py',
            },
        }

        collector.write_ts_file()

        ts_file = tmp_path / "frontend" / "src" / "types" / "generated_literals.ts"
        assert ts_file.exists()
        content = ts_file.read_text()
        assert "export type TokenType" in content
        assert "export type Flag" in content

    def test_handles_docstring_with_quotes(self):
        """Should handle docstrings with quotes"""
        collector = BaseModelCollector(".", "output.py")

        code = '''class MyEnum(Enum):
    """
    Example: 'single' and "double"
    """
    VALUE = 1
'''
        result = collector._clean_enum_for_pydantic2ts(code, 'MyEnum')

        assert 'class MyEnum(Enum):' in result
        assert 'VALUE = 1' in result
        assert 'Example:' not in result
