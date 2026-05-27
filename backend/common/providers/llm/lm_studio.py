import os
from typing import TypedDict

from common.providers.base_api_provider import BaseApiProvider


class LlmInfo(TypedDict):
	key: str
	capabilities: dict[str, bool]
	loaded_instances: list[dict]


class LMStudioProvider(BaseApiProvider):
	base_url = os.getenv('LM_STUDIO_BASE_URL')
	timeout = 60 * 10

	def __init__(self):
		self._use_model: str | None = None

	def get_models(self) -> list[LlmInfo]:
		response = self.get('/api/v1/models')
		return response['models']

	def send_prompt(self, prompt: str, use_model: str | None = None):
		if not self._use_model:
			for _model in self.get_models():
				if _model['loaded_instances']:
					self._use_model = _model['key']
					break

		if not use_model:
			use_model = self._use_model

		response = self.post(
			endpoint_url='/api/v1/chat',
			payload={
				'input': prompt,
				'model': use_model,
			},
		)

		for result in response['output']:
			if result['type'] == 'message':
				return result['content']

		return None
