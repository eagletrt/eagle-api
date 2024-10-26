from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from modules import settings
from modules.models import UserUpdates
from modules.google_admin import GoogleAdminAPI

app = FastAPI()
security = HTTPBearer()
google = GoogleAdminAPI(
    service_account_json=settings.GOOGLE_SERVICE_ACCOUNT_JSON,
    impersonate_admin_email=settings.GOOGLE_IMPERSONATE_ADMIN_EMAIL
)

last_received_user_updates = [] # Save the last received update so we can make less API calls


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")


@app.post("/updateUsers", dependencies=[Depends(verify_token)])
async def update_users(data: UserUpdates):
    global last_received_user_updates

    to_update = [u for u in data.users if u not in last_received_user_updates]
    for user in to_update:
        google.try_create_new_user(user, settings.GOOGLE_NEW_USER_PASSWORD)
        google.add_user_to_team(user, user.team)

    last_received_user_updates = data.users
    return {"status": "success", "message": f"{len(to_update)} users updated successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT, root_path=settings.API_PATH)
