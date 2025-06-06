from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import URL

load_dotenv()

url_object = URL.create(
    "postgresql",
    username=f"{os.getenv('POSTGRES_USER')}",
    password=f"{os.getenv('POSTGRES_PASSWORD')}",
    host=f"{os.getenv('POSTGRES_HOST')}",
    database=f"{os.getenv('POSTGRES_DB')}",
)
engine = create_engine(url_object, echo=True)

class Base(DeclarativeBase):  # just a base class for entities
    pass
