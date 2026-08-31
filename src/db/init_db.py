from src.db.database import Base, engine
from src.db.models import *


def init_db():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
