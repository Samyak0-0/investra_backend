from models.schemas import Stocks
from models.database import SessionLocal


def stockSymbolToId(symbol):
    session = SessionLocal()
    stock = session.query(Stocks).filter_by(name=symbol).first()
    stock_id = stock.id
    session.close()
    return stock_id
