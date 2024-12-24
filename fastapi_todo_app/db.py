from sqlmodel import Session, SQLModel, create_engine

from fastapi_todo_app import settings

connection_string: str = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
# engine = create_engine(connection_string, connect_args={"sslmode": "require"} , echo=True, pool_recycle=300, pool_size=5)
engine = create_engine(connection_string, echo=True, pool_recycle=300, pool_size=5)


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
