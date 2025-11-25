from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, String, Column, Integer, INT, VARCHAR, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn, Relationship, mapped_column, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(128), default="None")

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)
    notification: Mapped["Notification"] = relationship(back_populates="user", uselist=False)



class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    qwery: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="profile")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    health: Mapped[str] = mapped_column(String)
    kp : Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="notification")

