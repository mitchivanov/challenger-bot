from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from services.challenges import get_actual_challenges, get_challenge, get_or_create_user, update_user_phone, is_joined, join_challenge, get_user_by_telegram_id, create_user, get_challenge_events, create_report, get_challenge_points, get_user_report_days, get_event, get_user_event_reports, get_challenge_leaderboard
from utils.pagination import build_challenges_keyboard, build_events_keyboard, build_days_keyboard
from utils.phone import validate_phone
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

router = Router()

CHALLENGES_PER_PAGE = 8

logger = logging.getLogger(__name__)

class ReportPhotoFSM(StatesGroup):
    waiting_photos = State()

class EventReportPhotoFSM(StatesGroup):
    waiting_photos = State()

# Вспомогательные функции для навигации
async def safe_edit_message(call: CallbackQuery, text: str, reply_markup=None, parse_mode='HTML'):
    """Безопасное редактирование сообщения с fallback на новое сообщение"""
    try:
        await call.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.warning(f"Failed to edit message: {e}")
        await call.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)

async def safe_answer_or_edit(message_or_call, text: str, reply_markup=None, parse_mode='HTML'):
    """Универсальная функция для отправки/редактирования сообщения"""
    if hasattr(message_or_call, 'message'):  # Это CallbackQuery
        await safe_edit_message(message_or_call, text, reply_markup, parse_mode)
    else:  # Это Message
        await message_or_call.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)

async def send_challenge_card(message_or_call, challenge: dict, user: dict, joined: bool = None):
    """Унифицированная функция для отправки карточки челленджа"""
    if joined is None:
        joined = await is_joined(user['id'], challenge['id'])
    
    challenge_id = challenge['id']
    buttons = []
    
    if not joined:
        text = f"🏆 <b>{challenge['title']}</b>\n\n📝 {challenge['description']}\n\n📅 <b>Период:</b> {challenge['start_date']} — {challenge['end_date']}\n\n💡 <i>Присоединяйтесь к челленджу и начните зарабатывать очки!</i>"
        buttons.append([
            types.InlineKeyboardButton(text="✅ Вступить", callback_data=f"join:{challenge_id}")
        ])
        buttons.append([
            types.InlineKeyboardButton(text="◀️ К списку челленджей", callback_data="to_challenges")
        ])
    else:
        points = await get_challenge_points(user['id'], challenge_id)
        text = f"🏆 <b>{challenge['title']}</b>\n\n📝 {challenge['description']}\n\n📅 <b>Период:</b> {challenge['start_date']} — {challenge['end_date']}\n\n⭐ <b>Ваши очки:</b> {points} 🏅"
        buttons.extend([
            [
                types.InlineKeyboardButton(text="🎯 Мероприятия", callback_data=f"events:{challenge_id}:0"),
                types.InlineKeyboardButton(text="📋 Отчёты", callback_data=f"reports:{challenge_id}:0")
            ],
            [types.InlineKeyboardButton(text="📊 Статистика", callback_data=f"stats:{challenge_id}")],
            [types.InlineKeyboardButton(text="◀️ К списку челленджей", callback_data="to_challenges")]
        ])
    
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await safe_answer_or_edit(message_or_call, text, kb, 'HTML')

@router.message(Command('start'))
async def start_handler(message: types.Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        text = f"🎉 <b>С возвращением, {message.from_user.full_name}!</b>\n\n🚀 Готовы к новым челленджам?"
    else:
        await create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username
        )
        text = f"👋 <b>Добро пожаловать, {message.from_user.full_name}!</b>\n\n✅ Вы успешно зарегистрированы!\n\n🎯 Теперь вы можете участвовать в челленджах и зарабатывать очки!"
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🏆 Челленджи", callback_data="to_challenges")]
        ]
    )
    await message.answer(text, reply_markup=kb, parse_mode='HTML')

