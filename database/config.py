import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from traceback_with_variables import ColorSchemes, Format

logger = logging.getLogger(__name__)


class PostgresConfig(BaseSettings):
    host: str
    port: str
    user: str
    password: str
    name: str
    MIN_POOL_SIZE: int = 5
    MAX_POOL_SIZE: int = 10

    model_config = SettingsConfigDict(extra="ignore")


class Config(BaseSettings):
    TESTING: bool = False
    DEBUG: bool = True
    postgres: PostgresConfig

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, env_nested_delimiter="__", extra="ignore"
    )


config = Config()
# def get_main_config():
#     return Config()


logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s [%(module)s] [%(levelname)s]: %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)

logger = logging.getLogger("agreemod")
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
