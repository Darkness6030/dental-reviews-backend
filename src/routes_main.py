import os
from datetime import datetime
from io import BytesIO
from typing import List, Optional

from aiogram.utils.deep_linking import create_start_link
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from rewire import simple_plugin
from rewire_sqlmodel import transaction
from starlette.responses import FileResponse, StreamingResponse

from src import auth
from src.auth import user_required
from src.bot import get_bot
from src.models import Aspect, Complaint, Doctor, Platform, Reason, Review, Reward, Service, Source, User
from src.schemas import AspectResponse, create_complaint_response, create_doctor_response, create_review_response, DoctorResponse, LinkTelegramResponse, LoginRequest, LoginResponse, PlatformResponse, ReasonResponse, ReviewsDashboardResponse, RewardResponse, ServiceResponse, SourceResponse, UserResponse
from src.utils import export_rows_to_excel

plugin = simple_plugin()
router = APIRouter(prefix='/api', tags=['Main'])


@router.get('/user', response_model=UserResponse)
@transaction(1)
async def get_user(user: User = Depends(user_required)) -> UserResponse:
    return UserResponse(**user.model_dump())


@router.post('/login', response_model=LoginResponse)
@transaction(1)
async def login(request: LoginRequest) -> LoginResponse:
    user = await User.get_by_username(request.username)
    if not user or not user.check_password(request.password):
        raise HTTPException(401, 'Invalid username or password!')

    return LoginResponse(
        user=UserResponse(**user.model_dump()),
        access_token=auth.generate_access_token(user.id)
    )


@router.get('/doctors', response_model=List[DoctorResponse])
@transaction(1)
async def get_doctors() -> List[DoctorResponse]:
    return [
        create_doctor_response(doctor)
        for doctor in await Doctor.get_all()
    ]


@router.get('/services', response_model=List[ServiceResponse])
@transaction(1)
async def get_services() -> List[ServiceResponse]:
    return [
        ServiceResponse(**service.model_dump())
        for service in await Service.get_all()
    ]


@router.get('/services/doctors', response_model=List[ServiceResponse])
@transaction(1)
async def get_services_by_doctor_ids(doctor_ids: List[int] = Query(...)) -> List[ServiceResponse]:
    return [
        ServiceResponse(**service.model_dump())
        for service in await Service.get_by_doctor_ids(doctor_ids)
    ]


@router.get('/aspects', response_model=List[AspectResponse])
@transaction(1)
async def get_aspects() -> List[AspectResponse]:
    return [
        AspectResponse(**aspect.model_dump())
        for aspect in await Aspect.get_all()
    ]


@router.get('/sources', response_model=List[SourceResponse])
@transaction(1)
async def get_sources() -> List[SourceResponse]:
    return [
        SourceResponse(**source.model_dump())
        for source in await Source.get_all()
    ]


@router.get('/rewards', response_model=List[RewardResponse])
@transaction(1)
async def get_rewards() -> List[RewardResponse]:
    return [
        RewardResponse(**reward.model_dump())
        for reward in await Reward.get_all()
    ]


@router.get('/platforms', response_model=List[PlatformResponse])
@transaction(1)
async def get_platforms() -> List[PlatformResponse]:
    return [
        PlatformResponse(**platform.model_dump())
        for platform in await Platform.get_all()
    ]


@router.get('/reasons', response_model=List[ReasonResponse])
@transaction(1)
async def get_reasons() -> List[ReasonResponse]:
    return [
        ReasonResponse(**reason.model_dump())
        for reason in await Reason.get_all()
    ]


@router.get('/owner', response_model=UserResponse)
@transaction(1)
async def get_owner() -> UserResponse:
    owner = await User.get_owner()
    if not owner:
        raise HTTPException(404, 'Owner not found!')

    return UserResponse(**owner.model_dump())


@router.get('/dashboard', response_model=ReviewsDashboardResponse, dependencies=[Depends(user_required)])
@transaction(1)
async def get_dashboard(date_after: Optional[datetime] = None, date_before: Optional[datetime] = None) -> ReviewsDashboardResponse:
    reviews = await Review.get_all(date_after, date_before)
    complaints = await Complaint.get_all(date_after, date_before)

    return ReviewsDashboardResponse(
        reviews=[create_review_response(review) for review in reviews],
        complaints=[create_complaint_response(complaint) for complaint in complaints]
    )


@router.get('/export/reviews', response_class=StreamingResponse, dependencies=[Depends(user_required)])
@transaction(1)
async def export_reviews_file(date_after: Optional[datetime] = None, date_before: Optional[datetime] = None):
    rows_data = []
    for review in await Review.get_all(date_after, date_before):
        doctors_text = ', '.join(doctor.name for doctor in review.selected_doctors)
        services_text = ', '.join(service.name for service in review.selected_services)
        platforms_text = ', '.join(platform.name for platform in review.published_platforms)
        rows_data.append({
            'Пациент': review.contact_name,
            'Телефон': review.contact_phone,
            'Врач': doctors_text,
            'Услуга': services_text,
            'Подарок': review.selected_reward.name if review.selected_reward else None,
            'Платформы': platforms_text,
            'Текст отзыва': review.review_text,
        })

    excel_bytes = export_rows_to_excel(rows_data)
    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@router.get('/export/complaints', response_class=StreamingResponse, dependencies=[Depends(user_required)])
@transaction(1)
async def export_complaints_file(date_after: Optional[datetime] = None, date_before: Optional[datetime] = None) -> StreamingResponse:
    rows_data = []
    for complaint in await Complaint.get_all(date_after, date_before):
        reasons_text = ', '.join(reason.name for reason in complaint.selected_reasons)
        rows_data.append({
            'Пациент': complaint.contact_name,
            'Телефон': complaint.contact_phone,
            'Причины': reasons_text,
            'Текст жалобы': complaint.complaint_text,
        })

    excel_bytes = export_rows_to_excel(rows_data)
    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@router.get('/telegram/link', response_model=LinkTelegramResponse)
@transaction(1)
async def link_telegram(user: User = Depends(user_required)) -> LinkTelegramResponse:
    start_link = await create_start_link(get_bot(), str(user.id), encode=True)
    return LinkTelegramResponse(start_link=start_link)


@router.post('/telegram/unlink', status_code=204)
@transaction(1)
async def unlink_telegram(user: User = Depends(user_required)):
    user.telegram_id = None
    user.telegram_name = None
    user.add()


@router.get('/images/{image_path}', response_class=FileResponse)
async def get_image_file(image_path: str) -> FileResponse:
    full_path = os.path.join('images', image_path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail='Image not found!')

    return FileResponse(full_path)


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
