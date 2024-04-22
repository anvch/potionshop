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

        if(len(potions_delivered) == 0):
            print("empty bottle plan")
            return "OK"

        total_quantity = 0
        for i in potions_delivered:

            connection.execute(sqlalchemy.text("""UPDATE potions SET 
                                            quantity = quantity + :quantity
                                            WHERE
                                            red = :red
                                            AND green = :green 
                                            AND blue = :blue
                                            AND dark = :dark
                                            """),
                                            [{"quantity": i.quantity, 
                                             "red": i.potion_type[0],
                                             "green": i.potion_type[1],
                                             "blue": i.potion_type[2],
                                             "dark": i.potion_type[3]}])
            
            connection.execute(sqlalchemy.text("""UPDATE global_inventory SET 
                                            red_ml = red_ml - (:red * :quantity),
                                            green_ml = green_ml - (:green * :quantity),
                                            blue_ml = blue_ml - (:blue * :quantity),
                                            dark_ml = dark_ml - (:dark * :quantity)
                                            """),
                                            [{"quantity": i.quantity, 
                                             "red": i.potion_type[0],
                                             "green": i.potion_type[1],
                                             "blue": i.potion_type[2],
                                             "dark": i.potion_type[3]}])
            total_quantity += i.quantity
        
        print(f"total added quantity: {total_quantity}")
        connection.execute(sqlalchemy.text("""UPDATE global_inventory SET 
                                    num_potions = num_potions + :quantity"""),
                                    [{"quantity": total_quantity}])
        

        print(connection.execute(sqlalchemy.text(f"SELECT * FROM potions")))

        
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
        results = connection.execute(sqlalchemy.text("""SELECT 
                                                    red_ml,
                                                    green_ml,
                                                    blue_ml,
                                                    dark_ml
                                                    FROM global_inventory""")).one()
        
        ml_inventory = [results.red_ml, results.green_ml, results.blue_ml, results.dark_ml]

        red = ml_inventory[0]
        green = ml_inventory[1]
        blue = ml_inventory[2]
        dark = ml_inventory[3]

        recipes = connection.execute(sqlalchemy.text("""SELECT item_sku,
                                                     red,
                                                     green,
                                                     blue,
                                                     dark
                                                     FROM potions
                                                     WHERE red <= :red
                                                     AND green <= :green
                                                     AND blue <= blue
                                                     AND dark <= :dark
                                                     ORDER BY id"""
                                                     ),
                                                     [{"red": red, "green": green, "blue": blue, "dark": dark}])
        
        potion_list = []

        for i in recipes:
            print(f"item_sku: {i[0]}")
            print(f"type: ({i[1]}, {i[2]}, {i[3]}, {i[4]})")
            potion_list.append([i[1], i[2], i[3], i[4]])

        if (len(potion_list) != 0):
            print(f"bottling {potion_list[0]}")
        else:
            return []



    return [
        {   '''only bottling 1 at a time for convenience at this moment'''
            "potion_type": potion_list[0],
            "quantity": 1
        }
    ]

if __name__ == "__main__":
    print(get_bottle_plan())