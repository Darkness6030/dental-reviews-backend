import os
import uuid
from datetime import datetime
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, UploadFile
from rewire import simple_plugin
from rewire_sqlmodel import session_context, transaction
from starlette.requests import Request

from src.auth import admin_required
from src.models import Aspect, Complaint, Doctor, Owner, Platform, Reason, Review, Reward, Service, Source
from src.schemas import AspectRequest, AspectResponse, DoctorRequest, DoctorResponse, OwnerRequest, OwnerResponse, PlatformRequest, PlatformResponse, ReasonRequest, ReasonResponse, ReviewsDashboardResponse, RewardRequest, RewardResponse, ServiceRequest, ServiceResponse, SourceRequest, SourceResponse, UploadImageResponse, create_complaint_response, create_doctor_response, create_review_response

plugin = simple_plugin()
router = APIRouter(
    prefix='/api/admin',
    tags=['Admin'],
    dependencies=[Depends(admin_required)]
)


@router.post('/doctors', response_model=DoctorResponse)
@transaction(1)
async def create_doctor(request: DoctorRequest) -> DoctorResponse:
    services = await Service.get_by_ids(request.service_ids)
    doctor = Doctor(**request.model_dump(), services=services)
    doctor.add()

    await session_context.get().commit()
    return create_doctor_response(doctor)


@router.post('/doctors/{doctor_id}', response_model=DoctorResponse)
@transaction(1)
async def update_doctor(doctor_id: int, request: DoctorRequest) -> DoctorResponse:
    doctor = await Doctor.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(404, 'Doctor not found!')

    services = await Service.get_by_ids(request.service_ids)
    doctor.sqlmodel_update(request.model_dump())
    doctor.services = services
    doctor.add()

    return create_doctor_response(doctor)


@router.delete('/doctors/{doctor_id}', status_code=204)
@transaction(1)
async def delete_doctor(doctor_id: int):
    doctor = await Doctor.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(404, 'Doctor not found!')

    await doctor.delete()


@router.post('/services', response_model=ServiceResponse)
@transaction(1)
async def create_service(request: ServiceRequest) -> ServiceResponse:
    service = Service(**request.model_dump())
    service.add()

    await session_context.get().commit()
    return ServiceResponse(**service.model_dump())


@router.post('/services/{service_id}', response_model=ServiceResponse)
@transaction(1)
async def update_service(service_id: int, request: ServiceRequest) -> ServiceResponse:
    service = await Service.get_by_id(service_id)
    if not service:
        raise HTTPException(404, 'Service not found!')

    service.sqlmodel_update(request.model_dump())
    service.add()

    return ServiceResponse(**service.model_dump())


@router.delete('/services/{service_id}', status_code=204)
@transaction(1)
async def delete_service(service_id: int):
    service = await Service.get_by_id(service_id)
    if not service:
        raise HTTPException(404, 'Service not found!')

    await service.delete()


@router.post('/aspects', response_model=AspectResponse)
@transaction(1)
async def create_aspect(request: AspectRequest) -> AspectResponse:
    aspect = Aspect(**request.model_dump())
    aspect.add()

    await session_context.get().commit()
    return AspectResponse(**aspect.model_dump())


@router.post('/aspects/{aspect_id}', response_model=AspectResponse)
@transaction(1)
async def update_aspect(aspect_id: int, request: AspectRequest) -> AspectResponse:
    aspect = await Aspect.get_by_id(aspect_id)
    if not aspect:
        raise HTTPException(404, 'Aspect not found!')

    aspect.sqlmodel_update(request.model_dump())
    aspect.add()

    return AspectResponse(**aspect.model_dump())


@router.delete('/aspects/{aspect_id}', status_code=204)
@transaction(1)
async def delete_aspect(aspect_id: int):
    aspect = await Aspect.get_by_id(aspect_id)
    if not aspect:
        raise HTTPException(404, 'Aspect not found!')

    await aspect.delete()


@router.post('/sources', response_model=SourceResponse)
@transaction(1)
async def create_source(request: SourceRequest) -> SourceResponse:
    source = Source(**request.model_dump())
    source.add()

    await session_context.get().commit()
    return SourceResponse(**source.model_dump())


@router.post('/sources/{source_id}', response_model=SourceResponse)
@transaction(1)
async def update_source(source_id: int, request: SourceRequest) -> SourceResponse:
    source = await Source.get_by_id(source_id)
    if not source:
        raise HTTPException(404, 'Source not found!')

    source.sqlmodel_update(request.model_dump())
    source.add()

    return SourceResponse(**source.model_dump())


@router.delete('/sources/{source_id}', status_code=204)
@transaction(1)
async def delete_source(source_id: int):
    source = await Source.get_by_id(source_id)
    if not source:
        raise HTTPException(404, 'Source not found!')

    await source.delete()


