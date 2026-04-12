import requests


class NocoDB:
    AREAS_MAP = {
        1: "CM",
        2: "DMT",
        3: "HW",
        4: "MGT",
        5: "MT",
        6: "SW"
    }

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
            "fields": "Full Name,Team Email,Area,State",
            "nested[Area][fields]": "Tag"
        })
        items = res.json().get("list")

        return [
            {
                "name": item["Full Name"],
                "email": item["Team Email"],
                "area": item["Area"]["Tag"] if item.get("Area") else "",
                "active": item["State"] in ["Active Member", "In trial"]
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
