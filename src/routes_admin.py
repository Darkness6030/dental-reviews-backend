from fastapi import APIRouter, FastAPI, HTTPException, Depends
from rewire import simple_plugin
from rewire_sqlmodel import transaction, session_context

from src.auth import admin_required
from src.models import Doctor, Service, Aspect
from src.schemas import DoctorRequest, DoctorResponse, ServiceRequest, ServiceResponse, AspectRequest, AspectResponse, create_doctor_response

plugin = simple_plugin()
router = APIRouter(
    prefix='/admin',
    tags=['Admin'],
    dependencies=[Depends(admin_required)]
)


@router.post('/doctors', response_model=DoctorResponse)
@transaction(1)
async def create_doctor(request: DoctorRequest) -> DoctorResponse:
    services = await Service.get_by_ids(request.service_ids)
    if not services:
        raise HTTPException(404, 'No services found!')

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
    if not services:
        raise HTTPException(404, 'No services found!')

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


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
