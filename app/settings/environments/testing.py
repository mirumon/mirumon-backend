from pydantic import AnyUrl, PostgresDsn, RedisDsn, SecretStr

from app.settings.environments.base import AppSettings


class TestAppSettings(AppSettings):
    """Application settings with override params for test environment."""

    # fastapi.applications.FastAPI initializer kwargs
    debug: bool = False

    title: str = "Test Mirumon Service"

    # Auth settings
    secret_key: SecretStr = SecretStr("test-secret-key")
    shared_key: SecretStr = SecretStr("test-shared-key")

    # Infrastructure settings
    database_dsn: PostgresDsn = "postgres://postgres:postgres@localhost/postgres"  # type: ignore
    redis_dsn: RedisDsn = "redis://redis:redis@localhost/0"  # type: ignore
    rabbit_dsn: AnyUrl = "amqp://rabbitmq:rabbitmq@localhost/"  # type: ignore

    # First superuser credentials
    first_superuser_username: str = "test-superuser-username"
    first_superuser_password: str = "test-superuser-password"

    class Config(AppSettings.Config):
        env_file = "test.env"
