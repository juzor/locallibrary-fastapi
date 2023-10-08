import os
from .config import settings
from dotenv import load_dotenv
import sqlalchemy as sa
import sqlalchemy.orm as so


class Model(so.DeclarativeBase):
    metadata = sa.MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


# load_dotenv()

DATABASE_URL = f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = sa.create_engine(DATABASE_URL)
Session = so.sessionmaker(engine)

def get_db():
    db = Session()
    try: 
        yield db
    finally:
        db.close()