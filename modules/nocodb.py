import requests
from uuid import uuid4
from datetime import datetime, timedelta


class NocoDB:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            'xc-token': api_key,
            'Content-Type': 'application/json'
        })

    def sponsors(self) -> list[dict]:
        res = self._session.get(f"{self.base_url}/api/v2/tables/mm7i3d83fn2pbdr/records", params={
            "limit": 1000
        })
        items = res.json().get("list")

        return [
            {
                "name": item["Name"],
                "rank": item["Rank"],
                "url": item["URL"],
                "logo": f"{self.base_url}/{item['Logo'][0]['path']}",
            } for item in items
        ]

    def all_members(self) -> list[str]:
        res = self._session.get(f"{self.base_url}/api/v2/tables/m3rsrrmnhhxxw0p/records", params={
            "limit": 1000,
            "fields": "Full Name,Team Email,Area",
            "nested[Area][fields]": "Tag"
        })
        items = res.json().get("list")

        return [
            {
                "name": item["Full Name"],
                "email": item["Team Email"],
                "area": item["Area"]["Tag"] if item.get("Area") else ""
            } for item in items
        ]

    def public_members(self) -> list[dict]:
        res = self._session.get(f"{self.base_url}/api/v2/tables/m3rsrrmnhhxxw0p/records", params={
            "limit": 1000,
            "viewId": "vw563gca4zb8joff",
            "fields": "Full Name"
        })
        items = res.json().get("list")

        return [item["Full Name"] for item in items]

    def get_user_roles(self, user_id: int) -> list[str]:
        res = self._session.get(f"{self.base_url}/api/v2/tables/m3rsrrmnhhxxw0p/links/crfcwmtkrbctt9p/records/{user_id}", params={
            "limit": 1000,
            "fields": "Tag"
        })
        return [item['Tag'] for item in res.json().get("list")]

    def get_or_create_telemetry_user(self, email: str) -> dict:
        res = self._session.get(f"{self.base_url}/api/v3/data/pz4ocnd339o3u9v/m8ib5uhza9mai6i/records", params={
            "limit": 1,
            "where": f"(email,eq,{email})",
        })
        items = res.json().get("records")
        if items:
            return items[0]["fields"]

        # If user not found, create it
        res = self._session.post(f"{self.base_url}/api/v3/data/pz4ocnd339o3u9v/m8ib5uhza9mai6i/records", json={
            "fields": {"email": email}
        })
        items = res.json().get("records")
        return items[0]["fields"]

    def create_telemetry_token(self, email: str) -> dict:
        res = self._session.get(f"{self.base_url}/api/v3/data/pz4ocnd339o3u9v/m8ib5uhza9mai6i/records", params={
            "limit": 1,
            "where": f"(email,eq,{email})",
        })
        items = res.json().get("records")
        if not items:
            return None

        user = items[0]
        res = self._session.patch(f"{self.base_url}/api/v3/data/pz4ocnd339o3u9v/m8ib5uhza9mai6i/records", json={
            "id": user["id"],
            "fields": {
                "token": str(uuid4()),
                "expiry": (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S+00:00")
            }
        })
        items = res.json().get("records")
        return items[0]["fields"]

    def get_telemetry_token(self, token: str) -> dict:
        res = self._session.get(f"{self.base_url}/api/v3/data/pz4ocnd339o3u9v/m8ib5uhza9mai6i/records", params={
            "limit": 1,
            "where": f"(token,eq,{token})",
        })
        items = res.json().get("records")
        if not items:
            return None

        if datetime.strptime(items[0]["fields"]["expiry"], "%Y-%m-%d %H:%M:%S+00:00") < datetime.now():
            return None

        return items[0]["fields"]
