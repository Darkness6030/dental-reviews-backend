from fastapi import APIRouter, BackgroundTasks, FastAPI, HTTPException
from rewire import simple_plugin
from rewire_sqlmodel import session_context, transaction

from src import chatgpt
from src.bot import send_admin_message
from src.models import Aspect, Complaint, Doctor, Platform, Prompt, Reason, Review, Reward, Service, Source
from src.schemas import create_review_response, CreateComplaintRequest, CreateComplaintResponse, CreateReviewResponse, ReviewAspectsRequest, ReviewContactsRequest, ReviewDoctorsRequest, ReviewResponse, ReviewRewardRequest, ReviewServicesRequest, ReviewSourceRequest, ReviewTextRequest

plugin = simple_plugin()
router = APIRouter(prefix='/api/reviews', tags=['Reviews'])


@router.post('', response_model=CreateReviewResponse)
@transaction(1)
async def create_review() -> CreateReviewResponse:
    review = Review()
    review.add()

    await session_context.get().commit()
    return CreateReviewResponse(**review.model_dump())


@router.get('/{review_id}', response_model=ReviewResponse)
@transaction(1)
async def get_review(review_id: int) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    return create_review_response(review)


@router.post('/{review_id}/doctors', response_model=ReviewResponse)
@transaction(1)
async def select_review_doctors(review_id: int, request: ReviewDoctorsRequest) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    doctors = await Doctor.get_by_ids(request.doctor_ids)
    if not doctors:
        raise HTTPException(400, 'Doctors not found!')

    review.selected_doctors = doctors
    review.add()

    return create_review_response(review)


@router.post('/{review_id}/services', response_model=ReviewResponse)
@transaction(1)
async def select_review_services(review_id: int, request: ReviewServicesRequest) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    services = await Service.get_by_ids(request.service_ids)
    if not services:
        raise HTTPException(400, 'Services not found!')

    review.selected_services = services
    review.add()

    return create_review_response(review)


@router.post('/{review_id}/aspects', response_model=ReviewResponse)
@transaction(1)
async def select_review_aspects(review_id: int, request: ReviewAspectsRequest) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    aspects = await Aspect.get_by_ids(request.aspect_ids)
    if not aspects:
        raise HTTPException(400, 'Aspects not found!')

    review.selected_aspects = aspects
    review.add()

    return create_review_response(review)


@router.post('/{review_id}/source', response_model=ReviewResponse)
@transaction(1)
async def select_review_source(review_id: int, request: ReviewSourceRequest) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    source = await Source.get_by_id(request.source_id)
    if not source:
        raise HTTPException(400, 'Source not found!')

    review.selected_source = source
    review.add()

    return create_review_response(review)


@router.post('/{review_id}/contacts', response_model=ReviewResponse)
@transaction(1)
async def set_review_contacts(review_id: int, request: ReviewContactsRequest) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    review.contact_name = request.contact_name
    review.contact_phone = request.contact_phone
    review.add()

    return create_review_response(review)


@router.post('/{review_id}/text', response_model=ReviewResponse)
@transaction(1)
async def update_review_text(review_id: int, request: ReviewTextRequest) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    review.review_text = request.review_text
    review.add()

    return create_review_response(review)


@router.post('/{review_id}/generate', response_model=ReviewResponse)
@transaction(1)
async def generate_review_text(review_id: int, background_tasks: BackgroundTasks) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    reviews_prompt = await Prompt.get_by_id('reviews')
    if not reviews_prompt:
        raise HTTPException(404, 'Reviews prompt not found!')

    review_text = await chatgpt.generate_review_text(
        prompt_text=reviews_prompt.prompt_text,
        temperature=reviews_prompt.temperature,
        frequency_penalty=reviews_prompt.frequency_penalty,
        doctors=review.selected_doctors,
        services=review.selected_services,
        aspects=review.selected_aspects,
        source=review.selected_source
    )

    review.review_text = review_text
    review.add()

    doctors_text = ', '.join(doctor.name for doctor in review.selected_doctors) or '—'
    services_text = ', '.join(service.name for service in review.selected_services) or '—'
    aspects_text = ', '.join(aspect.name for aspect in review.selected_aspects) or '—'
    source_text = review.selected_source.name if review.selected_source else '—'

    message_text = (
        f'🆕 <b>Сгенерирован новый отзыв</b>\n\n'
        f'🆔 ID: <b>{review.id}</b>\n'
        f'📅 Дата: {review.created_at.strftime('%d.%m.%Y %H:%M')}\n\n'
        f'👤 Имя: {review.contact_name or '—'}\n'
        f'📞 Телефон: {review.contact_phone or '—'}\n\n'
        f'👨‍⚕️ Врачи: {doctors_text}\n'
        f'🛎 Услуги: {services_text}\n'
        f'⭐ Аспекты: {aspects_text}\n'
        f'🌐 Источник: {source_text}\n\n'
        f'📝 <b>Текст отзыва:</b>\n'
        f'{review.review_text or '—'}'
    )

    background_tasks.add_task(
        send_admin_message,
        message_text
    )

    return create_review_response(review)


@router.post('/{review_id}/reward', response_model=ReviewResponse)
@transaction(1)
async def select_review_reward(review_id: int, request: ReviewRewardRequest) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    reward = await Reward.get_by_id(request.reward_id)
    if not reward:
        raise HTTPException(400, 'Reward not found!')

    review.selected_reward = reward
    review.add()

    return create_review_response(review)


@router.post('/{review_id}/platforms/{platform_id}', response_model=ReviewResponse)
@transaction(1)
async def add_review_platform(review_id: int, platform_id: int) -> ReviewResponse:
    review = await Review.get_by_id(review_id)
    if not review:
        raise HTTPException(404, 'Review not found!')

    platform = await Platform.get_by_id(platform_id)
    if not platform:
        raise HTTPException(400, 'Platform not found!')

    if platform not in review.published_platforms:
        review.published_platforms.append(platform)
        review.add()

    return create_review_response(review)


@router.post('/complaint', response_model=CreateComplaintResponse)
@transaction(1)
async def create_complaint(request: CreateComplaintRequest, background_tasks: BackgroundTasks) -> CreateComplaintResponse:
    reasons = await Reason.get_by_ids(request.reason_ids)
    if not reasons:
        raise HTTPException(400, 'Reasons not found!')

    complaint = Complaint(**request.model_dump(), selected_reasons=reasons)
    complaint.add()

    reasons_text = ', '.join(reason.name for reason in complaint.selected_reasons) or '—'
    message_text = (
        f'🚨 <b>Новая жалоба</b>\n\n'
        f'🆔 ID: <b>{complaint.id}</b>\n'
        f'📅 Дата: {complaint.created_at.strftime('%d.%m.%Y %H:%M')}\n\n'
        f'👤 Имя: {complaint.contact_name or '—'}\n'
        f'📞 Телефон: {complaint.contact_phone or '—'}\n'
        f'⚠ Причины: {reasons_text}\n\n'
        f'📝 <b>Текст жалобы:</b>\n'
        f'{complaint.complaint_text or '—'}'
    )

    background_tasks.add_task(
        send_admin_message,
        message_text
    )

    await session_context.get().commit()
    return CreateComplaintResponse(**complaint.model_dump())


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
