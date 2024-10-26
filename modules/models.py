from typing import List, Union
from pydantic import BaseModel


class AirtableTeam(BaseModel):
    id: str
    name: str
    color: str

class AirtableGroup(BaseModel):
    id: str
    name: str
    color: str

class AirtableRank(BaseModel):
    id: str
    name: str
    color: str


class AirtableUser(BaseModel):
    name: str
    surname: str
    email: str
    team: AirtableTeam
    group: Union[AirtableGroup, None]
    ranks: Union[List[AirtableRank], None]
    role: int
    role_override: Union[int, None]


class UserUpdates(BaseModel):
    users: List[AirtableUser]
