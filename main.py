from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules import settings, utils
from modules.models import UserUpdates
from modules.google_admin import GoogleAdminAPI

app = FastAPI()
security = HTTPBearer()
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
        google.add_user_to_team(user, user.team)

    return {"status": "success", "message": f"{len(to_create)} users created successfully"}


# create a GET /userGroups that takes an email as a query parameter and returns the groups that the user is part of
@app.get("/userGroups", dependencies=[Depends(verify_token)])
async def get_user_groups(email: str) -> list[str]:
    return google.list_user_groups(email)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, root_path=settings.API_PATH)
