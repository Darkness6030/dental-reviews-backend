from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from rewire import simple_plugin
from rewire_sqlmodel import session_context, transaction

from src import chatgpt
from src.auth import admin_required, owner_required
from src.models import Aspect, Doctor, News, Platform, Prompt, Reason, Reward, Service, Source, User
from src.schemas import AspectRequest, AspectResponse, create_doctor_response, DoctorRequest, DoctorResponse, NewsRequest, NewsResponse, PlatformRequest, PlatformResponse, PromptRequest, PromptResponse, PromptTestResponse, ReasonRequest, ReasonResponse, ReorderRequest, RewardRequest, RewardResponse, ServiceRequest, ServiceResponse, SourceRequest, SourceResponse, UserRequest, UserResponse

plugin = simple_plugin()
router = APIRouter(
    prefix='/api/admin',
    tags=['Admin'],
    dependencies=[Depends(admin_required)]
)


@router.get('/users', dependencies=[Depends(owner_required)])
@transaction(1)
async def get_users() -> List[UserResponse]:
    return [
        UserResponse(**user.model_dump())
        for user in await User.get_all()
    ]


@router.post('/users', dependencies=[Depends(owner_required)])
@transaction(1)
async def create_user(request: UserRequest) -> UserResponse:
    user = User(**request.model_dump())
    user.set_password(request.password)
    user.add()

    await session_context.get().commit()
    return UserResponse(**user.model_dump())


@router.post('/users/{user_id}', dependencies=[Depends(owner_required)])
@transaction(1)
async def update_user(user_id: int, request: UserRequest) -> UserResponse:
    user = await User.get_by_id(user_id)
    if not user:
        raise HTTPException(404, 'User not found!')

    if request.password:
        user.set_password(request.password)

    user.sqlmodel_update(request.model_dump())
    user.add()

    return UserResponse(**user.model_dump())


@router.delete('/users/{user_id}', dependencies=[Depends(owner_required)], status_code=204)
@transaction(1)
async def delete_user(user_id: int):
    user = await User.get_by_id(user_id)
    if not user:
        raise HTTPException(404, 'User not found!')

    await user.delete()


@router.post('/doctors')
@transaction(1)
async def create_doctor(request: DoctorRequest) -> DoctorResponse:
    services = await Service.get_by_ids(request.service_ids)
    doctor = Doctor(**request.model_dump(), services=services)
    doctor.add()

    await session_context.get().commit()
    return create_doctor_response(doctor)


@router.post('/doctors/{doctor_id}')
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


@router.patch('/doctors/reorder', status_code=204)
@transaction(1)
async def reorder_doctors(request: ReorderRequest):
    await Doctor.reorder(request.ordered_ids)


@router.post('/services')
@transaction(1)
async def create_service(request: ServiceRequest) -> ServiceResponse:
    service = Service(**request.model_dump())
    service.add()

    await session_context.get().commit()
    return ServiceResponse(**service.model_dump())


@router.post('/services/{service_id}')
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


@router.patch('/services/reorder', status_code=204)
@transaction(1)
async def reorder_services(request: ReorderRequest):
    await Service.reorder(request.ordered_ids)


@router.post('/aspects')
@transaction(1)
async def create_aspect(request: AspectRequest) -> AspectResponse:
    aspect = Aspect(**request.model_dump())
    aspect.add()

    await session_context.get().commit()
    return AspectResponse(**aspect.model_dump())


@router.post('/aspects/{aspect_id}')
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


@router.patch('/aspects/reorder', status_code=204)
@transaction(1)
async def reorder_aspects(request: ReorderRequest):
    await Aspect.reorder(request.ordered_ids)


@router.post('/sources')
@transaction(1)
async def create_source(request: SourceRequest) -> SourceResponse:
    source = Source(**request.model_dump())
    source.add()

    await session_context.get().commit()
    return SourceResponse(**source.model_dump())


@router.post('/sources/{source_id}')
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


