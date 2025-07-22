from pydantic import Field, model_validator, ValidationError

from core.schema import FrozenModelType


class RegistrationData(FrozenModelType):
    login: str = Field(..., min_length=1, max_length=50)
    email: str  # TODO: email validation
    password: str
    confirm_password: str

    @model_validator(mode='after')
    def validate_passwords(self) -> 'RegistrationData':
        if self.password != self.confirm_password:
            raise ValidationError('Passwords do not match')
        return self
