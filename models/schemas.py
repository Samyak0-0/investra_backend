from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    PrimaryKeyConstraint,
    UniqueConstraint
)
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from models.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    email_verified: Mapped[datetime.datetime] = mapped_column("email_verified", DateTime(timezone=True), nullable=True)
    image: Mapped[str] = mapped_column(String(255), nullable=True)

    accounts = relationship("Account", backref="user", cascade="all, delete-orphan")
    sessions = relationship("Session", backref="user", cascade="all, delete-orphan")
    portfolio = relationship("Portfolio", backref="user", cascade="all, delete-orphan")

class Portfolio(Base):
    __tablename__ = "portfolio"
    user_id: Mapped[str] = mapped_column(String(128), ForeignKey("users.id"), primary_key=True)
    stock_name: Mapped[str] = mapped_column("stock_Name", String(50), primary_key=True)
    stock_amt: Mapped[int] = mapped_column("stock_Amt", Integer, nullable=False)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# class Stocks(Base):
#     __tablename__ = "stocks"

#     id: Mapped[int] = mapped_column(
#         Integer,
#         primary_key=True,
#         autoincrement=True,
#     )
#     name: Mapped[str] = mapped_column(String(10), nullable=False)

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[str] = mapped_column(
        String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_account_id: Mapped[str] = mapped_column(String(100), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    access_token: Mapped[str] = mapped_column(String, nullable=True)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=True)
    token_type: Mapped[str] = mapped_column(String(50), nullable=True)
    scope: Mapped[str] = mapped_column(String(255), nullable=True)
    id_token: Mapped[str] = mapped_column(String, nullable=True)
    session_state: Mapped[str] = mapped_column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("provider", "provider_account_id"),)


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(128), primary_key=True, default=uuid.uuid4)
    session_token: Mapped[str] = mapped_column("session_token", String(255), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column("user_id", String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class VerificationToken(Base):
    __tablename__ = "verificationtokens"
    identifier: Mapped[str] = mapped_column(String(255), primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("identifier", "token"),
    )

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

