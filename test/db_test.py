from models.database import engine as db
from models.database import Base
from models.schemas import User,Portfolio,Stocks
from sqlalchemy.orm import sessionmaker


Session = sessionmaker(bind=db)

session = Session()

myUser = User(id="010CYBIOA",name='test',email='test_mail@gmail.com')

Base.metadata.create_all(db)

session.add(myUser)
session.commit()
session.close()

