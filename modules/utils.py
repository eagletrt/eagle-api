from datetime import timedelta
from fastapi.responses import HTMLResponse


def get_eagletrt_email(email: str) -> str:
    username = email.split('@')[0].lower()
    return f"{username}@eagletrt.it"


def orelab_entrata() -> HTMLResponse:
    with open("pages/entrata_lab.html") as f:
        res = f.read()
    return HTMLResponse(content=res, status_code=200)


def orelab_uscita(ore: float) -> HTMLResponse:
    emoji_dict = {
        0: "😐",
        1: "🙂",
        2: "😜",
        3: "😄",
        4: "😌",
        5: "😎"
    }
    ore = str(round(ore, 2))
    emoji = emoji_dict.get(int(ore), "🥹")

    with open("pages/uscita_lab.html") as f:
        res = f.read().replace("{ore}", ore).replace("happy_hour_emoji", emoji)
    return HTMLResponse(content=res, status_code=200)


def timedelta_to_hours(td: timedelta) -> float:
    return td.total_seconds() / 3600
