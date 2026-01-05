from typing import List, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel
from rewire import config

from src.models import Aspect, Doctor, Service, Source


@config
class Config(BaseModel):
    api_key: str
    base_url: str
    project: str


CLIENT = AsyncOpenAI(
    api_key=Config.api_key,
    base_url=Config.base_url,
    project=Config.project
)

LLM_MODEL = f'gpt://{Config.project}/yandexgpt/latest'
LLM_TEMPERATURE = 0.8

REVIEW_SYSTEM_PROMPT = '''
Ты — реальный пациент, который пишет отзыв о посещении медицинской клиники на публичной платформе (например, Яндекс Карты или ПроДокторов).

Задача:
Напиши искренний, живой и правдоподобный текст отзыва от первого лица.

Требования к стилю:
- Разговорный, человеческий язык
- Без канцелярита, рекламных слоганов и шаблонных фраз
- Допустимы эмоции, личные впечатления, эмодзи
- Текст должен выглядеть как написанный обычным человеком, а не маркетологом

Структура отзыва:
1. Короткое вступление с общим впечатлением
2. Описание визита и взаимодействия с врачами и персоналом
3. Подробности по услугам и тому, что особенно понравилось
4. Итоговое впечатление и готовность рекомендовать клинику

Ограничения:
- Не используй слово «клиника» чаще 2 раз
- Не перечисляй аспекты списком — вписывай их в текст естественно
- Не упоминай, что текст был сгенерирован
- Объём: 1–3 абзаца

Напиши только текст отзыва, без заголовков и пояснений.
'''

REVIEW_USER_PROMPT = '''
Контекст визита:
- Врачи, у которых был приём: {doctors}
- Полученные услуги: {services}
- Что особенно понравилось во время визита: {aspects}
- Откуда узнал(а) о клинике: {source}
'''


def format_doctors(doctors: List[Doctor]) -> str:
    return ', '.join(
        f'{doctor.role} {doctor.name}' if doctor.role else doctor.name
        for doctor in doctors
    )


def format_services(services: List[Service]) -> str:
    return ', '.join(service.name for service in services)


def format_aspects(aspects: List[Aspect]) -> str:
    return ', '.join(aspect.name for aspect in aspects)


async def generate_review_text(
        doctors: List[Doctor],
        services: List[Service],
        aspects: List[Aspect],
        source: Optional[Source]
) -> str:
    user_prompt = REVIEW_USER_PROMPT.format(
        doctors=format_doctors(doctors) if doctors else 'не указаны',
        services=format_services(services) if services else 'не указаны',
        aspects=format_aspects(aspects) if aspects else 'не указано',
        source=source.name if source else 'не указано'
    )

    response = await CLIENT.chat.completions.create(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        messages=[
            {
                'role': 'system',
                'content': REVIEW_SYSTEM_PROMPT
            },
            {
                'role': 'user',
                'content': user_prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()
