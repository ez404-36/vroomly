"""Tests for tschema backends."""

import pytest
from typing import Optional

from pydantic import BaseModel

from tschema.backends.base import ParsedField, ParsedModel
from tschema.backends.pydantic import PydanticParser


class TestPydanticParser:
    """Tests for PydanticParser."""

    def test_can_parse_pydantic_model(self):
        """Should detect Pydantic BaseModel."""
        parser = PydanticParser()

        class TestModel(BaseModel):
            name: str

        assert parser.can_parse(TestModel) is True

    def test_cannot_parse_regular_class(self):
        """Should not match regular Python classes."""
        parser = PydanticParser()

        class RegularClass:
            pass

        assert parser.can_parse(RegularClass) is False

    def test_parse_model_fields(self):
        """Should parse model fields correctly."""
        parser = PydanticParser()

        class UserModel(BaseModel):
            id: int
            name: str
            email: Optional[str] = None

        parsed = parser.parse_model(UserModel)

        assert parsed is not None
        assert parsed.name == "UserModel"
        assert len(parsed.fields) == 3

        field_names = [f.name for f in parsed.fields]
        assert "id" in field_names
        assert "name" in field_names
        assert "email" in field_names

    def test_parse_optional_field(self):
        """Should correctly identify optional fields."""
        parser = PydanticParser()

        class OptionalModel(BaseModel):
            required: str
            optional: Optional[str] = None

        parsed = parser.parse_model(OptionalModel)

        assert parsed is not None

        required_field = next(f for f in parsed.fields if f.name == "required")
        assert required_field.is_optional is False

        optional_field = next(f for f in parsed.fields if f.name == "optional")
        assert optional_field.is_optional is True

    def test_parse_list_field(self):
        """Should correctly identify list fields."""
        parser = PydanticParser()

        class ListModel(BaseModel):
            tags: list[str]

        parsed = parser.parse_model(ListModel)

        assert parsed is not None

        tags_field = next(f for f in parsed.fields if f.name == "tags")
        assert tags_field.is_list is True
        assert tags_field.ts_type == "string[]"

    def test_parse_dict_field(self):
        """Should correctly identify dict fields."""
        parser = PydanticParser()

        class DictModel(BaseModel):
            metadata: dict[str, str]

        parsed = parser.parse_model(DictModel)

        assert parsed is not None

        meta_field = next(f for f in parsed.fields if f.name == "metadata")
        assert meta_field.is_dict is True
        assert "Record<string, string>" in meta_field.ts_type


class TestParsedField:
    """Tests for ParsedField dataclass."""

    def test_basic_field(self):
        """Should create field with required params."""
        field = ParsedField(
            name="test",
            python_type="str",
            ts_type="string",
        )

        assert field.name == "test"
        assert field.python_type == "str"
        assert field.ts_type == "string"
        assert field.is_optional is False

    def test_optional_field_with_defaults(self):
        """Should create field with default values."""
        field = ParsedField(
            name="optional_field",
            python_type="Optional[str]",
            ts_type="string",
            is_optional=True,
            default_value="default",
        )

        assert field.is_optional is True
        assert field.default_value == "default"

    def test_field_with_alias(self):
        """Should store validation alias."""
        field = ParsedField(
            name="fieldName",
            python_type="str",
            ts_type="string",
            alias="field_name",
        )

        assert field.alias == "field_name"


class TestParsedModel:
    """Tests for ParsedModel dataclass."""

    def test_basic_model(self):
        """Should create model with fields."""
        model = ParsedModel(
            name="TestModel",
            fields=[
                ParsedField(name="id", python_type="int", ts_type="number"),
                ParsedField(name="name", python_type="str", ts_type="string"),
            ],
        )

        assert model.name == "TestModel"
        assert len(model.fields) == 2

    def test_model_with_bases(self):
        """Should track base classes."""
        model = ParsedModel(
            name="ChildModel",
            bases=["BaseModel", "Mixin"],
            fields=[],
        )

        assert model.bases == ["BaseModel", "Mixin"]

    def test_enum_model(self):
        """Should track enum information."""
        model = ParsedModel(
            name="Status",
            is_enum=True,
            enum_members={"ACTIVE": 1, "INACTIVE": 0},
        )

        assert model.is_enum is True
        assert model.enum_members["ACTIVE"] == 1