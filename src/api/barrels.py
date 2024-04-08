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
        num_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        price_s_green_barrel = 10
        new_balance = num_gold - price_s_green_barrel
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = '100"))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = '0'"))
        
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))

    if (num_green_potions < 10):
        buy_green = 1
    else:
        buy_green = 0


    return [
        {
            "sku": "SMALL_GREEN_BARREL",
            "quantity": buy_green,
        }
    ]

