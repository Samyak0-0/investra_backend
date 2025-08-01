# create_tables.py

from models.database import Base, engine
from models.schemas import User, Account, Portfolio, Session, VerificationToken

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created (if not existing)")

if __name__ == "__main__":
    create_tables()
