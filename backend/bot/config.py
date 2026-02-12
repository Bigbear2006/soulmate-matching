from dataclasses import dataclass, field

from environs import env

env.read_env()


@dataclass
class Config:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))


config = Config()
