from core.models.loader import load_all_models


class TestLoadSchemaModels:
    def test_load_schema_models(self):
        loaded_models, errors = load_all_models()
        assert not errors
        assert len(loaded_models) > 0
        assert all('abstract' not in it.lower() for it in loaded_models)
