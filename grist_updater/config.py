import logging
import typing
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from traceback_with_variables import ColorSchemes, Format


load_dotenv()

def setup_logging(logger_name: str) -> logging.Logger:
    debug_enabled = os.getenv("DEBUG", "False") == "True"
    level = logging.DEBUG if debug_enabled else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(module)s] [%(levelname)s]: %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )

    if os.getenv("LOG_STDOUT_ENABLED", "True") == "True":
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(formatter)
        root.addHandler(stdout_handler)

    if os.getenv("LOG_FILE_ENABLED", "True") == "True":
        log_dir = Path(os.getenv("LOG_DIR", "/var/log/agreemod"))
        log_file_name = os.getenv("LOG_FILE_NAME", "agreemod.log")
        max_bytes = int(os.getenv("LOG_MAX_BYTES", "10485760"))
        backup_count = int(os.getenv("LOG_BACKUP_COUNT", "10"))

        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_dir / log_file_name,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    return logging.getLogger(logger_name)

class CodaConfig(BaseSettings):
    api_key: str
    doc_id: str

    model_config = SettingsConfigDict(extra="ignore")

class GristConfig(BaseSettings):
    server: str
    doc_id: str
    api_key: str


class NotionConfig(BaseModel):
    token: str = Field(alias="token")
    write_token: str = Field(alias="write_token")


class PostgresConfig(BaseModel):
    host: str
    port: str
    user: str
    password: str
    name: str
    MIN_POOL_SIZE: int = 5
    MAX_POOL_SIZE: int = 10


class RabbitMQ(BaseModel):
    host: str = "rabbitmq"
    user: str = "guest"
    password: str = "guest"
    web_port: int = 15672
    queue_port: int = 5672
    telegram_queue: str = "telegram"
    # link = f'amqp://guest:guest@localhost/' # TODO: make link right here

    @property
    def url(self) -> str:
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.queue_port}/"


class Config(BaseSettings):
    TITLE: str = "Notion API & Integrations"
    DESCRIPTION: str = ""

    DEBUG: bool = False
    TESTING: bool = False

    MAJOR_VERSION: int = 0
    MINOR_VERSION: int = 1
    PATCH_VERSION: int = 7

    cors_origins: typing.Sequence[str] = ()
    cors_origin_regex: typing.Optional[str] = None
    cors_methods: typing.Sequence[str] = ("GET",)
    cors_headers: typing.Sequence[str] = ()

    allowed_hosts: typing.Sequence[str] | None = None

    SMTP_LOG_ENABLED: bool = False
    SMTP_LOG_HOST: str = ""
    SMTP_LOG_PORT: str = ""
    SMTP_LOG_FROM: str = ""
    SMTP_LOG_TO: str = ""
    SMTP_LOG_SUBJECT: str = ""
    SMTP_LOG_USER: str = ""
    SMTP_LOG_PASSWORD: str = ""
    SMTP_LOG_TIMEOUT: str = ""

    coda: CodaConfig
    notion: NotionConfig
    postgres: PostgresConfig
    rabbitmq: RabbitMQ
    grist: GristConfig

    ROUTER_GET_QUERY_CACHE_TIMEOUT: int = 15

    DEFAULT_ADMIN_LOGIN: str
    DEFAULT_ADMIN_PASSWORD: str

    TELEBOT_TOKEN: str = ""

    API_PREFIX: str = "/api/v1"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    API_AUTH_USER: str
    API_AUTH_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, env_nested_delimiter="__", extra="ignore")

    @property
    def version(self) -> str:
        return ".".join(map(str, [self.MAJOR_VERSION, self.MINOR_VERSION, self.PATCH_VERSION]))


config = Config()

# def get_main_config():
#     return Config()


main_logger = setup_logging("grist_updater")
# std_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(std_handler)


traceback_format = Format(
    before=3,
    after=1,
    max_value_str_len=10000,
    max_exc_str_len=1000,
    color_scheme=ColorSchemes.common,
    skip_files_except=[],
    brief_files_except=[],
    custom_var_printers=[
        ("password", lambda v: "...hidden..."),
        ("pswd", lambda v: "...hidden..."),
        (list, lambda v: f"list{v}"),
    ],
)
