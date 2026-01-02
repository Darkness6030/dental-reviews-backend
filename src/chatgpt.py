from typing import List

from openai import AsyncOpenAI
from pydantic import BaseModel
from rewire import config

from src.models import Aspect, Doctor, Service


@config
class Config(BaseModel):
    api_key: str
    base_url: str


CLIENT = AsyncOpenAI(api_key=Config.api_key, base_url=Config.base_url)


async def generate_review_text(doctors: List[Doctor], services: List[Service], aspects: List[Aspect]) -> str:  # TODO
    return 'Текст отзыва...'
