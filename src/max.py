from aiohttp import TCPConnector
from maxapi import Bot, Dispatcher
from maxapi.client import DefaultConnectionProperties
from maxapi.enums.parse_mode import ParseMode
from maxapi.filters.callback_payload import CallbackPayload
from maxapi.filters.command import Command
from maxapi.types import BotStarted, CallbackButton, MessageCallback, MessageCreated
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from pydantic import BaseModel
from rewire import config, DependenciesModule, simple_plugin
from rewire_sqlmodel import transaction

import auth
from src.models import User


@config
class Config(BaseModel):
    token: str


plugin = simple_plugin()
dispatcher = Dispatcher()


class UnlinkUserCallback(CallbackPayload, prefix='unlink_user'):
    user_id: int


@plugin.setup()
async def create_max_bot() -> Bot:
    return Bot(
        token=Config.token,
        parse_mode=ParseMode.HTML,
        default_connection=DefaultConnectionProperties(connector=TCPConnector(ssl=False))
    )


@plugin.run()
async def start_max_bot(bot: Bot):
    await dispatcher.start_polling(bot)


@dispatcher.bot_started()
@transaction(1)
async def bot_started_handler(event: BotStarted):
    if not event.payload:
        return

    user = await User.get_by_id(auth.decode_user_id(event.payload))
    if not user:
        return

    user.max_id = event.from_user.user_id
    user.max_name = event.from_user.full_name
    user.add()

    await event.bot.send_message(
        event.chat_id,
        text=(
            f'✨ Привязываем MAX к аккаунту <b>«{user.name}»</b>!\n'
            'Отправь мне /start, чтобы подтвердить привязку аккаунта.'
        )
    )


@dispatcher.message_created(Command('start'))
async def start_command_handler(event: MessageCreated):
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.add(
        CallbackButton(
            text='❌ Отвязать',
            payload=UnlinkUserCallback(user_id=event.from_user.user_id).pack()
        )
    )

    await event.message.answer(
        '✨ Привязка MAX аккаунта подтверждена!\n'
        'Теперь все уведомления о новых отзывах и жалобах будут направляться сюда.',
        attachments=[inline_keyboard.as_markup()]
    )


@dispatcher.message_callback(UnlinkUserCallback.filter())
@transaction(1)
async def unlink_user_callback(event: MessageCallback, payload: UnlinkUserCallback):
    user = await User.get_by_id(payload.user_id)
    user.max_id = None
    user.max_name = None
    user.add()

    await event.message.edit(
        f'🛑 MAX успешно отвязан от аккаунта <b>«{user.name}»</b>.\n'
        'Вы больше не будете получать уведомления о новых отзывах и жалобах.'
    )





def get_max_bot() -> Bot:
    return DependenciesModule.get().resolve(Bot)
