from sqlalchemy import Integer, String, ForeignKey, DateTime, PrimaryKeyConstraint
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from models.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(128), primary_key=True, default=uuid.uuid4()
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(120), nullable=True
    )

    def __repr__(self) -> str:
        return f'User(id={self.id!r},email={self.email!r},name={self.name!r},password_hash={self.password_hash!r})'


class Portfolio(Base):
    __tablename__ = "portfolio"

    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey('users.id')
    )
    stock_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('stocks.id')
    )
    added_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    updated_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "stock_id"),
    )
    
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    def __repr__(self) -> str:
        return f'Portfolio(user_id={self.user_id!r},stock_id={self.stock_id!r},quantity={self.quantity!r},updated_at={self.updated_at!r},added_at={self.added_at!r})'


class Stocks(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}
