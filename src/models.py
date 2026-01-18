from datetime import datetime
from typing import List, Optional

import bcrypt
from rewire_sqlmodel import SQLModel
from sqlmodel import Field, Relationship


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    username: str
    password_hash: str
    is_admin: bool = False
    telegram_id: Optional[int] = None

    def __init__(self, username: str, password: str):
        super().__init__(
            username=username,
            password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        )

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional['User']:
        return await cls.select().filter_by(id=user_id).first()

    @classmethod
    async def get_by_username(cls, username: str) -> Optional['User']:
        return await cls.select().filter_by(username=username).first()


class DoctorServiceLink(SQLModel, table=True):
    doctor_id: int = Field(foreign_key='doctor.id', primary_key=True)
    service_id: int = Field(foreign_key='service.id', primary_key=True)


class ReviewDoctorLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True)
    doctor_id: int = Field(foreign_key='doctor.id', primary_key=True)


class ReviewServiceLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True)
    service_id: int = Field(foreign_key='service.id', primary_key=True)


class ReviewAspectLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True)
    aspect_id: int = Field(foreign_key='aspect.id', primary_key=True)


class ReviewSourceLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True)
    source_id: int = Field(foreign_key='source.id', primary_key=True)


class ReviewRewardLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True)
    reward_id: int = Field(foreign_key='reward.id', primary_key=True)


class ReviewPlatformLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True)
    platform_id: int = Field(foreign_key='platform.id', primary_key=True)


class ComplaintReasonLink(SQLModel, table=True):
    complaint_id: int = Field(foreign_key='complaint.id', primary_key=True)
    reason_id: int = Field(foreign_key='reason.id', primary_key=True)


class Doctor(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    role: str
    avatar_url: Optional[str] = None

    services: List['Service'] = Relationship(
        link_model=DoctorServiceLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    @classmethod
    async def get_by_id(cls, doctor_id: int) -> Optional['Doctor']:
        return await cls.select().filter_by(id=doctor_id).first()

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
        return await cls.select().filter_by(id=service_id).first()

    @classmethod
    async def get_by_ids(cls, service_ids: List[int]) -> List['Service']:
        return list(await cls.select().where(cls.id.in_(service_ids)).all())

    @classmethod
    async def get_by_doctor_ids(cls, doctor_ids: List[int]) -> List['Service']:
        query = (
            cls.select()
            .join(DoctorServiceLink, DoctorServiceLink.service_id == cls.id)  # type: ignore
            .where(DoctorServiceLink.doctor_id.in_(doctor_ids))
            .distinct()
        )

        return list(await query.all())

    @classmethod
    async def get_all(cls) -> List['Service']:
        return list(await cls.select().all())


class Aspect(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    @classmethod
    async def get_by_id(cls, aspect_id: int) -> Optional['Aspect']:
        return await cls.select().filter_by(id=aspect_id).first()

    @classmethod
    async def get_by_ids(cls, aspect_ids: List[int]) -> List['Aspect']:
        return list(await cls.select().where(cls.id.in_(aspect_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Aspect']:
        return list(await cls.select().all())


class Source(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    @classmethod
    async def get_by_id(cls, source_id: int) -> Optional['Source']:
        return await cls.select().filter_by(id=source_id).first()

    @classmethod
    async def get_by_ids(cls, source_ids: List[int]) -> List['Source']:
        return list(await cls.select().where(cls.id.in_(source_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Source']:
        return list(await cls.select().all())


class Reward(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    image_url: Optional[str] = None

    @classmethod
    async def get_by_id(cls, reward_id: int) -> Optional['Reward']:
        return await cls.select().filter_by(id=reward_id).first()

    @classmethod
    async def get_by_ids(cls, reward_ids: List[int]) -> List['Reward']:
        return list(await cls.select().where(cls.id.in_(reward_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Reward']:
        return list(await cls.select().all())


class Platform(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    url: str
    image_url: Optional[str] = None

    @classmethod
    async def get_by_id(cls, platform_id: int) -> Optional['Platform']:
        return await cls.select().filter_by(id=platform_id).first()

    @classmethod
    async def get_by_ids(cls, platform_ids: List[int]) -> List['Platform']:
        return list(await cls.select().where(cls.id.in_(platform_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Platform']:
        return list(await cls.select().all())


class Reason(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

    @classmethod
    async def get_by_id(cls, reason_id: int) -> Optional['Reason']:
        return await cls.select().filter_by(id=reason_id).first()

    @classmethod
    async def get_by_ids(cls, reason_ids: List[int]) -> List['Reason']:
        return list(await cls.select().where(cls.id.in_(reason_ids)).all())

    @classmethod
    async def get_all(cls) -> List['Reason']:
        return list(await cls.select().all())


class Owner(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    avatar_url: Optional[str] = None

    @classmethod
    async def get(cls) -> Optional['Owner']:
        return await cls.select().first()


class Review(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    review_text: Optional[str] = None

    selected_doctors: List[Doctor] = Relationship(
        link_model=ReviewDoctorLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    selected_services: List[Service] = Relationship(
        link_model=ReviewServiceLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    selected_aspects: List[Aspect] = Relationship(
        link_model=ReviewAspectLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    selected_source: Optional[Source] = Relationship(
        link_model=ReviewSourceLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    selected_reward: Optional[Reward] = Relationship(
        link_model=ReviewRewardLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    published_platforms: List[Platform] = Relationship(
        link_model=ReviewPlatformLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    @classmethod
    async def get_by_id(cls, review_id: int) -> Optional['Review']:
        return await cls.select().filter_by(id=review_id).first()

    @classmethod
    async def get_all(cls, date_after: Optional[datetime] = None, date_before: Optional[datetime] = None) -> List['Review']:
        query = cls.select()
        if date_after:
            query = query.where(cls.created_at >= date_after)

        if date_before:
            query = query.where(cls.created_at <= date_before)

        return list(await query.all())


class Complaint(SQLModel, table=True):
    id: int = Field(primary_key=True, default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    complaint_text: Optional[str] = None

    selected_reasons: List[Reason] = Relationship(
        link_model=ComplaintReasonLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    @classmethod
    async def get_by_id(cls, complaint_id: int) -> Optional['Complaint']:
        return await cls.select().filter_by(id=complaint_id).first()

    @classmethod
    async def get_all(cls, date_after: Optional[datetime] = None, date_before: Optional[datetime] = None) -> List['Complaint']:
        query = cls.select()
        if date_after:
            query = query.where(cls.created_at >= date_after)

        if date_before:
            query = query.where(cls.created_at <= date_before)

        return list(await query.all())
