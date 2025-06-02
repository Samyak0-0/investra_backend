from models.database import engine as db
from models.database import Base
from models.schemas import User,Portfolio,Stocks
from sqlalchemy.orm import sessionmaker


Session = sessionmaker(bind=db)

session = Session()

Base.metadata.create_all(db)

myUser = User(name='test',email='test_mail@gmail.com',password_hash='$123$@abcdefg')


session.add(myUser)
session.commit()
session.close()

