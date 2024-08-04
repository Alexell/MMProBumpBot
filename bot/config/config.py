from pydantic_settings import BaseSettings, SettingsConfigDict
from bot.utils import logger


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

	API_ID: int
	API_HASH: str
	ERRORS_BEFORE_STOP: int = 3
	USE_PROXY_FROM_FILE: bool = False


try:
	settings = Settings()
except Exception as error:
	logger.error(error)
	settings = False
