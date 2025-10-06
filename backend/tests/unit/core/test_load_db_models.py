from core.models.loader import load_all_models


class TestLoadDBModels:
    def test_load_db_models(self):
        loaded_models, errors = load_all_models()
        assert not errors
        assert len(loaded_models) > 0
        assert all('abstract' not in it.lower() for it in loaded_models)
