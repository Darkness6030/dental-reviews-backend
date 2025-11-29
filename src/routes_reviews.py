from datetime import datetime
from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException, Depends
from rewire import simple_plugin
from rewire_sqlmodel import transaction, session_context

from src import openai
from src.auth import user_required
from src.models import ReviewRequest, Doctor, Service, Aspect, Platform
from src.schemas import ReviewCreateRequest, ReviewResponse, ReviewDoctorsRequest, ReviewServicesRequest, ReviewAspectsRequest, create_review_response, ReviewsDashboardResponse

plugin = simple_plugin()
router = APIRouter(prefix='/reviews', tags=['Reviews'])


@router.post('/create', response_model=ReviewResponse)
@transaction(1)
async def create_review_request(request: ReviewCreateRequest) -> ReviewResponse:
    review_request = ReviewRequest(user_fio=request.user_fio, user_phone=request.user_phone)
    review_request.add()

    await session_context.get().commit()
    await session_context.get().refresh(review_request)
    return create_review_response(review_request)


@router.get('/{request_id}', response_model=ReviewResponse)
@transaction(1)
async def get_review_request(request_id: int) -> ReviewResponse:
    review_request = await ReviewRequest.get_by_id(request_id)
    if not review_request:
        raise HTTPException(404, 'Review request not found!')

    return create_review_response(review_request)


@router.post('/{request_id}/doctors', response_model=ReviewResponse)
@transaction(1)
async def update_request_doctors(request_id: int, request: ReviewDoctorsRequest) -> ReviewResponse:
    review_request = await ReviewRequest.get_by_id(request_id)
    if not review_request:
        raise HTTPException(404, 'Review request not found!')

    selected_doctors = await Doctor.get_by_ids(request.doctor_ids)
    if not selected_doctors:
        raise HTTPException(400, 'No request doctors found!')

    review_request.selected_doctors = selected_doctors
    review_request.add()

    return create_review_response(review_request)


@router.post('/{request_id}/services', response_model=ReviewResponse)
@transaction(1)
async def update_request_services(request_id: int, request: ReviewServicesRequest) -> ReviewResponse:
    review_request = await ReviewRequest.get_by_id(request_id)
    if not review_request:
        raise HTTPException(404, 'Review request not found!')

    selected_services = await Service.get_by_ids(request.service_ids)
    if not selected_services:
        raise HTTPException(400, 'No request services found!')

    review_request.selected_services = selected_services
    review_request.add()

    return create_review_response(review_request)


@router.post('/{request_id}/aspects', response_model=ReviewResponse)
@transaction(1)
async def update_request_aspects(request_id: int, request: ReviewAspectsRequest) -> ReviewResponse:
    review_request = await ReviewRequest.get_by_id(request_id)
    if not review_request:
        raise HTTPException(404, 'Review request not found!')

    selected_aspects = await Aspect.get_by_ids(request.aspect_ids)
    if not selected_aspects:
        raise HTTPException(400, 'No request aspects found!')

    review_request.selected_aspects = selected_aspects
    review_request.add()

    return create_review_response(review_request)


@router.post('/{request_id}/platforms/{platform_id}/publish')
@transaction(1)
async def add_request_published_platform(request_id: int, platform_id: str) -> ReviewResponse:
    review_request = await ReviewRequest.get_by_id(request_id)
    if not review_request:
        raise HTTPException(404, 'Review request not found!')

    platform = await Platform.get_by_id(platform_id)
    if not platform:
        raise HTTPException(400, 'Platform not found!')

    if platform not in review_request.published_platforms:
        review_request.published_platforms.append(platform)
        review_request.add()

    return create_review_response(review_request)


@router.post('/{request_id}/generate', response_model=ReviewResponse)
@transaction(1)
async def generate_review_text(request_id: int) -> ReviewResponse:
    review_request = await ReviewRequest.get_by_id(request_id)
    if not review_request:
        raise HTTPException(404, 'Review request not found!')

    if not review_request.selected_doctors or not review_request.selected_services or not review_request.selected_aspects:
        raise HTTPException(400, 'Doctors, services or aspects not filled!')

    generated_text = await openai.generate_review_text(
        doctor_names=[doctor.name for doctor in review_request.selected_doctors],
        service_names=[service.name for service in review_request.selected_services],
        aspect_names=[aspect.name for aspect in review_request.selected_aspects]
    )

    review_request.generated_text = generated_text
    review_request.add()

    return create_review_response(review_request)


@router.get('/dashboard', response_model=ReviewsDashboardResponse, dependencies=[Depends(user_required)])
@transaction(1)
async def get_reviews_dashboard(date_before: Optional[datetime] = None, date_after: Optional[datetime] = None) -> ReviewsDashboardResponse:
    review_requests = await ReviewRequest.get_all(date_before, date_after)
    total_requests = len(review_requests)
    total_generated = sum(1 for request in review_requests if request.generated_text)
    total_published = sum(1 for request in review_requests if request.published_platforms)

    return ReviewsDashboardResponse(
        total_requests=total_requests,
        total_generated=total_generated,
        total_published=total_published,
        reviews=[create_review_response(review_request) for review_request in review_requests]
    )


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
