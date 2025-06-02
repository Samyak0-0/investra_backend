
# create_tables.py
from models.database import engine
from models.schemas import Base

Base.metadata.create_all(bind=engine)
