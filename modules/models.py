from pydantic import BaseModel


class TelemetryToken(BaseModel):
    token: str
