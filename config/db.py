from databases import Database
from sqlalchemy import MetaData

from config.settings import settings


DATABASE_URL = settings.db.url
metadata = MetaData()
database = Database(DATABASE_URL)
