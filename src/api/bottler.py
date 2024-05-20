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
        text = "bottle deliver: "
        for i in potions_delivered:

            # don't insert in for loop, build up a dictionary, then do a bulk insert
            potion_id = connection.execute(sqlalchemy.text("""UPDATE potions SET 
                                            quantity = quantity + :quantity
                                            WHERE
                                            red = :red
                                            AND green = :green 
                                            AND blue = :blue
                                            AND dark = :dark 
                                            RETURNING id
                                            """),
                                            [{"quantity": i.quantity, 
                                             "red": i.potion_type[0],
                                             "green": i.potion_type[1],
                                             "blue": i.potion_type[2],
                                             "dark": i.potion_type[3]}])
            
            
            '''ledger'''
            transaction_id = connection.execute(sqlalchemy.text("""INSERT INTO transactions (num_potions, red_ml, green_ml, blue_ml, dark_ml, description) 
                                           VALUES (:num_potions, -:red_ml, -:green_ml, -:blue_ml, -:dark_ml, :text)
                                            RETURNING id"""),
                                           [{"num_potions": i.quantity, 
                                            "red_ml": i.potion_type[0] * i.quantity,
                                            "green_ml": i.potion_type[1] * i.quantity,
                                            "blue_ml": i.potion_type[2] * i.quantity, 
                                            "dark_ml": i.potion_type[3] * i.quantity, 
                                            "text": text + f"{i.quantity} of {i.potion_type}"}])
            
            '''connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger (transaction_id, potion_id, quantity) 
                                           VALUES (:transaction_id, :potion_id, :quantity)"""),
                                            [{"transaction_id": transaction_id, "potion_id": potion_id, "quantity": i.quantity}])'''

            total_quantity += i.quantity
        
        print(f"total added quantity: {total_quantity}")
        # connection.execute(sqlalchemy.text("""UPDATE global_inventory SET 
        #                             num_potions = num_potions + :quantity"""),
        #                             [{"quantity": total_quantity}])
        

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
        # results = connection.execute(sqlalchemy.text("""SELECT 
        #                                             red_ml,
        #                                             green_ml,
        #                                             blue_ml,
        #                                             dark_ml
        #                                             FROM global_inventory""")).one()
        
                
        results = connection.execute(sqlalchemy.text("""SELECT SUM(red_ml) as red_ml, 
                                                    SUM(green_ml) AS green_ml,
                                                    SUM(blue_ml) as blue_ml, 
                                                    SUM(dark_ml) as dark_ml 
                                                    FROM transactions
                                                    """)).one()
        
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
            potion_type = potion_list[0]
            print(f"bottling {potion_type}")

            quantity = 1000

            if potion_type[0] != 0 and ((red) // potion_type[0]) < quantity:
                quantity = (red) // potion_type[0]
            if potion_type[1] != 0 and ((green) // potion_type[1]) < quantity:
                quantity = (green) // potion_type[1]
            if potion_type[2] != 0 and ((blue) // potion_type[2]) < quantity:
                quantity = (blue) // potion_type[2]
            if potion_type[3] != 0 and ((dark) // potion_type[3]) < quantity:
                quantity = (dark) // potion_type[3]

            '''if negative value is returned'''
            if quantity < 0:
                quantity = 0
            
            if quantity == 0:
                return []

        else:
            return []
        
        print(potion_type)
        print(quantity)

        if quantity > 50:
            quantity = 50

    return [
        {   
            "potion_type": potion_type,
            "quantity": quantity
        }
    ]

if __name__ == "__main__":
    print(get_bottle_plan())