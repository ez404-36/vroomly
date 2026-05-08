"""Tests for tschema config."""

import pytest
from pathlib import Path

from tschema.config import (
    TSchemaConfig,
    NamingConfig,
    OutputConfig,
    ExcludeConfig,
    TypeScriptConfig,
)


class TestNamingConfig:
    """Tests for NamingConfig."""

    def test_defaults(self):
        """Should have sensible defaults."""
        config = NamingConfig()

        assert config.models == "PascalCase"
        assert config.fields == "camelCase"


class TestOutputConfig:
    """Tests for OutputConfig."""

    def test_defaults(self):
        """Should have sensible defaults."""
        config = OutputConfig()

        assert config.output_dir == "src/types"
        assert config.file_pattern == "{name}.ts"


class TestExcludeConfig:
    """Tests for ExcludeConfig."""

    def test_empty_by_default(self):
        """Should be empty by default."""
        config = ExcludeConfig()

        assert config.models == []
        assert config.fields == []


class TestTSchemaConfig:
    """Tests for TSchemaConfig."""

    def test_defaults(self):
        """Should have sensible defaults."""
        config = TSchemaConfig()

        assert config.target == "react-query"
        assert config.strict is True
        assert config.use_erasable_syntax is True
        assert isinstance(config.output, OutputConfig)
        assert isinstance(config.naming, NamingConfig)
        assert isinstance(config.exclude, ExcludeConfig)
        assert isinstance(config.typescript, TypeScriptConfig)

    def test_from_pyproject_missing_file(self):
        """Should return defaults for missing file."""
        config = TSchemaConfig.from_pyproject("/nonexistent/path.toml")

        assert config.target == "react-query"

    def test_from_pyproject_invalid_toml(self, tmp_path: Path):
        """Should return defaults for invalid TOML."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("invalid toml content [[[[")

        config = TSchemaConfig.from_pyproject(pyproject)

        assert config.target == "react-query"

    def test_from_pyproject_valid_config(self, tmp_path: Path):
        """Should parse valid configuration."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.tschema]
target = "redux"
strict = false

[tool.tschema.output]
output_dir = "custom/types"

[tool.tschema.exclude]
models = ["BaseModel"]
fields = ["created_at"]
""")

        config = TSchemaConfig.from_pyproject(pyproject)

        assert config.target == "redux"
        assert config.strict is False
        assert config.output.output_dir == "custom/types"
        assert "BaseModel" in config.exclude.models
        assert "created_at" in config.exclude.fields

    def test_to_dict(self):
        """Should convert to dictionary."""
        config = TSchemaConfig()

        result = config.to_dict()

        assert isinstance(result, dict)
        assert "target" in result
        assert "output" in result
        assert "naming" in result


class TestTypeScriptConfig:
    """Tests for TypeScriptConfig."""

    def test_defaults(self):
        """Should have sensible defaults."""
        config = TypeScriptConfig()

        assert config.tsconfig_path is None
        assert config.strict_mode == "inherit"
        assert config.module_resolution == "node"