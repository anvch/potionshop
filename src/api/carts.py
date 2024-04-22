from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    with db.engine.begin() as connection:
        print("create cart")
        try:
            num_cart = 0
            result = connection.execute(sqlalchemy.text("SELECT id FROM carts ORDER BY id DESC")).one()
        except:
            print("first cart created")
            num_cart = 1

        if num_cart == 0:
            num_cart = result.id + 1

        print(f"cart id: {num_cart}")

        connection.execute(sqlalchemy.text("INSERT INTO carts (id) VALUES (:num_cart)"),
                           [{"num_cart": num_cart}])

    return {"cart_id": num_cart}

class CartItem(BaseModel):
    quantity: int

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("add item to cart")

    with db.engine.begin() as connection:

        result = connection.execute(sqlalchemy.text("""SELECT
                                                    id, price
                                                    FROM potions
                                                    WHERE
                                                    item_sku = :item_sku 
                                                    """),
                                                    [{"item_sku": item_sku}]).one()
        
        potion_id = result.id
        potion_price = result.price
        potion_quantity = cart_item.quantity

        connection.execute(sqlalchemy.text("""INSERT INTO cart_items 
                                           (cart_id, 
                                           potion_id, 
                                           item_sku, 
                                           price, 
                                           quantity) 
                                           VALUES 
                                           (:num_cart,
                                           :potion_id,
                                           :item_sku,
                                           :price,
                                           :quantity)"""),
                           [{"num_cart": cart_id, 
                             "potion_id": potion_id,
                             "item_sku": item_sku,
                             "price": potion_price,
                             "quantity": potion_quantity}])
        
        print(f"added {potion_quantity} {item_sku} to cart")

    return {"quantity": cart_item.quantity}


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("cart checkout")

    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("""SELECT
                                                    potion_id, price, quantity
                                                    FROM cart_items
                                                    WHERE
                                                    cart_id = :cart_id 
                                                    """),
                                                    [{"cart_id": cart_id}])
        
        gold_paid = 0
        potions_bought = 0

        for i in results:
            gold_paid += i.price * i.quantity
            potions_bought += i.quantity

            """remove potions from potion catalog"""
            connection.execute(sqlalchemy.text("""UPDATE potions
                                                SET quantity = quantity - :quantity
                                               WHERE id = :potion_id"""),
                                               [{"quantity": i.quantity, "potion_id": i.potion_id}])
            
        print(f"gold paid: {gold_paid}, potions bought: {potions_bought}")

        connection.execute(sqlalchemy.text("""UPDATE global_inventory
                                           SET gold = gold + :gold_paid, 
                                           num_potions = num_potions - :potions_bought
                                           """),
                                           [{"gold_paid": gold_paid, "potions_bought": potions_bought}])


    return {"total_potions_bought": potions_bought, "total_gold_paid": gold_paid}
