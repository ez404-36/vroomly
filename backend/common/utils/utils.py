from typing import Any


def import_class(path_to_class: str) -> Any:
	path_chunks = path_to_class.split(".")
	module = __import__(".".join(path_chunks[:-1]), fromlist=["*"])
	return getattr(module, path_chunks[-1], None)
