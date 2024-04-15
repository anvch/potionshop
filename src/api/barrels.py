from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """

    with db.engine.begin() as connection:
        print("barrel deliver")
        r = 0
        g = 0
        b = 0

        """TODO: figure out which barrel was delivered """
        """no barrels deliverd"""
        if(len(barrels_delivered) == 0): 
            print("no barrels delivered")
            print(f"order id: {order_id}")
            return "OK"

        barrel_type = barrels_delivered[0].sku
        if(barrel_type == 'MINI_GREEN_BARREL'): 
            ml_type = 'num_green_ml'
            g = 1
    
        elif (barrel_type == 'MINI_BLUE_BARREL'):
            ml_type = 'num_blue_ml'
            b = 1

        elif (barrel_type == 'MINI_RED_BARREL'): 
            ml_type = 'num_red_ml'
            r = 1

        else: 
            print("unrecognized barrel deliver type")
            return "NOT OK"
        
        """ set r/g/b to 1 depending on result"""
        print(f"ml_type: {ml_type}")


        result = connection.execute(sqlalchemy.text(f"SELECT gold, {ml_type}, barrel_color FROM global_inventory"))
        row_results = result.fetchone()

        num_gold = row_results[0]
        print(f"old gold balance: {num_gold}")
    
        num_ml = row_results[1]
        print(f"old {ml_type}: {num_ml}")

        barrel_color = row_results[2]
        print(f"old barrel color: {barrel_color}")
        barrel_color += 1

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET barrel_color = '{barrel_color}'"))

        '''update ml of green/blue/red'''
        if (g == 1):
            num_ml = num_ml + 200
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = '{num_ml}'"))
            new_balance = num_gold - 60
        elif (b == 1):
            num_ml = num_ml + 200
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = '{num_ml}'"))
            new_balance = num_gold - 60
        elif (r == 1):
            num_ml = num_ml + 200
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = '{num_ml}'"))
            new_balance = num_gold - 60

        """TODO: update balance based off of purchase"""
        print(f"updated gold: {new_balance}")
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = '{new_balance}'"))
        check = connection.execute(sqlalchemy.text(f"SELECT {ml_type}, gold, barrel_color FROM global_inventory"))
        for row in check:
            print(f"database updated (ml, gold, barrel color): {row}")

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"


'''ver2: want to buy green, red, blue barrel - set global variables'''
# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        print("barrels plan")
        result = connection.execute(sqlalchemy.text("SELECT gold, barrel_color FROM global_inventory"))

        row_result = result.fetchone()

        gold = row_result[0]
        print(f"amount of gold: {gold}")

        barrel_color = row_result[1] % 3
        print(f"barrel color (0 green/1 blue/2 red) = {barrel_color}")

    '''VER2: cycle through buying the different colors'''
    if (barrel_color == 0):
        print("buy green")
        return[
            {
                "sku": "MINI_GREEN_BARREL",
                "quantity": 1,
            }
        ]
    elif (barrel_color == 1):
        print("buy red")
        return[
            {
                "sku": "MINI_BLUE_BARREL",
                "quantity": 1,
            }
        ]
    elif (barrel_color == 2):
        print("buy blue")
        return[
            {
                "sku": "MINI_RED_BARREL",
                "quantity": 1,
            }
        ]

    else:
        print("don't buy anything")
        return [{}]

