from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


engine = create_engine(
    "sqlite:///./sca.db",
    connect_args={"check_same_thread": False},
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)
