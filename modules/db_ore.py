from pony.orm import Database, Required, Optional
from datetime import datetime, timedelta

db = Database("sqlite", "/data/oreLab.db", create_db=True)


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


db.generate_mapping(create_tables=True)
