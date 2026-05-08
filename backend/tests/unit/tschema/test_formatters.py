"""Tests for tschema formatters."""

import pytest

from tschema.formatters.typescript import TypeScriptFormatter


class TestTypeScriptFormatter:
    """Tests for TypeScriptFormatter."""

    def test_format_interface(self):
        """Should format interface correctly."""
        formatter = TypeScriptFormatter()

        fields = [
            {"name": "id", "ts_type": "number"},
            {"name": "name", "ts_type": "string"},
        ]

        result = formatter.format_interface("User", fields)

        assert "export interface User {" in result
        assert "id: number;" in result
        assert "name: string;" in result

    def test_format_interface_with_optional(self):
        """Should add ? for optional fields."""
        formatter = TypeScriptFormatter()

        fields = [
            {"name": "email", "ts_type": "string", "is_optional": True},
        ]

        result = formatter.format_interface("User", fields)

        assert "email?: string;" in result

    def test_format_enum_erasable(self):
        """Should format erasable enum (string literal union)."""
        formatter = TypeScriptFormatter()

        members = [("PENDING", "pending"), ("ACTIVE", "active")]
        result = formatter.format_enum("Status", members, use_erasable=True)

        assert "export type Status = 'pending' | 'active';" in result

    def test_format_enum_classic(self):
        """Should format classic enum."""
        formatter = TypeScriptFormatter()

        members = [("PENDING", "1"), ("ACTIVE", "2")]
        result = formatter.format_enum("Status", members, use_erasable=False)

        assert "export enum Status {" in result
        assert "PENDING = 1" in result

    def test_format_type_alias(self):
        """Should format type alias."""
        formatter = TypeScriptFormatter()

        result = formatter.format_type_alias("UserId", "string")

        assert result == "export type UserId = string;"

    def test_format_union(self):
        """Should format union type."""
        formatter = TypeScriptFormatter()

        result = formatter.format_union(["string", "number"])

        assert result == "string | number"

    def test_format_with_indent(self):
        """Should respect custom indent."""
        formatter = TypeScriptFormatter(indent="  ")

        fields = [{"name": "id", "ts_type": "number"}]
        result = formatter.format_interface("User", fields)

        assert "  id: number;" in result