from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import URL
from sqlalchemy import text

load_dotenv()

url_object = URL.create(
    "postgresql",
    username=f"{os.getenv('POSTGRES_USER')}",
    password=f"{os.getenv('POSTGRES_PASSWORD')}",
    host=f"{os.getenv('POSTGRES_HOST')}",
    database=f"{os.getenv('POSTGRES_DB')}",
)

engine = create_engine(url_object, echo=False)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):  # just a base class for entities
    pass

# def test_connection():
#     try:
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             print("Database connection successful:", result.scalar())
#     except Exception as e:
#         print("Database connection failed:", e)

# if __name__ == "__main__":
#     test_connection()