@router.callback_query(lambda c: c.data == "to_challenges")
async def to_challenges_callback(call: types.CallbackQuery):
    challenges = await get_actual_challenges()
    if not challenges:
        text = "🤷‍♂️ <b>Нет доступных челленджей</b>\n\n📅 На сегодня активных челленджей не найдено.\n\n🔄 Попробуйте позже!"
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🔄 Обновить", callback_data="to_challenges")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer()
        return
    
    kb = build_challenges_keyboard(challenges, page=0, per_page=CHALLENGES_PER_PAGE)
    text = "🏆 <b>Доступные челленджи</b>\n\n🎯 Выберите челлендж для участия:"
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.message(Command('challenges'))
async def challenges_handler(message: types.Message):
    challenges = await get_actual_challenges()
    if not challenges:
        text = "🤷‍♂️ <b>Нет доступных челленджей</b>\n\n📅 На сегодня активных челленджей не найдено.\n\n🔄 Попробуйте позже!"
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🔄 Обновить", callback_data="to_challenges")]
            ]
        )
        await message.answer(text, reply_markup=kb, parse_mode='HTML')
        return
    
    kb = build_challenges_keyboard(challenges, page=0, per_page=CHALLENGES_PER_PAGE)
    text = "🏆 <b>Доступные челленджи</b>\n\n🎯 Выберите челлендж для участия:"
    await message.answer(text, reply_markup=kb, parse_mode='HTML')

@router.callback_query(lambda c: c.data.startswith('ch_page:'))
async def page_callback(call: CallbackQuery):
    page = int(call.data.split(':')[1])
    challenges = await get_actual_challenges()
    kb = build_challenges_keyboard(challenges, page=page, per_page=CHALLENGES_PER_PAGE)
    text = "🏆 <b>Доступные челленджи</b>\n\n🎯 Выберите челлендж для участия:"
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('challenge:'))
async def challenge_detail_callback(call: CallbackQuery):
    challenge_id = int(call.data.split(':')[1])
    challenge = await get_challenge(challenge_id)
    user = await get_or_create_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username
    )
    joined = await is_joined(user['id'], challenge_id)
    await send_challenge_card(call, challenge, user, joined)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('join:'))
async def join_challenge_callback(call: CallbackQuery, state):
    challenge_id = int(call.data.split(':')[1])
    challenge = await get_challenge(challenge_id)
    user = await get_or_create_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username
    )
    
    if challenge.get('requires_phone') and not user.get('phone_number'):
        # Запросить номер телефона через кнопку
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        text = f"📱 <b>Требуется номер телефона</b>\n\n🏆 <b>Челлендж:</b> {challenge['title']}\n\n💡 Для участия в этом челлендже необходимо указать номер телефона.\n\n👆 Нажмите кнопку ниже, чтобы поделиться контактом:"
        await safe_edit_message(call, text)
        await call.message.answer("📱 Поделитесь своим контактом:", reply_markup=kb)
        await state.set_state("awaiting_phone")
        await state.update_data(user_id=user['id'], challenge_id=challenge_id)
        await call.answer()
        return
    
    try:
        await join_challenge(user['id'], challenge_id)
        success_text = f"🎉 <b>Поздравляем!</b>\n\n✅ Вы успешно присоединились к челленджу!\n\n🏆 <b>«{challenge['title']}»</b>\n\n🚀 Теперь вы можете участвовать в мероприятиях и отправлять отчёты!"
        
        # Показываем сообщение об успехе
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🎯 Начать участие", callback_data=f"challenge:{challenge_id}")]
            ]
        )
        await safe_edit_message(call, success_text, kb)
        await call.answer("🎉 Добро пожаловать в челлендж!")
        
        # Через 2 секунды показываем карточку челленджа
        import asyncio
        await asyncio.sleep(2)
        await send_challenge_card(call, challenge, user, joined=True)
        
    except Exception as e:
        logger.error(f"Ошибка при присоединении к челленджу: {e}")
        error_text = f"❌ <b>Ошибка присоединения</b>\n\n🔧 Не удалось присоединиться к челленджу.\n\n🔄 Попробуйте позже."
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🔄 Попробовать снова", callback_data=f"join:{challenge_id}")],
                [types.InlineKeyboardButton(text="◀️ К челленджу", callback_data=f"challenge:{challenge_id}")]
    ]
        )
        await safe_edit_message(call, error_text, kb)
    await call.answer()

