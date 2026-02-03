import requests
from datetime import timedelta
from fastapi.responses import HTMLResponse
from modules import settings
from modules.db_ore import PresenzaLab

ROLE_TO_GOOGLE_GROUP = {
    "RP": "responsibles@groups.eagletrt.it",
    "RT": "racingteam@groups.eagletrt.it",
    "PM": "project-managers@groups.eagletrt.it",
    "HR": "human-resources@groups.eagletrt.it"
}


def get_eagletrt_email(email: str) -> str:
    username = email.split('@')[0].lower()
    return f"{username}@eagletrt.it"


def timedelta_to_hours(td: timedelta) -> float:
    return td.total_seconds() / 3600


def pretty_time(hours: float) -> str:
    int_hours = int(hours)
    minutes = int((hours - int_hours) * 60)
    if hours < 1:
        return f"{minutes} minuti"
    return f"{int_hours}h {minutes}min"


def orelab_entrata(ore_oggi: float) -> HTMLResponse:
    ore_oggi = pretty_time(ore_oggi)
    with open("pages/entrata_lab.html") as f:
        res = f.read() \
                .replace("{ore_oggi}", ore_oggi)
    return HTMLResponse(content=res, status_code=200)


def orelab_uscita(ore: float, ore_oggi: float) -> HTMLResponse:
    emoji_dict = {
        0: "😐",
        1: "🙂",
        2: "😜",
        3: "😄",
        4: "😌",
        5: "😎"
    }
    emoji = emoji_dict.get(int(ore_oggi // 1), "🥹")
    ore = pretty_time(ore)
    ore_oggi = pretty_time(ore_oggi)

    with open("pages/uscita_lab.html") as f:
        res = f.read() \
                .replace("{ore}", ore) \
                .replace("{ore_oggi}", ore_oggi) \
                .replace("{happy_hour_emoji}", emoji)
    return HTMLResponse(content=res, status_code=200)


def notify_telegram(message: str):
    chatId = settings.LOG_CHAT_ID
    topicId = settings.LOG_TOPIC_ID
    if chatId == 0 or topicId == 0:
        return

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chatId,
        "message_thread_id": topicId,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


def notify_entry(presenza: PresenzaLab):
    msg = f"🎉 {presenza.email} has entered the lab"
    notify_telegram(msg)


def notify_exit(presenza: PresenzaLab):
    pretty_duration = pretty_time(timedelta_to_hours(presenza.duration))
    msg = f"💔 {presenza.email} has exited the lab ({pretty_duration})"
    notify_telegram(msg)


def telemetry_role_translation(role: str) -> int:
    roles = {
        "admin": 0,
        "editor": 1,
        "viewer": 2
    }
    return roles.get(role, -1)


def generate_temp_password() -> str:
    import string
    import secrets

    length = 16
    characters = string.ascii_letters + string.digits + "!@#*"
    while True:
        password = ''.join(secrets.choice(characters) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password)):
            return password
