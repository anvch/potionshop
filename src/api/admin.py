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

        '''reset potion quantities'''
        connection.execute(sqlalchemy.text("UPDATE potions SET quantity = 0"))

        '''drop carts, cart_items'''
        connection.execute(sqlalchemy.text("TRUNCATE carts CASCADE"))

        '''reset ledger'''
        connection.execute(sqlalchemy.text("TRUNCATE transactions"))
        connection.execute(sqlalchemy.text("INSERT INTO transactions (id, gold, description) VALUES (1, 100, :text)"), [{"text": "reset to initial state of 100 gold"}])
        
    return "OK"

