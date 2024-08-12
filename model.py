import datetime
import asyncio

from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

ENGINE = create_async_engine("sqlite+aiosqlite:///database.db", echo=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int]


class Delta(Base):
    __tablename__ = "delta"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    timestamp: Mapped[datetime.datetime]
    value: Mapped[int]


async def init_models():
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_delta(user_id: int, ts: datetime.datetime, value: int):
    async with AsyncSession(ENGINE) as session:
        delta = Delta(user_id=user_id, timestamp=ts, value=value)
        session.add(delta)
        await session.commit()


async def create_user(id: int, balance: int):
    async with AsyncSession(ENGINE) as session:
        user = User(id=id, balance=balance)
        session.add(user)
        await session.commit()


async def change_balance(user_id: int, value: int):
    async with AsyncSession(ENGINE) as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.scalars(stmt)).one()
        user.balance += value
        await session.commit()
