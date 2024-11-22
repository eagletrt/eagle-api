from datetime import timedelta
from fastapi.responses import HTMLResponse


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