@router.message(lambda m: m.contact is not None or (m.text and validate_phone(m.text)))
async def phone_handler(message: types.Message, state):
    data = await state.get_data()
    user_id = data.get('user_id')
    challenge_id = data.get('challenge_id')
    phone = message.contact.phone_number if message.contact else message.text
    
    if not validate_phone(phone):
        await message.answer("❌ <b>Некорректный номер</b>\n\n📱 Пожалуйста, отправьте корректный номер телефона или воспользуйтесь кнопкой 'Поделиться контактом'.", parse_mode='HTML')
        return
    
    try:
        await update_user_phone(user_id, phone)
        await join_challenge(user_id, challenge_id)
        await message.answer("✅ <b>Отлично!</b>\n\n📱 Номер телефона сохранен!\n🎉 Вы успешно присоединились к челленджу!", reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
        
        challenges = await get_actual_challenges()
        challenge = next((c for c in challenges if c['id'] == challenge_id), None)
        if not challenge:
            await message.answer('❌ Челлендж не найден', parse_mode='HTML')
        return
        
        user = {"id": user_id}  # Создаем объект пользователя для функции
    # Отправляем карточку с кнопками и очками
        await send_challenge_card(message, challenge, user, joined=True)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при обработке телефона: {e}")
        await message.answer("❌ <b>Ошибка</b>\n\n🔧 Произошла ошибка при сохранении данных.\n\n🔄 Попробуйте позже.", reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
        await state.clear()

@router.callback_query(lambda c: c.data.startswith('events:'))
async def events_catalog_callback(call: CallbackQuery):
    _, challenge_id, page = call.data.split(':')
    challenge_id = int(challenge_id)
    page = int(page)
    events = await get_challenge_events(challenge_id)
    
    if not events:
        text = "🤷‍♂️ <b>Нет мероприятий</b>\n\n📅 Для этого челленджа пока нет запланированных мероприятий."
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="◀️ Назад к челленджу", callback_data=f"challenge:{challenge_id}")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer()
        return
    
    kb = build_events_keyboard(events, page=page, per_page=8, challenge_id=challenge_id)
    text = f"🎯 <b>Мероприятия челленджа</b>\n\n📋 Найдено мероприятий: {len(events)}\n\n👆 Выберите мероприятие:"
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('ev_page:'))
async def events_page_callback(call: CallbackQuery):
    _, challenge_id, page = call.data.split(':')
    challenge_id = int(challenge_id)
    page = int(page)
    events = await get_challenge_events(challenge_id)
    kb = build_events_keyboard(events, page=page, per_page=8, challenge_id=challenge_id)
    text = f"🎯 <b>Мероприятия челленджа</b>\n\n📋 Найдено мероприятий: {len(events)}\n\n👆 Выберите мероприятие:"
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('reports:'))
async def reports_catalog_callback(call: CallbackQuery):
    _, challenge_id, page = call.data.split(':')
    challenge_id = int(challenge_id)
    page = int(page)
    challenge = await get_challenge(challenge_id)
    user = await get_or_create_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username
    )
    report_days = await get_user_report_days(user['id'], challenge_id)
    kb = build_days_keyboard(challenge['start_date'], challenge['end_date'], page=page, per_page=8, challenge_id=challenge_id, report_days=report_days)
    
    completed_reports = len(report_days)
    text = f"📋 <b>Ваши отчёты</b>\n\n✅ Выполнено отчётов: <b>{completed_reports}</b>\n\n📅 Выберите день для отчёта:"
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('day_page:'))
async def days_page_callback(call: CallbackQuery):
    _, challenge_id, page = call.data.split(':')
    challenge_id = int(challenge_id)
    page = int(page)
    challenge = await get_challenge(challenge_id)
    user = await get_or_create_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username
    )
    report_days = await get_user_report_days(user['id'], challenge_id)
    kb = build_days_keyboard(challenge['start_date'], challenge['end_date'], page=page, per_page=8, challenge_id=challenge_id, report_days=report_days)
    
    completed_reports = len(report_days)
    text = f"📋 <b>Ваши отчёты</b>\n\n✅ Выполнено отчётов: <b>{completed_reports}</b>\n\n📅 Выберите день для отчёта:"
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('report_day:'))
async def report_day_callback(call: CallbackQuery, state: FSMContext):
    _, challenge_id, day = call.data.split(':')
    challenge_id = int(challenge_id)
    challenge = await get_challenge(challenge_id)
    user = await get_or_create_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username
    )
    
    # Дополнительная проверка отчетов (обновленная)
    report_days = await get_user_report_days(user['id'], challenge_id)
    logger.info(f"User {user['id']} report days for challenge {challenge_id}: {report_days}")
    
    if day in report_days:
        text = f"✅ <b>Отчёт уже отправлен</b>\n\n📅 За дату <b>{day}</b> отчёт уже был отправлен.\n\n🎯 Выберите другой день для отчёта."
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="◀️ К календарю отчётов", callback_data=f"reports:{challenge_id}:0")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer()
        return
    
    required_photos = challenge.get('required_photos', 1)
    await state.set_state(ReportPhotoFSM.waiting_photos)
    await state.update_data(challenge_id=challenge_id, day=day, photos=[], required_photos=required_photos, call_message_id=call.message.message_id)
    
    text = f"📸 <b>Отправка отчёта</b>\n\n📅 <b>Дата:</b> {day}\n📋 <b>Челлендж:</b> {challenge['title']}\n\n📷 Пожалуйста, отправьте <b>{required_photos}</b> фото для отчёта."
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"reports:{challenge_id}:0")]
        ]
    )
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.message(ReportPhotoFSM.waiting_photos)
async def handle_report_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    required_photos = data.get('required_photos', 1)
    challenge_id = data.get('challenge_id')
    day = data.get('day')
    call_message_id = data.get('call_message_id')
    
    if message.photo:
        # Проверяем, не превышен ли лимит фотографий
        if len(photos) >= required_photos:
            try:
                await message.delete()
            except:
                pass
            # Отправляем предупреждение
            warning_text = f"⚠️ <b>Лимит фотографий достигнут</b>\n\n📷 Вы уже отправили максимальное количество фото ({required_photos}).\n\n✅ Ваш отчёт обрабатывается..."
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=call_message_id,
                    text=warning_text,
                    parse_mode='HTML'
                )
            except:
                pass
            return
            
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)
    
        # Удаляем предыдущее сообщение пользователя
        try:
            await message.delete()
        except:
            pass
    
    remaining = required_photos - len(photos)
    if remaining > 0:
        # Обновляем сообщение с прогрессом
        try:
            progress_text = f"📸 <b>Отправка отчёта</b>\n\n📅 <b>Дата:</b> {day}\n\n📷 Получено фото: <b>{len(photos)}/{required_photos}</b>\n\n⏳ Осталось загрузить: <b>{remaining}</b> фото"
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"reports:{challenge_id}:0")]
                ]
            )
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=call_message_id,
                text=progress_text,
                reply_markup=kb,
                parse_mode='HTML'
            )
        except:
            pass
        return
    
    # Все фото собраны, обрабатываем отчет
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    
    try:
        logger.info(f"Пользователь {user['id']} отправляет отчёт: challenge_id={challenge_id}, day={day}, photos={photos}")
        
        # Показываем сообщение о обработке
        processing_text = f"⏳ <b>Обработка отчёта...</b>\n\n📅 <b>Дата:</b> {day}\n📷 <b>Фото:</b> {len(photos)}\n\n🔄 Сохраняем ваш отчёт..."
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=call_message_id,
                text=processing_text,
                parse_mode='HTML'
            )
        except:
            pass
        
        # Создаем отчет с фотографиями
        report = await create_report(
            user_id=user['id'],
            text_content=f"Отчет за {day}",
            challenge_id=challenge_id,
            report_date=day,
            photos=photos,
            bot=message.bot
        )
        
        logger.info(f"Ответ от бэкенда на создание отчёта: {report}")
        if report and report.get('id'):
            # Получаем и показываем баланс очков
            points = await get_challenge_points(user['id'], challenge_id)
            success_text = f"✅ <b>Отчёт успешно отправлен!</b>\n\n📅 <b>Дата:</b> {day}\n📷 <b>Фото:</b> {len(photos)}\n⭐ <b>Ваши очки:</b> {points} 🏅"
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="📋 К отчётам", callback_data=f"reports:{challenge_id}:0")],
                    [types.InlineKeyboardButton(text="🏆 К челленджу", callback_data=f"challenge:{challenge_id}")]
                ]
            )
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=call_message_id,
                    text=success_text,
                    reply_markup=kb,
                    parse_mode='HTML'
                )
            except:
                await message.answer(success_text, reply_markup=kb, parse_mode='HTML')
        else:
            logger.error(f"Бэкенд вернул неожиданный ответ: {report}")
            error_text = "❌ <b>Ошибка сохранения</b>\n\n🔧 Произошла ошибка при сохранении отчета.\n\n🔄 Попробуйте позже."
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="📋 К отчётам", callback_data=f"reports:{challenge_id}:0")]
                ]
            )
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=call_message_id,
                    text=error_text,
                    reply_markup=kb,
                    parse_mode='HTML'
                )
            except:
                await message.answer(error_text, reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        import traceback
        logger.error(f"Ошибка при создании отчёта: {e}\n{traceback.format_exc()}")
        
        error_msg = str(e)
        if "Report already exists" in error_msg or "уже отправлен" in error_msg:
            error_text = "⚠️ <b>Отчёт уже существует</b>\n\n📅 Отчёт за этот день уже был отправлен."
        else:
            error_text = "❌ <b>Ошибка отправки</b>\n\n🔧 Произошла ошибка при сохранении отчета.\n\n🔄 Попробуйте позже."
        
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="📋 К отчётам", callback_data=f"reports:{challenge_id}:0")]
            ]
        )
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=call_message_id,
                text=error_text,
                reply_markup=kb,
                parse_mode='HTML'
            )
        except:
            await message.answer(error_text, reply_markup=kb, parse_mode='HTML')
    
    await state.clear()

