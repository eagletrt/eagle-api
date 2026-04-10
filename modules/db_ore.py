from datetime import datetime, timedelta
from pony.orm import Database, Required, Optional
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


db.bind(provider='postgres', user=settings.DB_USERNAME, password=settings.DB_PASSWORD, host=settings.DB_HOST, port=settings.DB_PORT, database=settings.DB_NAME)
db.generate_mapping(create_tables=True)
