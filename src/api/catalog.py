from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        for row in result:
            print(row)
            num_of_potions = int (row[0])
        print(num_of_potions)

    """hacking to only list 1 potion in catalog at a time"""
    if(num_of_potions > 0):
        return [
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [0, 0, 100, 0],
                }
            ]
    else:
        return []

