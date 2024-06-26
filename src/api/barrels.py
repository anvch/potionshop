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
        '''make it so that you can only process each order once (look at image taken in lab)'''
        '''create a processed table that stores the orders that were procesed, as well as the barrels, etc.'''
        print("barrel deliver")

        """TODO: figure out which barrel was delivered """
        """no barrels deliverd"""
        if(len(barrels_delivered) == 0): 
            print("no barrels delivered")
            print(f"order id: {order_id}")
            return "OK"
        
        gold_paid = 0
        red_ml = 0
        green_ml = 0
        blue_ml = 0
        dark_ml = 0
        text = "barrels deliver: "
        for barrel_delivered in barrels_delivered:
            gold_paid += barrel_delivered.price * barrel_delivered.quantity
            if barrel_delivered.potion_type == [1, 0, 0, 0]:
                red_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                text += "red "
            elif barrel_delivered.potion_type == [0, 1, 0, 0]:
                green_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                text += "green "
            elif barrel_delivered.potion_type == [0, 0, 1, 0]:
                blue_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                text += "blue "
            elif barrel_delivered.potion_type == [0, 0, 0, 1]:
                dark_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                text += "dark "
            else:
                raise Exception("Invalid potion type")
            
        print(f"gold_paid: {gold_paid}, red_ml: {red_ml}, green_ml: {green_ml}, blue_ml: {blue_ml}, dark_ml: {dark_ml}")

        '''ledger system'''
        connection.execute(sqlalchemy.text("""INSERT INTO transactions (gold, red_ml, green_ml, blue_ml, dark_ml, description, barrel_color) 
                                           VALUES (-:gold_paid, :red_ml, :green_ml, :blue_ml, :dark_ml, :text, 1)"""),
                                           [{"gold_paid": gold_paid, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml, "text": text}])


        print("check: ")

    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")

    return "OK"


'''ver2: want to buy green, red, blue barrel - set global variables'''
# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        print("barrels plan")

        results = connection.execute(sqlalchemy.text("""SELECT SUM(red_ml) as red_ml, 
                                                    SUM(green_ml) AS green_ml,
                                                    SUM(blue_ml) as blue_ml, 
                                                    SUM(dark_ml) as dark_ml, 
                                                    SUM(gold) as gold, 
                                                    SUM(barrel_color) as barrel_color
                                                    FROM transactions
                                                    """)).one()
        
        ml_inventory = [results.red_ml, results.green_ml, results.blue_ml, results.dark_ml]
        barrel_purchases = []
        current_ml = sum(ml_inventory)
        gold = results.gold

        '''only buying rgb right now, no dark'''
        barrel_color = results.barrel_color % 4

        print(f"barrel color (0 red/1 green/2 blue/3 dark) = {barrel_color}")

        print(f"ml_inventory (r, g, b, d): {ml_inventory}")
        print(f"current ml, gold: {current_ml}, {gold}")


        if(gold >= 250):
            print('enough money to buy')
            if barrel_color == 0:
                barrel_purchases = ["MEDIUM_RED_BARREL"]
            elif barrel_color == 1:
                barrel_purchases = ["MEDIUM_GREEN_BARREL"]
            elif barrel_color == 2 and gold >= 300:
                barrel_purchases = ["MEDIUM_BLUE_BARREL"]
            elif barrel_color == 3 and gold >= 300:
                '''not implemented at the moment'''
                barrel_purchases = ["MEDIUM_DARK_BARREL"]
        else:
            print("buy no barrels - saving")
            return []
        
        for i in barrel_purchases:
            price = 0
            price = next(item.price for item in wholesale_catalog if item.sku == i)
            ml_per_barrel = next(item.ml_per_barrel for item in wholesale_catalog if item.sku == i)
            if (price != 0):
                print(i + " in catalog")
                gold -= price
                current_ml += ml_per_barrel
            else:
                print(i + " not in catalog, can't purchase")
                barrel_purchases.remove(i)
            
    print(f"buying {barrel_purchases}, should update gold: {gold}, ml: {current_ml}")

    if len(barrel_purchases) == 0:
        return []
    
    return [
        {
            "sku": barrel_purchases[0],
            "quantity": 1,
        }
    ] 

    '''local database url'''