@router.callback_query(lambda c: c.data.startswith('event_detail:'))
async def event_detail_callback(call: CallbackQuery):
    event_id = int(call.data.split(':')[1])
    event = await get_event(event_id)
    if not event:
        text = "❌ <b>Мероприятие не найдено</b>\n\n🔍 Запрашиваемое мероприятие не существует или было удалено."
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="◀️ Назад", callback_data=f"events:{event.get('challenge_id', 0)}:0")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer()
        return
    
    user = await get_or_create_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username
    )
    
    # Проверяем, участвует ли пользователь в челлендже
    joined = await is_joined(user['id'], event['challenge_id'])
    if not joined:
        text = "🚫 <b>Доступ ограничен</b>\n\n💡 Вы не участвуете в этом челлендже.\n\n✅ Сначала присоединитесь к челленджу!"
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🏆 Перейти к челленджу", callback_data=f"challenge:{event['challenge_id']}")],
                [types.InlineKeyboardButton(text="◀️ К мероприятиям", callback_data=f"events:{event['challenge_id']}:0")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer()
        return
    
    # Проверяем, есть ли уже отчет пользователя для этого мероприятия
    event_reports = await get_user_event_reports(user['id'], event_id)
    has_report = len(event_reports) > 0
    
    text = f"🎯 <b>{event['title']}</b>\n\n📝 {event['description']}\n\n📅 <b>Дата:</b> {event['date']}\n⭐ <b>Баллов за отчет:</b> {event['points_per_report']} 🏅\n📸 <b>Требуется фото:</b> {event['required_photos']}"
    
    buttons = []
    if has_report:
        text += "\n\n✅ <b>Ваш отчет уже отправлен!</b>"
    else:
        buttons.append([types.InlineKeyboardButton(text="📋 Отправить отчет", callback_data=f"event_report:{event_id}")])
    
    buttons.append([types.InlineKeyboardButton(text="◀️ К мероприятиям", callback_data=f"events:{event['challenge_id']}:0")])
    
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('event_report:'))
async def event_report_callback(call: CallbackQuery, state: FSMContext):
    event_id = int(call.data.split(':')[1])
    event = await get_event(event_id)
    if not event:
        text = "❌ <b>Мероприятие не найдено</b>\n\n🔍 Запрашиваемое мероприятие не существует или было удалено."
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="◀️ К мероприятиям", callback_data=f"events:{event.get('challenge_id', 0)}:0")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer()
        return
    
    user = await get_or_create_user(
        telegram_id=call.from_user.id,
        username=call.from_user.username
    )
    
    # Дополнительная проверка отчетов (обновленная)
    event_reports = await get_user_event_reports(user['id'], event_id)
    logger.info(f"User {user['id']} has {len(event_reports)} reports for event {event_id} before starting FSM")
    
    if event_reports:
        text = f"✅ <b>Отчёт уже отправлен</b>\n\n🎯 <b>Мероприятие:</b> {event['title']}\n\n📅 Вы уже отправили отчет для этого мероприятия."
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="◀️ К мероприятиям", callback_data=f"events:{event['challenge_id']}:0")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer()
        return
    
    required_photos = event.get('required_photos', 1)
    await state.set_state(EventReportPhotoFSM.waiting_photos)
    await state.update_data(event_id=event_id, photos=[], required_photos=required_photos, call_message_id=call.message.message_id)
    
    text = f"📸 <b>Отправка отчёта по мероприятию</b>\n\n🎯 <b>Мероприятие:</b> {event['title']}\n📅 <b>Дата:</b> {event['date']}\n⭐ <b>Баллы:</b> {event['points_per_report']} 🏅\n\n📷 Пожалуйста, отправьте <b>{required_photos}</b> фото для отчёта."
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"events:{event['challenge_id']}:0")]
        ]
    )
    await safe_edit_message(call, text, kb)
    await call.answer()

