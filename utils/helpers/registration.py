from models.schemas import User
from models.database import SessionLocal


def doesUserExistByUsername(username):
    session = SessionLocal()
    user = session.query(User).filter_by(name=username).first()
    session.commit()
    session.close()

    return user is not None
