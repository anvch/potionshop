from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT 
                                                    item_sku, 
                                                    red, green, blue, dark, 
                                                    price, 
                                                    quantity 
                                                    FROM potions 
                                                    WHERE quantity > 0""")) 
        '''add ORDER BY logic (key number?), then LIMIT 6'''
        
        
    catalog = []

    for i in result:
        sku = i.item_sku
        potion_type = [i.red, i.green, i.blue, i.dark]
        catalog.append({
            "sku": sku,
            "name": sku,
            "quantity": i.quantity,
            "potion_type": potion_type,
            "price": i.price,
        })
        
    print(catalog)
    

    return catalog

