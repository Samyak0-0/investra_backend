from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session
from sqlalchemy import URL
from dotenv import load_dotenv
import os

load_dotenv()

url_object = URL.create(
    "postgresql",
    username=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DB'),
)

engine = create_engine(url_object, echo=True)

SessionLocal = scoped_session(sessionmaker(bind=engine))

class Base(DeclarativeBase):
    pass
