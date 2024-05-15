from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    print("getting inventory")
    with db.engine.begin() as connection:
        # results = connection.execute(sqlalchemy.text("""SELECT 
        #                                             red_ml,
        #                                             green_ml,
        #                                             blue_ml,
        #                                             dark_ml,
        #                                             num_potions,
        #                                             gold
        #                                             FROM global_inventory""")).one()
        
        results = connection.execute(sqlalchemy.text("""SELECT SUM(red_ml) as red_ml, 
                                                    SUM(green_ml) AS green_ml,
                                                    SUM(blue_ml) as blue_ml, 
                                                    SUM(dark_ml) as dark_ml, 
                                                    SUM(gold) as gold, 
                                                    SUM(num_potions) as num_potions,
                                                    SUM(barrel_color) as barrel_color
                                                    FROM transactions
                                                    """)).one()
        
        num_potions = results.num_potions
        ml_inventory = [results.red_ml, results.green_ml, results.blue_ml, results.dark_ml]
        current_ml = sum(ml_inventory)
        gold = results.gold

        print(f"gold: {gold}, num_potions: {num_potions}, ml_inventory: {ml_inventory}, barrel color: {results.barrel_color}")

    return {"number_of_potions": num_potions, "ml_in_barrels": current_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    buy = 1
    print("bought potion capactiy")

    return {
        "potion_capacity": buy,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
