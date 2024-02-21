import logging
import typing

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from traceback_with_variables import ColorSchemes, Format


class NotionConfig(BaseModel):
    token: str = Field(alias="token")


class RedisConfig(BaseModel):
    host: str
    port: int
    password: str


class PostgresConfig(BaseModel):
    host: str
    port: str
    user: str
    password: str
    name: str


class Config(BaseSettings):
    NOTION_DBS_INFO: str = "notion_dbs_info.json"
    DEBUG: bool = False
    REFRESH_PERIOD: int = 120  # seconds

    notion: NotionConfig
    postgres: PostgresConfig
    redis: RedisConfig

    class Config:
        env_file = ".env"
        case_insensitive = True
        env_nested_delimiter = "__"


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
