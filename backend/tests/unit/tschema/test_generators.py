"""Tests for tschema generators."""

import pytest

from tschema.generators.enum import generate_enum, _to_camel_case
from tschema.generators.interface import generate_interface
from tschema.generators.type_alias import generate_type_alias
from tschema.generators.union import generate_union
from tschema.generators.utility import generate_partial, generate_omit
from tschema.backends.base import ParsedModel, ParsedField


class TestEnumGenerator:
    """Tests for enum generator."""

    def test_generate_erasable_enum_int_values(self):
        """Should generate string literal union for int values."""
        result = generate_enum(
            name="Status",
            members={"PENDING": 1, "ACTIVE": 2},
            use_erasable_syntax=True,
        )

        assert "export type Status = " in result
        assert "'pending' | 'active'" in result

    def test_generate_erasable_enum_string_values(self):
        """Should use string values as-is."""
        result = generate_enum(
            name="Color",
            members={"RED": "red", "GREEN": "green"},
            use_erasable_syntax=True,
        )

        assert "export type Color = 'red' | 'green';" in result

    def test_generate_classic_enum(self):
        """Should generate classic TypeScript enum."""
        result = generate_enum(
            name="Status",
            members={"PENDING": 1, "ACTIVE": 2},
            use_erasable_syntax=False,
        )

        assert "export enum Status {" in result
        assert "PENDING = 1" in result
        assert "ACTIVE = 2" in result

    def test_to_camel_case(self):
        """Should convert UPPER_SNAKE_CASE to camelCase."""
        assert _to_camel_case("PENDING") == "pending"
        assert _to_camel_case("IS_ACTIVE") == "isActive"
        assert _to_camel_case("already_camel") == "already_camel"


class TestInterfaceGenerator:
    """Tests for interface generator."""

    def test_generate_simple_interface(self):
        """Should generate TypeScript interface."""
        model = ParsedModel(
            name="User",
            fields=[
                ParsedField(name="id", python_type="int", ts_type="number"),
                ParsedField(name="name", python_type="str", ts_type="string"),
            ],
        )

        result = generate_interface(model)

        assert "export interface User {" in result
        assert "id: number;" in result
        assert "name: string;" in result

    def test_generate_interface_with_optional(self):
        """Should handle optional fields."""
        model = ParsedModel(
            name="Config",
            fields=[
                ParsedField(name="required", python_type="str", ts_type="string"),
                ParsedField(
                    name="optional",
                    python_type="Optional[str]",
                    ts_type="string",
                    is_optional=True,
                ),
            ],
        )

        result = generate_interface(model)

        assert "required: string;" in result
        assert "optional: string | undefined;" in result

    def test_generate_interface_optional_syntax(self):
        """Should use ? for optional fields."""
        model = ParsedModel(
            name="Form",
            fields=[
                ParsedField(
                    name="email",
                    python_type="Optional[str]",
                    ts_type="string",
                    is_optional=True,
                ),
            ],
        )

        result = generate_interface(model, use_optional_syntax=True)

        assert "email?: string;" in result

    def test_generate_interface_with_alias(self):
        """Should use alias for field name."""
        model = ParsedModel(
            name="Model",
            fields=[
                ParsedField(
                    name="fieldName",
                    python_type="str",
                    ts_type="string",
                    alias="field_name",
                ),
            ],
        )

        result = generate_interface(model)

        assert "field_name: string;" in result


class TestTypeAliasGenerator:
    """Tests for type alias generator."""

    def test_generate_simple_type_alias(self):
        """Should generate type alias."""
        result = generate_type_alias("UserId", "string")

        assert "export type UserId = string;" in result

    def test_generate_complex_type_alias(self):
        """Should handle complex types."""
        result = generate_type_alias("UserOrNull", "User | null")

        assert "export type UserOrNull = User | null;" in result


class TestUnionGenerator:
    """Tests for union generator."""

    def test_generate_union_with_name(self):
        """Should generate named union type."""
        result = generate_union(["string", "number"], "StringOrNumber")

        assert "export type StringOrNumber = string | number;" in result

    def test_generate_union_without_name(self):
        """Should generate anonymous union."""
        result = generate_union(["string", "number"])

        assert result == "string | number"


class TestUtilityGenerator:
    """Tests for utility type generators."""

    def test_generate_partial(self):
        """Should generate Partial<> type."""
        result = generate_partial("User")

        assert result == "Partial<User>"

    def test_generate_omit(self):
        """Should generate Omit<> type."""
        result = generate_omit("User", ["password", "token"])

        assert "Omit<User" in result
        assert "'password'" in result
        assert "'token'" in result