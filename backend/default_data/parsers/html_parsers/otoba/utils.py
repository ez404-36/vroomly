import pickle
import re
from pathlib import Path

from core.db import database

from .types import NUMBER_PATTERN


def find_first_number_in_text(text: str) -> int | None:
	"""Находит первое число в строке и возвращает его"""
	search = re.search(NUMBER_PATTERN, text)
	return search and int(search[0])


async def create_from_pkl_file(pkl_file: str | Path):
	with open(pkl_file, 'rb') as f_obj:
		data = pickle.load(f_obj)

	engines = data.get('engines', [])
	transmissions = data.get('transmissions', [])

	async with database.get_async_session() as session:
		session.add_all(engines)
		session.add_all([it for it in transmissions if it.type is not None])
		await session.commit()
		await session.close()
