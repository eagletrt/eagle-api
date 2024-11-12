from pony.orm import Database, Required, Optional
from datetime import datetime, timedelta

db = Database("sqlite", "/data/oreLab.db", create_db=True)


class IngressoLab(db.Entity):
    email = Required(str)
    entrata = Required(datetime, default=datetime.now)
    uscita = Optional(datetime)
    note = Optional(str)

    @property
    def isActive(self) -> bool:
        return self.uscita is None

    @property
    def duration(self) -> timedelta:
        if self.isActive:
            return datetime.now() - self.entrata

        return self.uscita - self.entrata


db.generate_mapping(create_tables=True)
