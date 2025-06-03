from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

def build_challenges_keyboard(challenges, page=0, per_page=8):
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_challenges = challenges[start:end]
    for c in page_challenges:
        builder.row(
            InlineKeyboardButton(
                text=f"🏆 {c['title']}",
                callback_data=f"challenge:{c['id']}"
            )
        )
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text='⬅️', callback_data=f'ch_page:{page-1}'))
    if end < len(challenges):
        nav_buttons.append(InlineKeyboardButton(text='➡️', callback_data=f'ch_page:{page+1}'))
    if nav_buttons:
        builder.row(*nav_buttons)
    return builder.as_markup()

def build_events_keyboard(events, page=0, per_page=8, challenge_id=None):
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_events = events[start:end]
    for e in page_events:
        builder.row(
            InlineKeyboardButton(
                text=f"🎯 {e['title']}",
                callback_data=f"event_detail:{e['id']}"
            )
        )
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text='⬅️', callback_data=f'ev_page:{challenge_id}:{page-1}'))
    if end < len(events):
        nav_buttons.append(InlineKeyboardButton(text='➡️', callback_data=f'ev_page:{challenge_id}:{page+1}'))
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text='◀️ Назад к челленджу', callback_data=f'challenge:{challenge_id}'))
    return builder.as_markup()

def build_days_keyboard(start_date, end_date, page=0, per_page=8, challenge_id=None, report_days=None):
    builder = InlineKeyboardBuilder()
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    days = [(start_dt + timedelta(days=i)).date() for i in range((end_dt - start_dt).days + 1)]
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_days = days[start_idx:end_idx]
    report_days = set(report_days or [])
    for d in page_days:
        d_str = str(d)
        if d_str in report_days:
            mark = '✅'
            button_text = f"{mark} {d_str}"
        else:
            mark = '📅'
            button_text = f"{mark} {d_str}"
        builder.row(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"report_day:{challenge_id}:{d_str}"
            )
        )
    nav_buttons = []
    if start_idx > 0:
        nav_buttons.append(InlineKeyboardButton(text='⬅️', callback_data=f'day_page:{challenge_id}:{page-1}'))
    if end_idx < len(days):
        nav_buttons.append(InlineKeyboardButton(text='➡️', callback_data=f'day_page:{challenge_id}:{page+1}'))
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text='◀️ Назад к челленджу', callback_data=f'challenge:{challenge_id}'))
    return builder.as_markup() 