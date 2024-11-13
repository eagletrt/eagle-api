from datetime import timedelta
from fastapi.responses import HTMLResponse


def get_eagletrt_email(email: str) -> str:
    username = email.split('@')[0].lower()
    return f"{username}@eagletrt.it"


def orelab_entrata() -> HTMLResponse:
    res = f"""
    <html>
    <head>
        <title>Entrata Laboratorio</title>
    </head>
    <body>
        <h1>Benvenuto/a :)</h1>
        <p>La tua entrata è stata registrata correttamente.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=res, status_code=200)


def orelab_uscita(ore: float) -> HTMLResponse:
    res = f"""
    <html>
    <head>
        <title>Uscita Laboratorio</title>
    </head>
    <body>
        <h1>Ciao :(</h1>
        <p>La tua uscita è stata registrata correttamente.</p>
        <p>Sei rimasto/a in laboratorio per {ore:.2f} ore.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=res, status_code=200)


def timedelta_to_hours(td: timedelta) -> float:
    return td.total_seconds() / 3600
