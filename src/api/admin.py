from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
        '''reset global inventory'''
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET red_ml = '0', green_ml = '0', blue_ml = '0', dark_ml = '0', num_potions = '0', gold = '100', barrel_color = '0'"))

        '''reset potion quantities'''
        connection.execute(sqlalchemy.text("UPDATE potions SET quantity = 0"))

        '''drop carts, cart_items'''
        connection.execute(sqlalchemy.text("TRUNCATE carts CASCADE"))

        '''reset ledger'''
        connection.execute(sqlalchemy.text("TRUNCATE transactions"))
        connection.execute(sqlalchemy.text("INSERT INTO transactions (gold, num_potions, red_ml, green_ml, blue_ml) VALUES (100, 0, 0, 0, 0)"))
        
    return "OK"

