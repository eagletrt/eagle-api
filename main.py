from threading import Lock
from datetime import datetime, timedelta
from pony.orm import db_session, desc, select
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules import settings, utils
from modules.db_ore import PresenzaLab
from modules.models import UserUpdates
from modules.google_admin import GoogleAdminAPI

app = FastAPI()
security = HTTPBearer()
oreLock = Lock()
google = GoogleAdminAPI(
    service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON,
    impersonate_admin_email=settings.GOOGLE_IMPERSONATE_ADMIN_EMAIL
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")


@app.post("/updateUsers", dependencies=[Depends(verify_token)])
async def update_users(data: UserUpdates) -> dict:
    existing_users = google.list_all_users()
    to_create = [u for u in data.users if utils.get_eagletrt_email(u.email) not in existing_users]

    for user in to_create:
        google.try_create_new_user(user, settings.GOOGLE_NEW_USER_PASSWORD)

    return {"status": "success", "message": f"{len(to_create)} users created successfully"}


@app.get("/userGroups", dependencies=[Depends(verify_token)])
async def list_user_groups(email: str) -> list[str]:
    return google.list_user_groups(email)


@app.get("/presenzaLab", response_class=HTMLResponse, response_model=None)
async def presenzaLab(x_email: str = Header(default=None)):
    if not x_email:
        raise HTTPException(status_code=400, detail="Missing authentication")

    with oreLock:
        with db_session:
            presenze = select(p for p in PresenzaLab if p.email == x_email)
            latest = presenze.order_by(desc(PresenzaLab.entrata)).first()
            today = presenze.filter(
                lambda p: p.entrata >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            )

            ore = utils.timedelta_to_hours(latest.duration) if latest else 0
            ore_oggi = sum([utils.timedelta_to_hours(p.duration) for p in list(today)]) if latest else 0

            if latest and latest.isActive:
                return utils.orelab_uscita(ore, ore_oggi)
            else:
                return utils.orelab_entrata(ore_oggi)


@app.post("/presenzaLab/confirm", response_class=HTMLResponse, response_model=None)
async def presenzaLab_confirm(x_email: str = Header(default=None)):
    if not x_email:
        raise HTTPException(status_code=400, detail="Missing authentication")

    with oreLock:
        with db_session:
            latest = PresenzaLab.select(lambda p: p.email == x_email).order_by(desc(PresenzaLab.entrata)).first()
            if latest and latest.isActive:
                latest.uscita = datetime.now()
                return HTMLResponse(content="Uscita confermata.", status_code=200)
            else:
                latest = PresenzaLab(email=x_email, entrata=datetime.now())
                return HTMLResponse(content="Entrata confermata.", status_code=200)


@app.get("/presenzaLab/resetore")
async def presenzaLab_resetore(x_email: str = Header(default=None)):
    if not x_email:
        raise HTTPException(status_code=400, detail="Missing authentication")

    with oreLock:
        with db_session:
            latest = PresenzaLab.select(lambda p: p.email == x_email).order_by(desc(PresenzaLab.entrata)).first()
            if latest and latest.isActive:
                latest.delete()
                return RedirectResponse(url="https://api.eagletrt.it/api/v2/presenzaLab", status_code=302)


@app.get("/tecsLinkOre")
async def tecs_link_ore(x_email: str = Header(default=None)):
    if not x_email:
        raise HTTPException(status_code=400, detail="Missing authentication")

    username = x_email.split('@')[0].replace('.', '___')
    return RedirectResponse(url=f"https://t.me/ThonisNomasbot?start={username}", status_code=302)


@app.get("/oreLab")
async def oreLab(username: str, filter: str="month") -> dict:
    if not username:
        raise HTTPException(status_code=400, detail="Missing username")

    with db_session:
        presenze = select(p for p in PresenzaLab if p.email == f"{username}@eagletrt.it")
        latest = presenze.order_by(desc(PresenzaLab.entrata)).first()
        inLab = latest and latest.isActive
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if filter == "day":
            presenze = presenze.filter(lambda p: p.entrata >= today)
        elif filter == "7d":
            presenze = presenze.filter(lambda p: p.entrata >= today - timedelta(days=7))
        elif filter == "30d":
            presenze = presenze.filter(lambda p: p.entrata >= today - timedelta(days=30))
        elif filter == "month":
            presenze = presenze.filter(lambda p: p.entrata.month == now.month and p.entrata.year == now.year)
        elif filter == "year":
            presenze = presenze.filter(lambda p: p.entrata.year == now.year)
        else:
            filter = "all" # default
        return {
            "ore": sum([utils.timedelta_to_hours(p.duration) for p in list(presenze)]),
            "inlab": inLab,
            "filter": filter
        }


@app.get("/leaderboardOre")
async def leaderboardOre(filter: str="month") -> dict:
    with db_session:
        presenze = PresenzaLab.select()
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if filter == "day":
            presenze = presenze.filter(lambda p: p.entrata >= today)
        elif filter == "7d":
            presenze = presenze.filter(lambda p: p.entrata >= today - timedelta(days=7))
        elif filter == "30d":
            presenze = presenze.filter(lambda p: p.entrata >= today - timedelta(days=30))
        elif filter == "month":
            presenze = presenze.filter(lambda p: p.entrata.month == now.month and p.entrata.year == now.year)
        elif filter == "year":
            presenze = presenze.filter(lambda p: p.entrata.year == now.year)
        else:
            filter = "all" # default

        ore = select((p.email, sum(utils.timedelta_to_hours(p.duration))) for p in presenze).group_by(PresenzaLab.email)
        ore = sorted(ore, key=lambda x: x[1], reverse=True)
        return {
            "leaderboard": ore,
            "filter": filter
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, root_path=settings.API_PATH)