@router.patch('/sources/reorder', status_code=204)
@transaction(1)
async def reorder_sources(request: ReorderRequest):
    await Source.reorder(request.ordered_ids)


@router.post('/rewards')
@transaction(1)
async def create_reward(request: RewardRequest) -> RewardResponse:
    reward = Reward(**request.model_dump())
    reward.add()

    await session_context.get().commit()
    return RewardResponse(**reward.model_dump())


@router.post('/rewards/{reward_id}')
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


@router.patch('/rewards/reorder', status_code=204)
@transaction(1)
async def reorder_rewards(request: ReorderRequest):
    await Reward.reorder(request.ordered_ids)


@router.post('/platforms')
@transaction(1)
async def create_platform(request: PlatformRequest) -> PlatformResponse:
    platform = Platform(**request.model_dump())
    platform.add()

    await session_context.get().commit()
    return PlatformResponse(**platform.model_dump())


@router.post('/platforms/{platform_id}')
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


@router.patch('/platforms/reorder', status_code=204)
@transaction(1)
async def reorder_platforms(request: ReorderRequest):
    await Platform.reorder(request.ordered_ids)


@router.post('/reasons')
@transaction(1)
async def create_reason(request: ReasonRequest) -> ReasonResponse:
    reason = Reason(**request.model_dump())
    reason.add()

    await session_context.get().commit()
    return ReasonResponse(**reason.model_dump())


@router.post('/reasons/{reason_id}')
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


@router.patch('/reasons/reorder', status_code=204)
@transaction(1)
async def reorder_reasons(request: ReorderRequest):
    await Reason.reorder(request.ordered_ids)


@router.post('/news')
@transaction(1)
async def create_news(request: NewsRequest) -> NewsResponse:
    news = News(**request.model_dump())
    news.add()

    await session_context.get().commit()
    return NewsResponse(**news.model_dump())


@router.post('/news/{news_id}')
@transaction(1)
async def update_news(news_id: int, request: NewsRequest) -> NewsResponse:
    news = await News.get_by_id(news_id)
    if not news:
        raise HTTPException(404, 'News not found!')

    news.sqlmodel_update(request.model_dump())
    news.add()

    return NewsResponse(**news.model_dump())


@router.delete('/news/{news_id}', status_code=204)
@transaction(1)
async def delete_news(news_id: int):
    news = await News.get_by_id(news_id)
    if not news:
        raise HTTPException(404, 'News not found!')

    await news.delete()


@router.patch('/news/reorder', status_code=204)
@transaction(1)
async def reorder_news(request: ReorderRequest):
    await News.reorder(request.ordered_ids)


@router.get('/prompts')
@transaction(1)
async def get_prompts() -> List[PromptResponse]:
    return [
        PromptResponse(**prompt.model_dump())
        for prompt in await Prompt.get_all()
    ]


@router.get('/prompts/{prompt_id}')
@transaction(1)
async def get_prompt(prompt_id: str) -> PromptResponse:
    prompt = await Prompt.get_by_id(prompt_id)
    if not prompt:
        raise HTTPException(404, 'Prompt not found!')

    return PromptResponse(**prompt.model_dump())


@router.post('/prompts')
@transaction(1)
async def update_prompt(request: PromptRequest) -> PromptResponse:
    prompt = await Prompt.get_by_id(request.id)
    if not prompt:
        prompt = Prompt(**request.model_dump())
        prompt.add()
    else:
        prompt.sqlmodel_update(request.model_dump())
        prompt.add()

    await session_context.get().commit()
    return PromptResponse(**prompt.model_dump())


@router.post('/prompts/test')
@transaction(1)
async def test_prompt(request: PromptRequest) -> PromptTestResponse:
    generated_text = await chatgpt.test_prompt_text(
        prompt_text=request.prompt_text,
        temperature=request.temperature,
        frequency_penalty=request.frequency_penalty,
    )

    return PromptTestResponse(generated_text=generated_text)


@plugin.setup()
def include_router(app: FastAPI):
    app.include_router(router)