@router.message(EventReportPhotoFSM.waiting_photos)
async def handle_event_report_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    required_photos = data.get('required_photos', 1)
    event_id = data.get('event_id')
    call_message_id = data.get('call_message_id')
    
    if message.photo:
        # Проверяем, не превышен ли лимит фотографий
        if len(photos) >= required_photos:
            try:
                await message.delete()
            except:
                pass
            # Отправляем предупреждение
            event = await get_event(event_id)
            warning_text = f"⚠️ <b>Лимит фотографий достигнут</b>\n\n📷 Вы уже отправили максимальное количество фото ({required_photos}) для мероприятия '{event['title'] if event else 'Неизвестное'}'.\n\n✅ Ваш отчёт обрабатывается..."
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=call_message_id,
                    text=warning_text,
                    parse_mode='HTML'
                )
            except:
                pass
            return
            
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)
        
        # Удаляем предыдущее сообщение пользователя
        try:
            await message.delete()
        except:
            pass
    
    remaining = required_photos - len(photos)
    if remaining > 0:
        # Обновляем сообщение с прогрессом
        try:
            event = await get_event(event_id)
            progress_text = f"📸 <b>Отправка отчёта по мероприятию</b>\n\n🎯 <b>Мероприятие:</b> {event['title']}\n\n📷 Получено фото: <b>{len(photos)}/{required_photos}</b>\n\n⏳ Осталось загрузить: <b>{remaining}</b> фото"
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"events:{event['challenge_id']}:0")]
                ]
            )
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=call_message_id,
                text=progress_text,
                reply_markup=kb,
                parse_mode='HTML'
            )
        except:
            pass
        return
    
    # Все фото собраны, обрабатываем отчет
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )
    
    event = await get_event(event_id)
    if not event:
        error_text = "❌ <b>Мероприятие не найдено</b>\n\n🔍 Мероприятие было удалено или не существует."
        await message.answer(error_text, parse_mode='HTML')
        await state.clear()
        return
    
    try:
        logger.info(f"Пользователь {user['id']} отправляет отчёт для мероприятия: event_id={event_id}, photos={photos}")
        
        # Показываем сообщение о обработке
        processing_text = f"⏳ <b>Обработка отчёта...</b>\n\n🎯 <b>Мероприятие:</b> {event['title']}\n📷 <b>Фото:</b> {len(photos)}\n\n🔄 Сохраняем ваш отчёт..."
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=call_message_id,
                text=processing_text,
                parse_mode='HTML'
            )
        except:
            pass
        
        # Создаем отчет с фотографиями для мероприятия
        report = await create_report(
            user_id=user['id'],
            text_content=f"Отчет по мероприятию '{event['title']}'",
            challenge_id=event['challenge_id'],  # Связываем с челленджем для начисления очков
            event_id=event_id,
            report_date=event['date'],
            photos=photos,
            bot=message.bot
        )
        
        logger.info(f"Ответ от бэкенда на создание отчёта для мероприятия: {report}")
        if report and report.get('id'):
            # Получаем и показываем баланс очков за челлендж
            points = await get_challenge_points(user['id'], event['challenge_id'])
            success_text = f"✅ <b>Отчёт успешно отправлен!</b>\n\n🎯 <b>Мероприятие:</b> {event['title']}\n📷 <b>Фото:</b> {len(photos)}\n⭐ <b>Ваши очки за челлендж:</b> {points} 🏅"
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🎯 К мероприятиям", callback_data=f"events:{event['challenge_id']}:0")],
                    [types.InlineKeyboardButton(text="🏆 К челленджу", callback_data=f"challenge:{event['challenge_id']}")]
                ]
            )
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=call_message_id,
                    text=success_text,
                    reply_markup=kb,
                    parse_mode='HTML'
                )
            except:
                await message.answer(success_text, reply_markup=kb, parse_mode='HTML')
        else:
            logger.error(f"Бэкенд вернул неожиданный ответ: {report}")
            error_text = "❌ <b>Ошибка сохранения</b>\n\n🔧 Произошла ошибка при сохранении отчета.\n\n🔄 Попробуйте позже."
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🎯 К мероприятиям", callback_data=f"events:{event['challenge_id']}:0")]
                ]
            )
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=call_message_id,
                    text=error_text,
                    reply_markup=kb,
                    parse_mode='HTML'
                )
            except:
                await message.answer(error_text, reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        import traceback
        logger.error(f"Ошибка при создании отчёта для мероприятия: {e}\n{traceback.format_exc()}")
        
        error_msg = str(e)
        if "Report already exists" in error_msg or "уже отправлен" in error_msg:
            error_text = "⚠️ <b>Отчёт уже существует</b>\n\n📅 Отчёт для этого мероприятия уже был отправлен."
        else:
            error_text = "❌ <b>Ошибка отправки</b>\n\n🔧 Произошла ошибка при сохранении отчета.\n\n🔄 Попробуйте позже."
        
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🎯 К мероприятиям", callback_data=f"events:{event['challenge_id']}:0")]
            ]
        )
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=call_message_id,
                text=error_text,
                reply_markup=kb,
                parse_mode='HTML'
            )
        except:
            await message.answer(error_text, reply_markup=kb, parse_mode='HTML')
    
    await state.clear() 

