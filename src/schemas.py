from typing import List, Optional

from pydantic import BaseModel

from src.models import Complaint, Doctor, Review


class UserRequest(BaseModel):
    name: str
    username: str
    password: str
    is_admin: bool
    avatar_url: Optional[str]


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    is_admin: bool
    is_owner: bool
    avatar_url: Optional[str]


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str


class ReorderRequest(BaseModel):
    ordered_ids: List[int]


class UploadImageResponse(BaseModel):
    filename: str
    image_url: str


class DoctorRequest(BaseModel):
    name: str
    role: str
    avatar_url: Optional[str]
    is_enabled: bool
    service_ids: List[int]


class DoctorResponse(BaseModel):
    id: int
    name: str
    role: str
    avatar_url: Optional[str]
    is_enabled: bool
    services: List['ServiceResponse']


class ServiceRequest(BaseModel):
    name: str
    category: str
    is_enabled: bool


class ServiceResponse(BaseModel):
    id: int
    name: str
    category: str
    is_enabled: bool


class AspectRequest(BaseModel):
    name: str
    is_enabled: bool


class AspectResponse(BaseModel):
    id: int
    name: str
    is_enabled: bool


class SourceRequest(BaseModel):
    name: str
    is_enabled: bool


class SourceResponse(BaseModel):
    id: int
    name: str
    is_enabled: bool


class RewardRequest(BaseModel):
    name: str
    image_url: Optional[str]
    is_enabled: bool


class RewardResponse(BaseModel):
    id: int
    name: str
    image_url: Optional[str]
    is_enabled: bool


class PlatformRequest(BaseModel):
    name: str
    url: str
    image_url: Optional[str]
    is_enabled: bool


class PlatformResponse(BaseModel):
    id: int
    name: str
    url: str
    image_url: Optional[str]
    is_enabled: bool


class ReasonRequest(BaseModel):
    name: str
    is_enabled: bool


class ReasonResponse(BaseModel):
    id: int
    name: str
    is_enabled: bool


class PromptRequest(BaseModel):
    id: str
    prompt_text: str
    temperature: float
    frequency_penalty: float


class PromptResponse(BaseModel):
    id: str
    prompt_text: str
    temperature: float
    frequency_penalty: float


class PromptTestResponse(BaseModel):
    generated_text: str


class ReviewDoctorsRequest(BaseModel):
    doctor_ids: List[int]


class ReviewServicesRequest(BaseModel):
    service_ids: List[int]


class ReviewAspectsRequest(BaseModel):
    aspect_ids: List[int]


class ReviewSourceRequest(BaseModel):
    source_id: int


class ReviewContactsRequest(BaseModel):
    contact_name: Optional[str]
    contact_phone: Optional[str]


class ReviewTextRequest(BaseModel):
    review_text: str


class ReviewRewardRequest(BaseModel):
    reward_id: int


class CreateReviewResponse(BaseModel):
    id: int


class ReviewResponse(BaseModel):
    id: int
    contact_name: Optional[str]
    contact_phone: Optional[str]
    review_text: Optional[str]
    selected_doctors: List[DoctorResponse]
    selected_services: List[ServiceResponse]
    selected_aspects: List[AspectResponse]
    selected_source: Optional[SourceResponse]
    selected_reward: Optional[RewardResponse]
    published_platforms: List[PlatformResponse]


class CreateComplaintRequest(BaseModel):
    contact_name: str
    contact_phone: str
    complaint_text: str
    reason_ids: List[int]


class CreateComplaintResponse(BaseModel):
    id: int


class ComplaintResponse(BaseModel):
    id: int
    contact_name: Optional[str]
    contact_phone: Optional[str]
    complaint_text: Optional[str]
    selected_reasons: List[ReasonResponse]


class ReviewsDashboardResponse(BaseModel):
    reviews: List['ReviewResponse']
    complaints: List['ComplaintResponse']


def create_doctor_response(doctor: Doctor) -> DoctorResponse:
    return DoctorResponse(
        **doctor.model_dump(),
        services=[ServiceResponse(**service.model_dump()) for service in doctor.services]
    )


def create_review_response(review: Review) -> ReviewResponse:
    return ReviewResponse(
        id=review.id,
        contact_name=review.contact_name,
        contact_phone=review.contact_phone,
        review_text=review.review_text,
        selected_doctors=[
            create_doctor_response(doctor)
            for doctor in review.selected_doctors
        ],
        selected_services=[
            ServiceResponse(**service.model_dump())
            for service in review.selected_services
        ],
        selected_aspects=[
            AspectResponse(**aspect.model_dump())
            for aspect in review.selected_aspects
        ],
        selected_source=(
            SourceResponse(**review.selected_source.model_dump())
            if review.selected_source else None
        ),
        selected_reward=(
            RewardResponse(**review.selected_reward.model_dump())
            if review.selected_reward else None
        ),
        published_platforms=[
            PlatformResponse(**platform.model_dump())
            for platform in review.published_platforms
        ]
    )


def create_complaint_response(complaint: Complaint) -> ComplaintResponse:
    return ComplaintResponse(
        id=complaint.id,
        contact_name=complaint.contact_name,
        contact_phone=complaint.contact_phone,
        complaint_text=complaint.complaint_text,
        selected_reasons=[
            ReasonResponse(**reason.model_dump())
            for reason in complaint.selected_reasons
        ]
    )
