from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, UniqueConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
import uuid
import datetime
from models.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(128), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True)
    email_verified: Mapped[datetime.datetime | None] = mapped_column(
        "email_verified", DateTime, nullable=True)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    accounts: Mapped[list["Account"]] = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, email={self.email!r}, name={self.name!r})'


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id"),
    )

    id: Mapped[str] = mapped_column(
        String(128), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_account_id: Mapped[str] = mapped_column(
        String(100), nullable=False)

    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    id_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_state: Mapped[str | None] = mapped_column(
        String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="accounts")

    def __repr__(self) -> str:
        return f"Account(provider={self.provider!r}, provider_account_id={self.provider_account_id!r})"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(128), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_token: Mapped[str] = mapped_column(
        "session_token", String(255), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column("user_id", ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    expires: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __repr__(self) -> str:
        return f"Session(user_id={self.user_id!r}, session_token={self.session_token!r})"


class VerificationToken(Base):
    __tablename__ = "verificationtokens"
    __table_args__ = (
        UniqueConstraint("identifier", "token"),
    )

    identifier: Mapped[str] = mapped_column(String(255), primary_key=True)
    token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    expires: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"VerificationToken(identifier={self.identifier!r})"


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

