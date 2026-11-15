import os
import time

from dotenv import load_dotenv
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    create_engine,
    text,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

load_dotenv()


def build_database_url() -> str:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "realestate_db")
    return os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
    )


DATABASE_URL = build_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Property(Base):
    __tablename__ = "properties"
    __table_args__ = (
        CheckConstraint("price > 0", name="chk_price_positive"),
        CheckConstraint("area_sqm > 0", name="chk_area_positive"),
        Index("idx_properties_location", "location", postgresql_using="btree"),
        Index("idx_properties_price", "price", postgresql_using="btree"),
        Index("idx_properties_property_type", "property_type", postgresql_using="btree"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    neighborhood = Column(String(255), nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    area_sqm = Column(Numeric(10, 2), nullable=False)
    price_per_sqm = Column(Numeric(12, 2), nullable=False)
    property_type = Column(String(100), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def wait_for_db(retries: int = 30, delay_seconds: float = 2.0) -> None:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print(f"Lidhja me PostgreSQL u krye (tentativa {attempt}).")
            return
        except Exception as exc:
            last_error = exc
            print(f"PostgreSQL nuk është gati ({attempt}/{retries}): {exc}")
            time.sleep(delay_seconds)
    raise RuntimeError(f"Nuk u arrit lidhja me PostgreSQL: {last_error}")
