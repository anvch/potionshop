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
    """TODO: create a cart id (unique if you are not only selling one bottle at a time)"""
    '''TODO: create a new column of cart ids, increment, then select and update based off of data'''
    print("create cart")
    return {"cart_id": 1}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    """TODO: give them SKU REGEX"""
    """can hack this for ver1 by only selling one green potion at a time in catalog"""
    """then at checkout you know exactly what the customer is coming for"""
    '''TODO based on item_sku, reutrn a cart_checkout type of the total they have to pay'''
    
    print("set item quantity - do nothing for now")

    return {"quantity": 1}


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
        search_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        search_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        for row in search_potions:
            print(row)
            num_green_potion = row[0]
        print(f"current num green potions: {num_green_potion}")

        for row in search_gold:
            print(row)
            num_gold = row[0]
        print(f"current num gold: {num_gold}")

        new_num_green_potion = num_green_potion - 1
        new_num_gold = num_gold + 1
        print(new_num_green_potion)
        print(num_gold)

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = '{new_num_green_potion}'"))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = '{new_num_gold}'"))

        check = connection.execute(sqlalchemy.text("SELECT num_green_potions, gold FROM global_inventory"))
        for row in check:
            print(f"updated potion and gold - sell 1: {row}")
    
    return {"total_potions_bought": 1, "total_gold_paid": 1}
