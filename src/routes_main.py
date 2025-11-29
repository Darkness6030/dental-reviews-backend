import os
from typing import List

from fastapi import APIRouter, FastAPI, HTTPException, Depends
from rewire import simple_plugin
from rewire_sqlmodel import transaction
from starlette.responses import FileResponse

from src import auth
from src.auth import user_required
from src.models import Doctor, Service, Aspect, Platform, User
from src.schemas import DoctorResponse, ServiceResponse, AspectResponse, create_doctor_response, PlatformResponse, LoginRequest, LoginResponse, UserResponse

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


@router.get('/images/{image_path}', response_class=FileResponse)
async def get_image_file(image_path: str) -> FileResponse:
    full_path = os.path.join('images', image_path)
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail='Image not found!')

    return FileResponse(full_path)


@router.get('/doctors', response_model=List[DoctorResponse])
@transaction(1)
async def get_doctors() -> List[DoctorResponse]:
    return [
        create_doctor_response(doctor)
        for doctor in await Doctor.get_all()
    ]


@router.get('/doctors/{doctor_id}', response_model=DoctorResponse)
@transaction(1)
async def get_doctor(doctor_id: int) -> DoctorResponse:
    doctor = await Doctor.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(404, 'Doctor not found!')

    return create_doctor_response(doctor)


@router.get('/services', response_model=List[ServiceResponse])
@transaction(1)
async def get_services() -> List[ServiceResponse]:
    return [
        ServiceResponse(**service.model_dump())
        for service in await Service.get_all()
    ]


@router.get('/services/{service_id}', response_model=ServiceResponse)
@transaction(1)
async def get_service(service_id: int) -> ServiceResponse:
    service = await Service.get_by_id(service_id)
    if not service:
        raise HTTPException(404, 'Service not found!')

    return ServiceResponse(**service.model_dump())


@router.get('/aspects', response_model=List[AspectResponse])
@transaction(1)
async def get_aspects() -> List[AspectResponse]:
    return [
        AspectResponse(**aspect.model_dump())
        for aspect in await Aspect.get_all()
    ]


@router.get('/aspects/{aspect_id}', response_model=AspectResponse)
@transaction(1)
async def get_aspect(aspect_id: int) -> AspectResponse:
    aspect = await Aspect.get_by_id(aspect_id)
    if not aspect:
        raise HTTPException(404, 'Aspect not found!')

    return AspectResponse(**aspect.model_dump())


@router.get('/platforms', response_model=List[PlatformResponse])
@transaction(1)
async def get_platforms() -> List[PlatformResponse]:
    return [
        PlatformResponse(**platform.model_dump())
        for platform in await Platform.get_all()
    ]


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
