from datetime import datetime, time
from typing import List, Optional, Self

import bcrypt
from rewire_sqlmodel import session_context, SQLModel
from sqlalchemy import update
from sqlmodel import case, desc, Field, Relationship


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    username: str
    password_hash: str
    is_admin: bool = False
    is_owner: bool = False
    avatar_url: Optional[str] = None
    max_id: Optional[int] = None
    max_name: Optional[str] = None
    telegram_id: Optional[int] = None
    telegram_name: Optional[str] = None

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    @classmethod
    async def get_by_id(cls, user_id: int) -> Optional[Self]:
        return await cls.select().filter_by(id=user_id).first()

    @classmethod
    async def get_by_username(cls, username: str) -> Optional[Self]:
        return await cls.select().filter_by(username=username).first()

    @classmethod
    async def get_owner(cls) -> Optional[Self]:
        return await cls.select().filter_by(is_owner=True).first()

    @classmethod
    async def get_all(cls) -> List[Self]:
        return list(await cls.select().order_by(desc(cls.is_owner)).all())


class DoctorServiceLink(SQLModel, table=True):
    doctor_id: int = Field(foreign_key='doctor.id', primary_key=True, ondelete='CASCADE')
    service_id: int = Field(foreign_key='service.id', primary_key=True, ondelete='CASCADE')


class ReviewDoctorLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True, ondelete='CASCADE')
    doctor_id: int = Field(foreign_key='doctor.id', primary_key=True, ondelete='CASCADE')


class ReviewServiceLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True, ondelete='CASCADE')
    service_id: int = Field(foreign_key='service.id', primary_key=True, ondelete='CASCADE')


class ReviewAspectLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True, ondelete='CASCADE')
    aspect_id: int = Field(foreign_key='aspect.id', primary_key=True, ondelete='CASCADE')


class ReviewSourceLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True, ondelete='CASCADE')
    source_id: int = Field(foreign_key='source.id', primary_key=True, ondelete='CASCADE')


class ReviewRewardLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True, ondelete='CASCADE')
    reward_id: int = Field(foreign_key='reward.id', primary_key=True, ondelete='CASCADE')


class ReviewPlatformLink(SQLModel, table=True):
    review_id: int = Field(foreign_key='review.id', primary_key=True, ondelete='CASCADE')
    platform_id: int = Field(foreign_key='platform.id', primary_key=True, ondelete='CASCADE')


class ComplaintReasonLink(SQLModel, table=True):
    complaint_id: int = Field(foreign_key='complaint.id', primary_key=True, ondelete='CASCADE')
    reason_id: int = Field(foreign_key='reason.id', primary_key=True, ondelete='CASCADE')


class ItemModel(SQLModel, table=False):
    id: int = Field(primary_key=True)
    position: int = Field(default=0, index=True)
    is_enabled: bool = False

    @classmethod
    async def get_by_id(cls, item_id: int) -> Optional[Self]:
        return await cls.select().filter_by(id=item_id).first()

    @classmethod
    async def get_by_ids(cls, item_ids: List[int]) -> List[Self]:
        return list(await cls.select().where(cls.id.in_(item_ids)).all())

    @classmethod
    async def get_all(cls) -> List[Self]:
        return list(await cls.select().order_by(cls.position).all())

    @classmethod
    async def reorder(cls, ordered_ids: List[int]):
        position_case = case(
            {item_id: index for index, item_id in enumerate(ordered_ids)},
            value=cls.id
        )

        await session_context.get().exec(
            update(cls)
            .where(cls.id.in_(ordered_ids))
            .values(position=position_case)
        )


class Doctor(ItemModel, table=True):
    name: str
    role: str
    avatar_url: Optional[str] = None

    services: List['Service'] = Relationship(
        link_model=DoctorServiceLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )


class Service(ItemModel, table=True):
    name: str
    category: str

    @classmethod
    async def get_by_doctor_ids(cls, doctor_ids: List[int]) -> List[Self]:
        query = (
            cls.select()
            .join(DoctorServiceLink, DoctorServiceLink.service_id == cls.id)  # type: ignore
            .where(DoctorServiceLink.doctor_id.in_(doctor_ids))
            .distinct()
        )

        return list(await query.order_by(cls.position).all())


class Aspect(ItemModel, table=True):
    name: str


class Source(ItemModel, table=True):
    name: str


class Reward(ItemModel, table=True):
    name: str
    image_url: Optional[str] = None


class Platform(ItemModel, table=True):
    name: str
    url: str
    image_url: Optional[str] = None


class Reason(ItemModel, table=True):
    name: str


class Prompt(SQLModel, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

    prompt_text: str
    temperature: float
    frequency_penalty: float

    @classmethod
    async def get_by_id(cls, prompt_id: str) -> Optional[Self]:
        return await cls.select().filter_by(id=prompt_id).first()

    @classmethod
    async def get_all(cls) -> List[Self]:
        return list(await cls.select().order_by(cls.created_at).all())


class Review(SQLModel, table=True):
    id: int = Field(primary_key=True)
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
    async def get_by_id(cls, review_id: int) -> Optional[Self]:
        return await cls.select().filter_by(id=review_id).first()

    @classmethod
    async def get_all(cls, date_after: Optional[datetime] = None, date_before: Optional[datetime] = None) -> List[Self]:
        query = cls.select()
        if date_after:
            date_after = datetime.combine(date_after, time.min)
            query = query.where(cls.created_at >= date_after)

        if date_before:
            date_before = datetime.combine(date_before, time.max)
            query = query.where(cls.created_at <= date_before)

        return list(await query.order_by(cls.created_at).all())


class Complaint(SQLModel, table=True):
    id: int = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    complaint_text: Optional[str] = None

    selected_reasons: List[Reason] = Relationship(
        link_model=ComplaintReasonLink,
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    @classmethod
    async def get_by_id(cls, complaint_id: int) -> Optional[Self]:
        return await cls.select().filter_by(id=complaint_id).first()

    @classmethod
    async def get_all(cls, date_after: Optional[datetime] = None, date_before: Optional[datetime] = None) -> List[Self]:
        query = cls.select()
        if date_after:
            date_after = datetime.combine(date_after, time.min)
            query = query.where(cls.created_at >= date_after)

        if date_before:
            date_before = datetime.combine(date_before, time.max)
            query = query.where(cls.created_at <= date_before)

        return list(await query.order_by(cls.created_at).all())
