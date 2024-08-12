import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from model import Base, User, Delta

if __name__ == '__main__':
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            id=12345,
            balance=0
        )

        delta = Delta(
            id=1,
            user_id=user.id,
            timestamp=datetime.datetime.now(),
            value=5
        )

        session.add(user)
        session.add(delta)

        session.commit()

    print(f"All inserted: {user}, {session}")

    with Session(engine) as session:
        for user in session.scalars(select(User)):
            print(f"Selected user {user}")
