from typing import List

from openai import AsyncOpenAI
from pydantic import BaseModel
from rewire import config


@config
class Config(BaseModel):
    api_key: str
    base_url: str


CLIENT = AsyncOpenAI(api_key=Config.api_key, base_url=Config.base_url)


async def generate_review_text(doctor_names: List[str], service_names: List[str], aspect_names: List[str]) -> str:  # TODO
    return f'{doctor_names}\n\n{service_names}\n\n{aspect_names}'  # TODO
