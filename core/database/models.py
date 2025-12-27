from sqlalchemy import BigInteger, ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(128), default="None")

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)
    health: Mapped[list["Health"]] = relationship(back_populates="user")



class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    query: Mapped[bool] = mapped_column(Boolean, default=True)
    min_kp_notification: Mapped[int] = mapped_column(Integer, default=1)

    user: Mapped["User"] = relationship(back_populates="profile")


class Health(Base):
    __tablename__ = "health"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    health: Mapped[str] = mapped_column(String)
    kp : Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="health")