@router.post('/rewards', response_model=RewardResponse)
@transaction(1)
async def create_reward(request: RewardRequest) -> RewardResponse:
    reward = Reward(**request.model_dump())
    reward.add()

    await session_context.get().commit()
    return RewardResponse(**reward.model_dump())


@router.post('/rewards/{reward_id}', response_model=RewardResponse)
@transaction(1)
async def update_reward(reward_id: int, request: RewardRequest) -> RewardResponse:
    reward = await Reward.get_by_id(reward_id)
    if not reward:
        raise HTTPException(404, 'Reward not found!')

    reward.sqlmodel_update(request.model_dump())
    reward.add()

    return RewardResponse(**reward.model_dump())


@router.delete('/rewards/{reward_id}', status_code=204)
@transaction(1)
async def delete_reward(reward_id: int):
    reward = await Reward.get_by_id(reward_id)
    if not reward:
        raise HTTPException(404, 'Reward not found!')

    await reward.delete()


@router.post('/platforms', response_model=PlatformResponse)
@transaction(1)
async def create_platform(request: PlatformRequest) -> PlatformResponse:
    platform = Platform(**request.model_dump())
    platform.add()

    await session_context.get().commit()
    return PlatformResponse(**platform.model_dump())


@router.post('/platforms/{platform_id}', response_model=PlatformResponse)
@transaction(1)
async def update_platform(platform_id: int, request: PlatformRequest) -> PlatformResponse:
    platform = await Platform.get_by_id(platform_id)
    if not platform:
        raise HTTPException(404, 'Platform not found!')

    platform.sqlmodel_update(request.model_dump())
    platform.add()

    return PlatformResponse(**platform.model_dump())


@router.delete('/platforms/{platform_id}', status_code=204)
@transaction(1)
async def delete_platform(platform_id: int):
    platform = await Platform.get_by_id(platform_id)
    if not platform:
        raise HTTPException(404, 'Platform not found!')

    await platform.delete()


@router.post('/reasons', response_model=ReasonResponse)
@transaction(1)
async def create_reason(request: ReasonRequest) -> ReasonResponse:
    reason = Reason(**request.model_dump())
    reason.add()

    await session_context.get().commit()
    return ReasonResponse(**reason.model_dump())


@router.post('/reasons/{reason_id}', response_model=ReasonResponse)
@transaction(1)
async def update_reason(reason_id: int, request: ReasonRequest) -> ReasonResponse:
    reason = await Reason.get_by_id(reason_id)
    if not reason:
        raise HTTPException(404, 'Reason not found!')

    reason.sqlmodel_update(request.model_dump())
    reason.add()

    return ReasonResponse(**reason.model_dump())


@router.delete('/reasons/{reason_id}', status_code=204)
@transaction(1)
async def delete_reason(reason_id: int):
    reason = await Reason.get_by_id(reason_id)
    if not reason:
        raise HTTPException(404, 'Reason not found!')

    await reason.delete()


@router.post('/owner', response_model=OwnerResponse)
@transaction(1)
async def update_owner(request: OwnerRequest):
    owner = await Owner.get()
    if not owner:
        owner = Owner(**request.model_dump())
        owner.add()
    else:
        owner.sqlmodel_update(request.model_dump())
        owner.add()

    await session_context.get().commit()
    return OwnerResponse(**owner.model_dump())


@router.delete('/owner', status_code=204)
async def delete_owner():
    owner = await Owner.get()
    if not owner:
        raise HTTPException(404, 'Owner not found!')

    await owner.delete()


@router.get('/reviews/dashboard', response_model=ReviewsDashboardResponse)
@transaction(1)
async def get_dashboard(date_after: Optional[datetime] = None, date_before: Optional[datetime] = None) -> ReviewsDashboardResponse:
    reviews = await Review.get_all(date_after, date_before)
    complaints = await Complaint.get_all(date_after, date_before)

    return ReviewsDashboardResponse(
        reviews=[create_review_response(review) for review in reviews],
        complaints=[create_complaint_response(complaint) for complaint in complaints]
    )


@router.post('/images/upload')
async def upload_image_file(request: Request, file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='Only image files are allowed!')

    extension = os.path.splitext(file.filename)[1]
    filename = f'{uuid.uuid4().hex}{extension}'

    file_path = os.path.join('images', filename)
    async with aiofiles.open(file_path, 'wb') as output_file:
        await output_file.write(await file.read())

    base_url = str(request.base_url).rstrip('/')
    return UploadImageResponse(
        filename=filename,
        image_url=f'{base_url}/api/images/{filename}'
    )


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
