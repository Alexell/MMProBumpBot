from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

	API_ID: int
	API_HASH: str
	ERRORS_BEFORE_STOP: int = 3
	USE_PROXY_FROM_FILE: bool = False


settings = Settings()
