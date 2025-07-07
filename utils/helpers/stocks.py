from models.schemas import Stocks
from models.database import SessionLocal


def stockSymbolToId(symbol):
    session = SessionLocal()
    try:
        print(symbol)
        stock = session.query(Stocks).filter(Stocks.name == symbol).first()
        print(stock)
        if stock:
            return stock.to_dict()['id']
        else:
            return ""
    finally:
        session.close()
