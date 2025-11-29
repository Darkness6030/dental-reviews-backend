from datetime import datetime
from typing import Optional, List

import bcrypt
from rewire_sqlmodel import SQLModel
from sqlmodel import Field, Relationship


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str
    password_hash: str
    is_admin: bool = False
    telegram_id: Optional[int] = None

    def __init__(self, username: str, password: str):
        super().__init__(username=username, password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode())

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional['User']:
        return await cls.select().where(cls.id == user_id).first()

    @classmethod
    async def get_by_username(cls, username: str) -> Optional['User']:
        return await cls.select().where(cls.username == username).first()


class DoctorServiceLink(SQLModel, table=True):
    doctor_id: int = Field(foreign_key='doctor.id', primary_key=True)
    service_id: int = Field(foreign_key='service.id', primary_key=True)


class ReviewRequestDoctorLink(SQLModel, table=True):
    review_request_id: int = Field(foreign_key='reviewrequest.id', primary_key=True)
    doctor_id: int = Field(foreign_key='doctor.id', primary_key=True)


class ReviewRequestServiceLink(SQLModel, table=True):
    review_request_id: int = Field(foreign_key='reviewrequest.id', primary_key=True)
    service_id: int = Field(foreign_key='service.id', primary_key=True)


class ReviewRequestAspectLink(SQLModel, table=True):
    review_request_id: int = Field(foreign_key='reviewrequest.id', primary_key=True)
    aspect_id: int = Field(foreign_key='aspect.id', primary_key=True)


class ReviewRequestPlatformLink(SQLModel, table=True):
    review_request_id: int = Field(foreign_key='reviewrequest.id', primary_key=True)
    platform_id: str = Field(foreign_key='platform.id', primary_key=True)


class Doctor(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    specialty: str

    services: List['Service'] = Relationship(
        link_model=DoctorServiceLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    @classmethod
    async def get_by_id(cls, doctor_id: int) -> Optional['Doctor']:
        return await cls.select().where(cls.id == doctor_id).first()

    @classmethod
    async def get_by_ids(cls, doctor_ids: List[int]) -> List['Doctor']:
        return list(await cls.select().where(cls.id.in_(doctor_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Doctor']:
        return list(await cls.select().all())


class Service(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    @classmethod
    async def get_by_id(cls, service_id: int) -> Optional['Service']:
        return await cls.select().where(cls.id == service_id).first()

    @classmethod
    async def get_by_ids(cls, service_ids: List[int]) -> List['Service']:
        return list(await cls.select().where(cls.id.in_(service_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Service']:
        return list(await cls.select().all())


class Aspect(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    @classmethod
    async def get_by_id(cls, aspect_id: int) -> Optional['Aspect']:
        return await cls.select().where(cls.id == aspect_id).first()

    @classmethod
    async def get_by_ids(cls, aspect_ids: List[int]) -> List['Aspect']:
        return list(await cls.select().where(cls.id.in_(aspect_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Aspect']:
        return list(await cls.select().all())


class Platform(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    image_path: str

    @classmethod
    async def get_by_id(cls, platform_id: str) -> Optional['Platform']:
        return await cls.select().where(cls.id == platform_id).first()

    @classmethod
    async def get_all(cls) -> List['Platform']:
        return list(await cls.select().all())


class ReviewRequest(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    user_fio: Optional[str] = None
    user_phone: Optional[str] = None
    generated_text: Optional[str] = None

    selected_doctors: List[Doctor] = Relationship(
        link_model=ReviewRequestDoctorLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    selected_services: List[Service] = Relationship(
        link_model=ReviewRequestServiceLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    selected_aspects: List[Aspect] = Relationship(
        link_model=ReviewRequestAspectLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    published_platforms: List['Platform'] = Relationship(
        link_model=ReviewRequestPlatformLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    @classmethod
    async def get_by_id(cls, request_id: int) -> Optional['ReviewRequest']:
        return await cls.select().where(cls.id == request_id).first()

    @classmethod
    async def get_all(cls, date_before: Optional[datetime] = None, date_after: Optional[datetime] = None) -> List['ReviewRequest']:
        query = cls.select()
        if date_before:
            query = query.where(cls.created_at <= date_before)

        if date_after:
            query = query.where(cls.created_at >= date_after)

        return list(await query.all())
