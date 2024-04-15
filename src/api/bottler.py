from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    with db.engine.begin() as connection:
        print("bottle deliver")
        '''TODO: figure out how to make variable incrementable for num of potions'''
        '''update in deliver'''
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
        row_result = result.fetchone()
        num_red_potions = row_result[0]
        num_green_potions = row_result[1]
        num_blue_potions = row_result[2]

        print(f"original num of potions (r,g,b): {num_red_potions}, {num_green_potions}, {num_blue_potions}")

        num_red_potions += potions_delivered[0].quantity
        num_green_potions += potions_delivered[1].quantity
        num_blue_potions += potions_delivered[2].quantity

        '''update number of potions '''
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = '{num_red_potions}', num_green_potions = '{num_green_potions}', num_blue_potions = '{num_blue_potions}'"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = '0', num_green_ml = '0', num_blue_ml = '0'"))

        updated = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
        print(f"updating database (rgb potions, ml): {updated.fetchall()}")
              
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    with db.engine.begin() as connection:
        print("bottle plan")
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
    
        row_result = result.fetchone()
        num_red_ml = row_result[0]
        num_green_ml = row_result[1]
        num_blue_ml = row_result[2]
        print(f"num red ml: {num_red_ml}")
        print(f"num green ml: {num_green_ml}")
        print(f"num blue ml: {num_blue_ml}")
        num_red_potions = (int) (num_red_ml/100)
        num_green_potions = (int) (num_green_ml/100)
        num_blue_potions = (int) (num_blue_ml/100)
        print(f"bottling {num_red_potions} red, {num_green_potions} green, {num_blue_potions} blue potions (plan)")

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_red_potions,
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": num_green_potions,
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": num_blue_potions,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())