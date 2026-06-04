"""Бизнес-логика аутентификации и регистрации пользователей.

Сервис не знает про HTTP: ``authenticate``/``login`` возвращают ``User``/``Token``
или ``None`` (единый сигнал «не аутентифицирован»), а ``register`` создаёт
пользователя в транзакции. Преобразование ``None`` → ``404/401`` — задача
слоя эндпоинтов.
"""

from uuid import UUID

from apps.accounts.api.schemas.mutators import RegistrationDataForm
from apps.accounts.models.user import User
from apps.accounts.models.user_session import UserSession
from apps.accounts.repositories.user import UserRepository
from core.db import database
from core.safety.token import (
	Token,
	create_access_token,
	decode_token_claims,
	get_password_hash,
	verify_password,
)


class AuthService:
	"""Аутентификация, выпуск токена/сессии и регистрация пользователей."""

	async def authenticate(self, identifier: str, password: str) -> User | None:
		"""
		Аутентифицировать пользователя по login/email + паролю.

		Возвращает ``User`` при успехе или ``None`` в ЛЮБОМ случае неуспеха
		(пользователь не найден ИЛИ пароль неверен). Единый сигнал важен и для
		единообразного HTTP-ответа, и для защиты от user-enumeration.
		"""
		user = await UserRepository().get_active_by_login_or_email(identifier)
		if user is None:
			return None

		if not verify_password(password, user.password_hash):
			return None

		return user

	async def login(self, identifier: str, password: str) -> Token | None:
		"""
		Аутентифицировать пользователя и выпустить access-токен + сессию.

		:returns: ``Token`` при успехе; ``None``, если аутентификация не прошла.
		"""
		user = await self.authenticate(identifier, password)
		if user is None:
			return None

		access_token = create_access_token(data={'sub': str(user.id)})
		token_jti, expires_at = decode_token_claims(access_token)
		session_record = UserSession(user_id=user.id, token_jti=token_jti, expires_at=expires_at)

		async with database.get_async_session() as session:
			session.add(session_record)
			await session.commit()

		return Token(access_token=access_token, token_type='bearer')

	async def logout(self, user_id: UUID) -> None:
		"""Завершить все сессии пользователя (удалить записи ``UserSession``)."""
		await database.execute(UserSession.__table__.delete().where(UserSession.user_id == user_id))

	async def register(self, data: RegistrationDataForm) -> User:
		"""
		Создать пользователя (с хешированием пароля) в транзакции.

		:returns: созданный ``User``.
		"""
		user = User(login=data.login, email=data.email, password_hash=get_password_hash(data.password))

		async with database.get_async_session() as session:
			session.add(user)
			await session.commit()
			await session.refresh(user)

		return user
