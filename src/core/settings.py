from typing import Any, Final

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseModel):
    """Logging settings"""

    # OTel collector URL
    otel_url: str | None = None

    # Show SQLAlchemy logs
    show_sql: bool = False


class AppSettings(BaseModel):
    """Application settings"""

    # App startup host
    host: str = '0.0.0.0'
    # App startup port
    port: int = 8000

    # Database URL
    database_url: str

    # Allowed origins
    origins: list[str] = ['*']

    # Application mode (dev mode)
    dev_mode: bool = False

    @field_validator('origins', mode='before')
    @classmethod
    def parse_origins(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return value


class Settings(BaseSettings):
    """Project settings class"""

    app: AppSettings
    logging: LoggingSettings = LoggingSettings()

    version: str = '0.0.1'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore',
        validate_default=False,
        env_nested_delimiter='__',
    )

    @property
    def app_config(self) -> dict[str, Any]:
        return {
            'title': '[Template]',
            'docs_url': '/docs' if self.app.dev_mode else None,
            'openapi_url': '/openapi.json' if self.app.dev_mode else None,
            'version': self.version,
        }


# Singleton object
settings: Final[Settings] = Settings()  # pyright: ignore[reportCallIssue]
