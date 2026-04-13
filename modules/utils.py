import re
import json
import requests
from datetime import timedelta
from fastapi.responses import HTMLResponse
from modules import settings
from modules.database import PresenzaLab

# Initialize MQTT topics cache
MQTT_TOPICS = requests.get(settings.TLM_MQTT_TOPICS_URL, timeout=3).json()


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


def telemetry_login_html(callback_url: str, payload: dict) -> HTMLResponse:
    safe_url = json.dumps(callback_url)
    safe_payload = json.dumps(payload)
    with open("pages/telemetry_login.html") as f:
        res = f.read() \
                .replace("{callback_url}", safe_url) \
                .replace("{payload}", safe_payload)
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

    requests.post(f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage", data={
        "chat_id": chatId,
        "message_thread_id": topicId,
        "text": message,
        "parse_mode": "HTML"
    })


def notify_entry(presenza: PresenzaLab):
    msg = f"🎉 {presenza.email} has entered the lab"
    notify_telegram(msg)


def notify_exit(presenza: PresenzaLab):
    pretty_duration = pretty_time(timedelta_to_hours(presenza.duration))
    msg = f"💔 {presenza.email} has exited the lab ({pretty_duration})"
    notify_telegram(msg)


def mqtt_topics_to_emqx(topics: list) -> list:
    return [
        {
            "topic": re.sub(r'<[^>]+>', '+', topic["topic"]),
            "subscribe_roles": topic["subscribe_roles"],
            "publish_roles": topic["publish_roles"],
            "qos": topic["qos"]
        } for topic in topics
    ]
