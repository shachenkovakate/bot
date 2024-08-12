import datetime
import asyncio

from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

ENGINE = create_async_engine("sqlite+aiosqlite:///database.db", echo=True)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int]
    state: Mapped[int]


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


async def create_user(user_id: int, balance: int):
    async with AsyncSession(ENGINE) as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.scalars(stmt)).one_or_none()
        if user is None:
            user = User(id=user_id, balance=balance, state=0)
            session.add(user)
            await session.commit()


async def change_balance(user_id: int, value: int):
    async with AsyncSession(ENGINE) as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.scalars(stmt)).one_or_none()
        if user is None:
            user = User(id=user_id, balance=0, state=0)
            session.add(user)
        user.balance += value
        await session.commit()


async def change_state(user_id: int, state: int):
    async with AsyncSession(ENGINE) as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.scalars(stmt)).one_or_none()
        if user is None:
            user = User(id=user_id, balance=0, state=0)
            session.add(user)
        user.state = state
        await session.commit()


async def get_state(user_id: int) -> int:
    async with AsyncSession(ENGINE) as session:
        stmt = select(User).where(User.id == user_id)
        user = (await session.scalars(stmt)).one_or_none()

        print('MMMMMMMMMMM')

        if user is None:
            return -1
        else:
            return user.state


async def mean(ts1: datetime.datetime, ts2: datetime.datetime, user_id: int, typee: int) -> float:
    if ts1 > ts2:
        t = ts1
        ts1 = ts2
        ts2 = t

    ts = ts2 - ts1

    async with AsyncSession(ENGINE) as session:
        stmt = select(Delta).where(
            Delta.user_id == user_id).where(
            ts2 >= Delta.timestamp).where(
            Delta.timestamp >= ts1).where(
            typee * Delta.value > 0)
        result = await session.execute(stmt)
        events = result.scalars().all()
        sum = 0
        for e in events:
            sum += e.value
            print(e.value, end='\n')
        answer = sum / (ts.days + 1)
        return answer
