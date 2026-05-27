from pydantic import Field, ValidationError, model_validator

from common.schemas.models import FrozenModelType


class RegistrationDataForm(FrozenModelType):
	login: str = Field(..., min_length=1, max_length=50)
	email: str  # TODO: email validation
	password: str
	confirm_password: str

	@model_validator(mode='after')
	def validate_passwords(self) -> 'RegistrationDataForm':
		if self.password != self.confirm_password:
			raise ValidationError('Passwords do not match')
		return self
