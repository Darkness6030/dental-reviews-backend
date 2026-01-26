from typing import List, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel
from rewire import config

from src.models import Aspect, Doctor, Prompt, Service, Source


@config
class Config(BaseModel):
    api_key: str
    base_url: str
    project: str
    temperature: float = 0.8


CLIENT = AsyncOpenAI(
    api_key=Config.api_key,
    base_url=Config.base_url,
    project=Config.project
)

REVIEWS_USER_PROMPT = '''
Контекст визита:
{doctors_text}
- Что особенно понравилось во время визита: {aspects_text}
- Откуда узнал(а) о клинике: {source_text}
'''


def format_doctors_text(doctors: List[Doctor], services: List[Service]) -> str:
    if not doctors:
        return '- Врачи, у которых был приём: не указаны'

    service_ids = {
        service.id
        for service in services
    }

    doctor_lines = ['- Врачи, у которых был приём:']
    for doctor in doctors:
        doctor_title = f'{doctor.role} {doctor.name}'
        doctor_services = [
            service.name for service in doctor.services
            if service.id in service_ids
        ]

        services_text = ', '.join(doctor_services) if doctor_services else 'не указаны'
        doctor_lines.append(f'{doctor_title}:\nУслуги: {services_text}')

    return '\n'.join(doctor_lines)


def build_review_user_prompt(
    doctors: List[Doctor],
    services: List[Service],
    aspects: List[Aspect],
    source: Optional[Source]
) -> str:
    aspects_text = ', '.join(aspect.name for aspect in aspects) if aspects else 'не указано'
    source_text = source.name if source else 'не указано'

    return REVIEWS_USER_PROMPT.format(
        doctors_block=format_doctors_text(doctors, services),
        aspects_text=aspects_text,
        source_text=source_text
    )


async def generate_review_text(
    reviews_prompt: Prompt,
    doctors: List[Doctor],
    services: List[Service],
    aspects: List[Aspect],
    source: Optional[Source]
) -> str:
    user_prompt = build_review_user_prompt(
        doctors=doctors,
        services=services,
        aspects=aspects,
        source=source
    )

    response = await CLIENT.chat.completions.create(
        model=f'gpt://{Config.project}/yandexgpt/latest',
        temperature=reviews_prompt.temperature,
        messages=[
            {'role': 'system', 'content': reviews_prompt.prompt_text},
            {'role': 'user', 'content': user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()
