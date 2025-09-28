import schedule
from time import sleep
from threading import Thread
from datetime import datetime, timedelta
from fastapi.responses import HTMLResponse
from pony.orm import db_session, desc, select
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules.nocodb import NocoDB
from modules import settings, utils
from modules.db_ore import PresenzaLab
from modules.google_admin import GoogleAdminAPI

app = FastAPI()
security = HTTPBearer()
google = GoogleAdminAPI(
    service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON,
    impersonate_admin_email=settings.GOOGLE_IMPERSONATE_ADMIN_EMAIL
)
nocodb = NocoDB(
    base_url="https://nocodb.eagletrt.it",
    api_key=settings.NOCODB_API_TOKEN
)

# Fix CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")


@app.post("/users", dependencies=[Depends(verify_token)])
async def create_users(data: dict) -> dict:
    existing_users = google.list_all_users()
    to_create = [u for u in data["data"]["rows"] if u["Team Email"] not in existing_users]

    for user in to_create:
        if google.try_create_new_user(user, settings.GOOGLE_NEW_USER_PASSWORD):
            google.add_user_to_group(user["Team Email"], "members@groups.eagletrt.it")

    return {"status": "success", "message": f"{len(to_create)} users created successfully"}


@app.put("/users", dependencies=[Depends(verify_token)])
async def update_users(data: dict) -> dict:
    existing_users = google.list_all_users()
    to_update = [u for u in data["data"]["rows"] if u["Team Email"] in existing_users]

    for user in to_update:
        # Members group
        if user["State"] not in ["Active Member", "In trial"]:
            google.remove_user_from_group(user["Team Email"], "members@groups.eagletrt.it")
        elif user["State"] in ["Active Member", "In trial"]:
            google.add_user_to_group(user["Team Email"], "members@groups.eagletrt.it")

        # Alumni group
        if user["State"] == "Alumno":
            google.add_user_to_group(user["Team Email"], "alumni@groups.eagletrt.it")
        else:
            google.remove_user_from_group(user["Team Email"], "alumni@groups.eagletrt.it")

    return {"status": "success", "message": f"{len(to_update)} users updated successfully"}


@app.get("/lab/presenza", response_class=HTMLResponse, response_model=None)
async def lab_presenza(x_email: str = Header(default=None)):
    if not x_email:
        raise HTTPException(status_code=400, detail="Missing authentication")

    with db_session:
        presenze = PresenzaLab.select(lambda p: p.email == x_email)
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


@app.post("/lab/presenza/confirm", response_class=HTMLResponse, response_model=None)
async def lab_presenza_confirm(x_email: str = Header(default=None)):
    if not x_email:
        raise HTTPException(status_code=400, detail="Missing authentication")

    with db_session:
        latest = PresenzaLab.select(lambda p: p.email == x_email).order_by(desc(PresenzaLab.entrata)).first()
        if latest and latest.isActive:
            latest.uscita = datetime.now()
            utils.notify_exit(latest)
            return HTMLResponse(content="Uscita confermata.", status_code=200)
        else:
            latest = PresenzaLab(email=x_email, entrata=datetime.now())
            utils.notify_entry(latest)
            return HTMLResponse(content="Entrata confermata.", status_code=200)


@app.get("/lab/ore")
async def lab_ore(username: str) -> dict:
    now = datetime.now()
    with db_session:
        presenze = PresenzaLab.select(lambda p: p.email == f"{username}@eagletrt.it")
        latest = presenze.order_by(desc(PresenzaLab.entrata)).first()
        inLab = latest and latest.isActive

        presenze = presenze.filter(lambda p: p.entrata.month == now.month and p.entrata.year == now.year)
        return {
            "ore": sum([utils.timedelta_to_hours(p.duration) for p in list(presenze)]),
            "inlab": inLab
        }


@app.get("/lab/leaderboard")
async def lab_leaderboard(since: str="", until: str="", x_email: str = Header(default=None)) -> dict:
    if not x_email:
        raise HTTPException(status_code=400, detail="Missing authentication")

    now = datetime.now()
    if not since:
        since = now.strftime("%Y-%m-01") # default to the first day of the current month
    if not until:
        until = now.strftime("%Y-%m-%d") # default to today

    try:
        since_date = datetime.strptime(since, "%Y-%m-%d")
        until_date = datetime.strptime(until, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format(s). Use YYYY-MM-DD.")

    with db_session:
        presenze = PresenzaLab.select(lambda p: p.entrata >= since_date and p.entrata <= until_date + timedelta(days=1))
        leaderboard = {}
        for p in presenze:
            if p.email not in leaderboard:
                leaderboard[p.email] = 0
            leaderboard[p.email] += utils.timedelta_to_hours(p.duration)
        leaderboard = dict(sorted(leaderboard.items(), key=lambda i: i[1], reverse=True))

        return {
            "leaderboard": leaderboard,
            "since": since_date.strftime("%Y-%m-%d"),
            "until": until_date.strftime("%Y-%m-%d")
        }


@app.get("/lab/inlab")
async def lab_inlab() -> dict:
    with db_session:
        in_lab = select(p.email for p in PresenzaLab if p.isActive)
        return {
            "count": len(in_lab),
            "people": list(in_lab)
        }


@app.get("/website/sponsors")
async def website_sponsors():
    return {
        "sponsors": nocodb.sponsors()
    }


@app.get("/website/members")
async def website_members():
    return {
        "members": nocodb.public_members()
    }


@app.get("/members")
async def members():
    return {
        "members": nocodb.current_members()
    }


def deleteActivePresenze():
    with db_session:
        to_delete = PresenzaLab.select(lambda p: p.isActive)
        for p in to_delete:
            p.uscita = datetime.now()
            p.isValid = False
            p.note = "Closed due to inactivity"


def run_schedules():
    while True:
        schedule.run_pending()
        sleep(10)


if __name__ == "__main__":
    import uvicorn
    schedule.every().day.at("04:00").do(deleteActivePresenze)
    Thread(target=run_schedules, daemon=True).start()
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, root_path=settings.API_PATH)
