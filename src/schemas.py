from typing import List, Optional

from pydantic import BaseModel

from src.models import ReviewRequest, Doctor


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str


class UserResponse(BaseModel):
    username: str
    is_admin: bool


class DoctorRequest(BaseModel):
    name: str
    specialty: str
    service_ids: List[int]


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialty: str
    services: List['ServiceResponse']


class ServiceRequest(BaseModel):
    name: str


class ServiceResponse(BaseModel):
    id: int
    name: str


class AspectRequest(BaseModel):
    name: str


class AspectResponse(BaseModel):
    id: int
    name: str


class PlatformResponse(BaseModel):
    id: str
    name: str
    image_path: str


class ReviewsDashboardResponse(BaseModel):
    total_requests: int
    total_generated: int
    total_published: int
    reviews: List['ReviewResponse']


class ReviewCreateRequest(BaseModel):
    user_fio: str
    user_phone: str


class ReviewDoctorsRequest(BaseModel):
    doctor_ids: List[int]


class ReviewServicesRequest(BaseModel):
    service_ids: List[int]


class ReviewAspectsRequest(BaseModel):
    aspect_ids: List[int]


class ReviewResponse(BaseModel):
    id: int
    user_fio: Optional[str]
    user_phone: Optional[str]
    created_at: str
    selected_doctors: List['DoctorResponse']
    selected_services: List['ServiceResponse']
    selected_aspects: List['AspectResponse']
    published_platforms: List['PlatformResponse']
    generated_text: Optional[str]


def create_doctor_response(doctor: Doctor) -> DoctorResponse:
    return DoctorResponse(
        **doctor.model_dump(),
        services=[ServiceResponse(**service.model_dump()) for service in doctor.services]
    )


def create_review_response(review_request: ReviewRequest) -> ReviewResponse:
    return ReviewResponse(
        id=review_request.id,
        created_at=review_request.created_at.isoformat(),
        user_fio=review_request.user_fio,
        user_phone=review_request.user_phone,
        generated_text=review_request.generated_text,
        selected_doctors=[create_doctor_response(doctor) for doctor in review_request.selected_doctors],
        selected_services=[ServiceResponse(**service.model_dump()) for service in review_request.selected_services],
        selected_aspects=[AspectResponse(**aspect.model_dump()) for aspect in review_request.selected_aspects],
        published_platforms=[PlatformResponse(**platform.model_dump()) for platform in review_request.published_platforms]
    )