@router.callback_query(lambda c: c.data.startswith('stats:'))
async def stats_callback(call: CallbackQuery):
    challenge_id = int(call.data.split(':')[1])
    
    try:
        # Получаем информацию о челлендже и пользователе
        challenge = await get_challenge(challenge_id)
        user = await get_or_create_user(
            telegram_id=call.from_user.id,
            username=call.from_user.username
        )
        
        if not challenge:
            text = "❌ <b>Челлендж не найден</b>\n\n🔍 Запрашиваемый челлендж не существует или был удален."
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="◀️ К списку челленджей", callback_data="to_challenges")]
                ]
            )
            await safe_edit_message(call, text, kb)
            await call.answer()
            return
        
        # Проверяем, участвует ли пользователь в челлендже
        joined = await is_joined(user['id'], challenge_id)
        if not joined:
            text = "🚫 <b>Доступ ограничен</b>\n\n💡 Вы не участвуете в этом челлендже.\n\n✅ Присоединитесь, чтобы увидеть статистику!"
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="🏆 Перейти к челленджу", callback_data=f"challenge:{challenge_id}")],
                    [types.InlineKeyboardButton(text="◀️ К списку челленджей", callback_data="to_challenges")]
                ]
            )
            await safe_edit_message(call, text, kb)
            await call.answer()
            return
        
        # Получаем рейтинг участников
        leaderboard = await get_challenge_leaderboard(challenge_id)
        
        if not leaderboard:
            text = f"📊 <b>Статистика челленджа</b>\n<b>«{challenge['title']}»</b>\n\n🤷‍♂️ В этом челлендже пока нет участников."
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="◀️ Назад к челленджу", callback_data=f"challenge:{challenge_id}")]
                ]
            )
            await safe_edit_message(call, text, kb)
            await call.answer()
            return
        
        # Находим позицию текущего пользователя
        user_position = None
        user_points = None
        for i, participant in enumerate(leaderboard, 1):
            if participant['user_id'] == user['id']:
                user_position = i
                user_points = participant['points']
                break
        
        # Формируем текст с рейтингом
        text = f"📊 <b>Рейтинг участников</b>\n🏆 <b>«{challenge['title']}»</b>\n\n"
        
        # Показываем информацию о текущем пользователе
        if user_position:
            position_emoji = "🥇" if user_position == 1 else "🥈" if user_position == 2 else "🥉" if user_position == 3 else "📍"
            text += f"{position_emoji} <b>Ваша позиция: {user_position} место ({user_points} очков)</b>\n\n"
        
        # Показываем топ-10
        text += "🏆 <b>Топ участников:</b>\n"
        for i, participant in enumerate(leaderboard[:10], 1):  # Показываем топ-10
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            username = participant['username'] or "Аноним"
            points = participant['points']
            
            # Выделяем текущего пользователя
            if participant['user_id'] == user['id']:
                text += f"<b>{medal} {username} — {points} очков</b>\n"
            else:
                text += f"{medal} {username} — {points} очков\n"
        
        if len(leaderboard) > 10:
            text += f"\n... и ещё {len(leaderboard) - 10} участников"
        
        text += f"\n\n👥 <b>Всего участников:</b> {len(leaderboard)}"
        
        # Кнопки
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="🔄 Обновить", callback_data=f"stats:{challenge_id}")],
                [types.InlineKeyboardButton(text="◀️ Назад к челленджу", callback_data=f"challenge:{challenge_id}")]
            ]
        )
        
        await safe_edit_message(call, text, kb)
        await call.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        text = "❌ <b>Ошибка загрузки</b>\n\n🔧 Произошла ошибка при загрузке статистики.\n\n🔄 Попробуйте позже."
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="◀️ Назад к челленджу", callback_data=f"challenge:{challenge_id}")]
            ]
        )
        await safe_edit_message(call, text, kb)
        await call.answer() 

# Обработчик отмены для любых FSM состояний
@router.callback_query(lambda c: c.data.startswith(('reports:', 'events:')) and '/cancel' not in c.data)
async def cancel_fsm_handler(call: CallbackQuery, state: FSMContext):
    """Автоматическая отмена FSM состояний при навигации"""
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        logger.info(f"Auto-cleared FSM state during navigation: {current_state}") 