import requests


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

    def active_members(self) -> list[str]:
        res = self._session.get(f"{self.base_url}/api/v2/tables/m3rsrrmnhhxxw0p/records", params={
            "limit": 1000,
            "viewId": "vw72nyx0bmaak96s",
            "fields": "Full Name"
        })
        items = res.json().get("list")

        return [item["Full Name"] for item in items]
