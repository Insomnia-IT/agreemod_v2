import logging
import typing

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from traceback_with_variables import ColorSchemes, Format


load_dotenv()


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
    host: str = "localhost"
    user: str = "guest"
    password: str = "guest"
    web_port: int = 15672
    queue_port: int = 5672
    telegram_queue: str = "telegram"
    # link = f'amqp://guest:guest@localhost/' # TODO: make link right here


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

    notion: NotionConfig
    postgres: PostgresConfig
    rabbitmq: RabbitMQ

    ROUTER_GET_QUERY_CACHE_TIMEOUT: int = 15

    DEFAULT_ADMIN_LOGIN: str
    DEFAULT_ADMIN_PASSWORD: str

    TELEBOT_TOKEN: str = ""

    API_PREFIX: str = "/api/v1"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_nested_delimiter="__", extra="ignore"
    )

    @property
    def version(self) -> str:
        return ".".join(
            map(str, [self.MAJOR_VERSION, self.MINOR_VERSION, self.PATCH_VERSION])
        )


config = Config()

# def get_main_config():
#     return Config()


logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s [%(module)s] [%(levelname)s]: %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)

main_logger = logging.getLogger("agreemod")
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
