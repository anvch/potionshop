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
        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        result1 = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        
        for row in result:
            print(row)
            num_gold = int (row[0])
        print(num_gold)

        for row in result1:
            print(row)
            num_green_ml = int (row[0])
        print(num_green_ml)

        num_green_ml = num_green_ml + (len(barrels_delivered) * 500)
        print(num_green_ml)
        price_s_green_barrel = 100
        new_balance = num_gold - price_s_green_barrel
        print(new_balance)
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = '{num_green_ml}'"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = '{new_balance}'"))
        check = connection.execute(sqlalchemy.text("SELECT num_green_ml, gold FROM global_inventory"))
        for row in check:
            print(row)

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))

        for row in result:
            print(row)
            num_green_potion = row[0]
        print(num_green_potion)


    if (num_green_potion < 10):
        print("buy green")
        return[
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": 1,
        }
    ]
    else:
        print("don't buy green")
        return [{}]

