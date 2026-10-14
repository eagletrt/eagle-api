import logging
import requests
from collections import defaultdict

BASE_ID = "p1j4lzwj5w41492"
PEOPLE_TABLE_ID = "muewy5068i7g63g"
AREAS_TABLE_ID = "mdvb2yn7yflq7yu"
ROLES_TABLE = "Roles"
PROJECTS_TABLE = "Projects"
PROJECT_HEAD_ROLE = "PM"


def _linked_ids(value) -> list[str]:
    """IDs from a link field, which is a single record or a list of records."""
    if not value:
        return []
    if isinstance(value, dict):
        value = [value]
    return [str(record['id']) for record in value if isinstance(record, dict) and 'id' in record]


class NocoDB:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({
            'xc-token': api_key,
            'Content-Type': 'application/json'
        })
        self._table_ids: dict[str, str] = {}

    def _records(self, table_id: str, **params) -> list[dict]:
        res = self._session.get(f"{self.base_url}/api/v3/data/{BASE_ID}/{table_id}/records", params=params)
        res.raise_for_status()
        return res.json().get("records") or []

    def _table_id(self, title: str) -> str:
        if not self._table_ids:
            res = self._session.get(f"{self.base_url}/api/v3/meta/bases/{BASE_ID}/tables")
            res.raise_for_status()
            self._table_ids = {table['title']: table['id'] for table in res.json().get("list", [])}
        if title not in self._table_ids:
            raise KeyError(f"NocoDB table '{title}' not found")
        return self._table_ids[title]

    def member_roles(self) -> dict[str, set[str]]:
        """Map each person record ID to its role tags (e.g. CT from Roles, PM from project heads)."""
        roles = defaultdict(set)

        for role in self._records(self._table_id(ROLES_TABLE), pageSize=1000, fields="Tag,People"):
            tag = (role['fields'].get("Tag") or "").strip().upper()
            if tag:
                for person_id in _linked_ids(role['fields'].get("People")):
                    roles[person_id].add(tag)

        projects = self._records(self._table_id(PROJECTS_TABLE), pageSize=1000, fields="Head",
                                 where="(Type,eq,Project)")
        for project in projects:
            for person_id in _linked_ids(project['fields'].get("Head")):
                roles[person_id].add(PROJECT_HEAD_ROLE)

        return roles

    def all_members(self) -> list[dict]:
        areas = self._records(AREAS_TABLE_ID, pageSize=10, fields="Tag")
        areas_map = {
            area['id']: area['fields']['Tag']
            for area in areas
        }
        items = self._records(PEOPLE_TABLE_ID, pageSize=1000, fields="Full Name,Team Email,Area,State")

        # Roles are a nice-to-have: if they can't be loaded, still return the members
        try:
            roles_map = self.member_roles()
        except (requests.RequestException, KeyError, ValueError) as e:
            logging.warning(f"Could not load member roles from NocoDB: {e}")
            roles_map = {}

        return [
            {
                "name": item['fields']["Full Name"],
                "email": item['fields']["Team Email"],
                "area": areas_map[item['fields']['Area']['id']] if item['fields'].get("Area") else "",
                "active": item['fields']["State"] in ["Active Member", "In trial", "Reachable"],
                "roles": sorted(roles_map.get(str(item['id']), []))
            } for item in items
        ]

    def public_members(self) -> list[dict]:
        items = self._records(PEOPLE_TABLE_ID, pageSize=1000, fields="Full Name", where="(State,eq,Active Member)")
        return [item['fields']["Full Name"] for item in items]
