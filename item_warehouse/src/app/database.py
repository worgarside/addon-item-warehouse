"""Database constants and classes."""

from json import dumps
from os import environ, getenv
from typing import Any

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker  # type: ignore[attr-defined]

from item_warehouse.src.app.schemas import ITEM_TYPE_TYPES

DATABASE_USERNAME = environ["DATABASE_USERNAME"]
DATABASE_PASSWORD = environ["DATABASE_PASSWORD"]
DATABASE_HOST = getenv("DATABASE_HOST", "homeassistant.local")
DATABASE_PORT = int(getenv("DATABASE_PORT", "3306"))
DATABASE_NAME = getenv("DATABASE_NAME", "item_warehouse")

SQLALCHEMY_DATABASE_URL = f"mariadb+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?charset=utf8mb4"  # noqa: E501


def _custom_json_serializer(*args: Any, **kwargs: Any) -> str:
    def _serialize(obj: Any) -> Any:
        if obj in ITEM_TYPE_TYPES:
            return obj.__name__.lower()

        return obj

    return dumps(*args, default=_serialize, **kwargs)


engine = create_engine(SQLALCHEMY_DATABASE_URL, json_serializer=_custom_json_serializer)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
