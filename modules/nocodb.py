import requests


class NocoDB:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            'xc-token': api_key,
            'Content-Type': 'application/json'
        })

    def all_members(self) -> list[str]:
        areas = self._session.get(f"{self.base_url}/api/v3/data/p1j4lzwj5w41492/mdvb2yn7yflq7yu/records", params={
            "pageSize": 10,
            "fields": "Tag"
        }).json()['records']
        areas_map = {
            area['id']: area['fields']['Tag']
            for area in areas
        }
        res = self._session.get(f"{self.base_url}/api/v3/data/p1j4lzwj5w41492/muewy5068i7g63g/records", params={
            "pageSize": 1000,
            "fields": "Full Name,Team Email,Area,State"
        })
        items = res.json().get("records")

        return [
            {
                "name": item['fields']["Full Name"],
                "email": item['fields']["Team Email"],
                "area": areas_map[item['fields']['Area']['id']] if item['fields'].get("Area") else "",
                "active": item['fields']["State"] in ["Active Member", "In trial", "Reachable"]
            } for item in items
        ]

    def public_members(self) -> list[dict]:
        res = self._session.get(f"{self.base_url}/api/v3/data/p1j4lzwj5w41492/muewy5068i7g63g/records", params={
            "pageSize": 1000,
            "fields": "Full Name",
            "where": "(State,eq,Active Member)"
        })
        items = res.json().get("records")
        return [item['fields']["Full Name"] for item in items]
