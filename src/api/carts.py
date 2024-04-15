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

    """create global dict on first run"""
    global cart_dict
    if 'cart_dict' not in globals():
        cart_dict = {}
    """TODO: create a cart id (unique if you are not only selling one bottle at a time)"""
    '''TODO: create a new column of cart ids, increment, then select and update based off of data'''
    with db.engine.begin() as connection:
        print("create cart")
        result = connection.execute(sqlalchemy.text("SELECT num_carts FROM global_inventory"))
        num_cart = result.fetchone()[0]
        num_cart += 1
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_carts = {num_cart}"))
        print(f"cart id: {num_cart}")

        cart_dict[num_cart] = MyCart(0,0,0)
        print(f"cart_dict (rgb): {cart_dict[num_cart].red}, {cart_dict[num_cart].green}, {cart_dict[num_cart].blue}")

    return {"cart_id": num_cart}

'''created my own class MyCart to store in dict'''
class MyCart():
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    """TODO: give them SKU REGEX"""
    if(item_sku == 'RED_POTION_0'):
        cart_dict[cart_id].red = cart_item.quantity
        print(f"add {cart_item.quantity} red to cart")
    elif(item_sku == 'GREEN_POTION_0'):
        cart_dict[cart_id].green = cart_item.quantity
        print(f"add {cart_item.quantity} green to cart")
    else:
        cart_dict[cart_id].blue = cart_item.quantity
        print(f"add {cart_item.quantity} blue to cart")

    return {"quantity": cart_item.quantity}


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    """TODO: update minus potions, add gold"""
    print("cart checkout")
    with db.engine.begin() as connection:
        '''TODO: only sell 1 green potion at a time'''
        '''TODO: minus red and blue potions'''
        '''update in deliver'''
        search_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
        search_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        row_potions = search_potions.fetchone()
        num_red_potion = row_potions[0]
        num_green_potion = row_potions[1]
        num_blue_potion = row_potions[2]

        print(f"current num rgb potions: {num_red_potion}, {num_green_potion}, {num_blue_potion}")

        num_gold = search_gold.fetchone()[0]
        print(f"current num gold: {num_gold}")

        new_num_red_potion = num_red_potion - cart_dict[cart_id].red
        new_num_green_potion = num_green_potion - cart_dict[cart_id].green
        new_num_blue_potion = num_blue_potion - cart_dict[cart_id].blue

        total_potions = cart_dict[cart_id].red + cart_dict[cart_id].green + cart_dict[cart_id].blue
        new_num_gold = num_gold + (30 * total_potions)
        print(f"updated num rgb potions: {new_num_red_potion}, {new_num_green_potion}, {new_num_blue_potion}")
        print(f"new gold: {new_num_gold}")

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = '{new_num_red_potion}', num_green_potions = '{new_num_green_potion}', num_blue_potions = '{new_num_blue_potion}'"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = '{new_num_gold}'"))

        check = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions, gold FROM global_inventory"))
        for row in check:
            print(f"updated rgb potion and gold - sell: {row}")
    
    return {"total_potions_bought": total_potions, "total_gold_paid": 30 * total_potions}
