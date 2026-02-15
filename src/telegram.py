from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandObject, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel
from rewire import config, DependenciesModule, logger, simple_plugin
from rewire_sqlmodel import transaction

import auth
from src.models import User


@config
class Config(BaseModel):
    token: str


plugin = simple_plugin()
router = Router()


class UnlinkUserCallback(CallbackData, prefix='unlink_user'):
    user_id: int


@plugin.setup()
async def create_telegram_bot() -> Bot:
    return Bot(token=Config.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@plugin.setup()
async def create_dispatcher() -> Dispatcher:
    return Dispatcher(storage=MemoryStorage())


@plugin.setup()
def include_router(dispatcher: Dispatcher):
    dispatcher.include_router(router)


@plugin.setup()
def add_middleware(dispatcher: Dispatcher):
    dispatcher.callback_query.middleware(CallbackAnswerMiddleware())


@plugin.run()
async def start_telegram_bot(bot: Bot, dispatcher: Dispatcher):
    await dispatcher.start_polling(bot)


@router.message(CommandStart())
@transaction(1)
async def start_command_handler(message: Message, command: CommandObject):
    if not command.args:
        return

    user = await User.get_by_id(auth.decode_user_id(command.args))
    if not user:
        return

    user.telegram_id = message.from_user.id
    user.telegram_name = message.from_user.full_name
    user.add()

    await message.answer(
        f'✨ Telegram успешно привязан к аккаунту <b>«{user.name}»</b>!\n'
        'Теперь все уведомления о новых отзывах и жалобах будут направляться сюда.',
        reply_markup=InlineKeyboardBuilder()
        .button(text='❌ Отвязать', callback_data=UnlinkUserCallback(user_id=user.id))
        .adjust(1).as_markup()
    )


@router.callback_query(UnlinkUserCallback.filter())
@transaction(1)
async def unlink_user_callback(callback: CallbackQuery, callback_data: UnlinkUserCallback):
    user = await User.get_by_id(callback_data.user_id)
    user.telegram_id = None
    user.telegram_name = None
    user.add()

    await callback.message.edit_text(
        f'🛑 Telegram успешно отвязан от аккаунта <b>«{user.name}»</b>.\n'
        'Вы больше не будете получать уведомления о новых отзывах и жалобах.'
    )


@transaction(1)
async def send_admin_message(message_text: str):
    for user in await User.get_all():
        if not user.telegram_id:
            continue

        try:
            await get_telegram_bot().send_message(
                user.telegram_id,
                message_text
            )
        except TelegramAPIError as e:
            logger.error(f'Failed to send message to {user.telegram_id}: {e}')


def get_telegram_bot() -> Bot:
    return DependenciesModule.get().resolve(Bot)
