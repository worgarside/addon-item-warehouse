"""API for managing warehouses and items."""
from __future__ import annotations

from collections.abc import Generator
from logging import StreamHandler, getLogger
from sys import stdout
from wg_utilities.functions.json import JSONObj
from fastapi import Body, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session
from collections.abc import Callable, MutableMapping, Sequence

from item_warehouse.src.app import crud
from item_warehouse.src.app.database import Base, SessionLocal, engine
from item_warehouse.src.app.models import Warehouse as WarehouseModel
from item_warehouse.src.app.schemas import Warehouse, WarehouseCreate
from item_warehouse.src.app._dependencies import get_db
from typing import Annotated, Union
LOGGER = getLogger(__name__)
LOGGER.setLevel("DEBUG")
LOGGER.addHandler(StreamHandler(stdout))


JSONVal = Union[
    None, object, bool, str, float, int, list["JSONVal"], "JSONObj", dict[str, object]
]
JSONObj = MutableMapping[str, JSONVal]

Base.metadata.create_all(bind=engine)

app = FastAPI()





# Warehouse Endpoints


@app.post("/v1/warehouses", response_model=Warehouse)
def create_warehouse(
    warehouse: WarehouseCreate, db: Session = Depends(get_db)  # noqa: B008
) -> WarehouseModel:
    """Create a warehouse."""

    if warehouse.name == "warehouse":
        raise HTTPException(
            status_code=400,
            detail="Warehouse name 'warehouse' is reserved.",
        )
    
    if (db_warehouse := crud.get_warehouse(db, warehouse.name)) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Warehouse {warehouse.name!r} already exists. Created"
            f" at {db_warehouse.created_at}",
        )
    
    if crud.get_item_model(db, warehouse.item_name) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Item {warehouse.item_name!r} already exists.",
        )

    try:
        return crud.create_warehouse(db, warehouse)
    except Exception as exc:
        LOGGER.exception(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to create warehouse {warehouse.name!r}: "{exc}"',
        ) from exc


@app.delete(
    "/v1/warehouses/{warehouse_name}",
    # status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_warehouse(
    warehouse_name: int, db: Session = Depends(get_db)  # noqa: B008
) -> None:
    """Delete a warehouse."""
    crud.delete_warehouse(db, warehouse_name)


@app.get("/v1/warehouses/{warehouse_name}", response_model=Warehouse)
def get_warehouse(
    warehouse_name: str, db: Session = Depends(get_db)  # noqa: B008
) -> WarehouseModel:
    """Get a warehouse."""

    if (db_warehouse := crud.get_warehouse(db, warehouse_name)) is None:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    return db_warehouse


@app.get("/v1/warehouses", response_model=list[Warehouse])
def get_warehouses(
    offset: int = 0, limit: int = 100, db: Session = Depends(get_db)  # noqa: B008
) -> list[WarehouseModel]:
    """List warehouses."""

    return crud.get_warehouses(db, offset=offset, limit=limit)


@app.put("/v1/warehouses/{warehouse_name}")
def update_warehouse(
    warehouse_name: int,
) -> dict[str, str]:
    """Update a warehouse in a warehouse."""
    _ = warehouse_name
    return {"message": "warehouse has been updated!"}


# Item Schema Endpoints


@app.get("/v1/items/{item_name}/schema/")
def get_item_schema(item_name: str, db: Session = Depends(get_db)# noqa: B008
                   ) -> dict[str, str]:
    """Get an item's schema."""
    if (item_model := crud.get_item_model(db, item_name)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_name!r} not found",
        )

    return item_model[0]


@app.get("/v1/items/schemas")
def get_item_schemas(
    db: Session = Depends(get_db),# noqa: B008
) -> dict[str, dict[str, str]]:  
    """Get a list of items' names and schemas."""
    return crud.get_item_schemas(db)

# Item Endpoints

@app.post("/v1/warehouses/{warehouse_name}/items")
def create_item(
    warehouse_name: str, item: Annotated[
        dict[str, object],
        Body(
            example={
                "name":"Joe Bloggs",
                "age": 42,
                "salary": 123456,
                "alive": True,
                "hire_date": "2021-01-01",
                "last_login": "2021-01-01T12:34:56"
            }
        )
    ], db: Session = Depends(get_db)# noqa: B008
) -> dict[str, str]:
    """Create an item."""
    
    crud.create_item(db, warehouse_name, item)

# @app.get("/v1/items/{item_name}")
# def get_item(
#     item_name: str, db: Session = Depends(get_db)# noqa: B008
# ) -> dict[str, str]:
#     """Get an item."""
#     _ = item_name
#     return {"message": "item has been retrieved!"}


if __name__ == "__main__":
    import uvicorn

    LOGGER.info("Starting server...")
    LOGGER.debug("http://0.0.0.0:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)
