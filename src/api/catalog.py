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
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
        row_result = result.fetchone()
        num_red_potions = row_result[0]
        num_green_potions = row_result[1]
        num_blue_potions = row_result[2]
        print(f"total num of potions inventory (rgb): {num_red_potions}, {num_green_potions}, {num_blue_potions}")

    catalog = []

    if (num_red_potions > 0):
        catalog.append({
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": num_red_potions,
                    "potion_type": [100, 0, 0, 0],
                    "price": 30,
                })
    if (num_green_potions > 0):
        catalog.append({
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": num_green_potions,
                    "potion_type": [0, 100, 0, 0],
                    "price": 30,
                })
    if (num_blue_potions > 0):
        catalog.append({
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": num_blue_potions,
                    "potion_type": [0, 0, 100, 0],
                    "price": 30,
                })
        
    print(catalog)
    

    return [
            catalog
            ]

