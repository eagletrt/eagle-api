import uuid
from datetime import datetime, timedelta
from pony.orm import Database, PrimaryKey, Required, Optional
from modules import settings

db = Database()


class PresenzaLab(db.Entity):
    email = Required(str, index="email_asc")
    entrata = Required(datetime, default=datetime.now, index="entrata_desc")
    uscita = Optional(datetime, index="uscita_desc")
    isValid = Required(bool, default=True)
    note = Optional(str)

    @property
    def isActive(self) -> bool:
        return self.uscita is None

    @property
    def duration(self) -> timedelta:
        if not self.isValid:
            return timedelta(0)
        if self.isActive:
            return datetime.now() - self.entrata
        return self.uscita - self.entrata


class TelemetryUser(db.Entity):
    email = PrimaryKey(str)
    role = Required(int, default=2)
    token = Optional(uuid.UUID, index="token_desc", unique=True, default=uuid.uuid4)
    expiry = Optional(datetime, default=datetime(1970, 1, 1))

    @property
    def hasValidToken(self) -> bool:
        return self.token and self.expiry > datetime.now()

    def generateToken(self) -> None:
        self.token = uuid.uuid4()
        self.expiry = datetime.now() + timedelta(seconds=settings.TLM_TOKEN_DURATION)

    def refreshToken(self) -> bool:
        if not self.hasValidToken:
            return False
        self.expiry = datetime.now() + timedelta(seconds=settings.TLM_TOKEN_REFRESH)
        return True


db.bind(provider='postgres', user=settings.DB_USERNAME, password=settings.DB_PASSWORD, host=settings.DB_HOST, port=settings.DB_PORT, database=settings.DB_NAME)
db.generate_mapping(create_tables=True)
