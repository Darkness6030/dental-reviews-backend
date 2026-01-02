import os
from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from rewire import simple_plugin
from rewire_sqlmodel import transaction
from starlette.responses import FileResponse

from src import auth
from src.auth import user_required
from src.models import Aspect, Doctor, Platform, Reason, Reward, Service, Source, User
from src.schemas import AspectResponse, DoctorResponse, LoginRequest, LoginResponse, PlatformResponse, ReasonResponse, RewardResponse, ServiceResponse, SourceResponse, UserResponse, create_doctor_response

plugin = simple_plugin()
router = APIRouter(tags=['Main'])


@router.post('/login', response_model=LoginResponse)
@transaction(1)
async def login(request: LoginRequest) -> LoginResponse:
    user = await User.get_by_username(request.username)
    if not user or not user.check_password(request.password):
        raise HTTPException(401, 'Invalid username or password!')

    access_token = auth.generate_access_token(user.id)
    return LoginResponse(access_token=access_token)


@router.get('/user', response_model=UserResponse)
@transaction(1)
async def get_user(user: User = Depends(user_required)) -> UserResponse:
    return UserResponse(**user.model_dump())


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


@router.get('/images/{image_path}', response_class=FileResponse)
async def get_image_file(image_path: str) -> FileResponse:
    full_path = os.path.join('images', image_path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail='Image not found!')

    return FileResponse(full_path)


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
