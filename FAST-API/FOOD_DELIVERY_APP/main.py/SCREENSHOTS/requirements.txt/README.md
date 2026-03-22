from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# -----------------------------
# Sample Data
# -----------------------------
menu = [
    {"id": 1, "name": "Pizza", "price": 200, "category": "Fast Food"},
    {"id": 2, "name": "Burger", "price": 100, "category": "Fast Food"},
    {"id": 3, "name": "Biryani", "price": 250, "category": "Main Course"}
]

orders = []
cart = []

# -----------------------------
# Pydantic Models
# -----------------------------
class Item(BaseModel):
    name: str = Field(..., min_length=2)
    price: float = Field(..., gt=0)
    category: str

class Order(BaseModel):
    item_ids: List[int]

# -----------------------------
# Helper Functions
# -----------------------------
def find_item(item_id: int):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None

def calculate_total(item_ids: List[int]):
    total = 0
    for i in item_ids:
        item = find_item(i)
        if item:
            total += item["price"]
    return total

def filter_logic(keyword: Optional[str]):
    if keyword:
        return [item for item in menu if keyword.lower() in item["name"].lower()]
    return menu

# -----------------------------
# Day 1: GET APIs
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to Food Delivery App"}

@app.get("/menu")
def get_menu():
    return menu

@app.get("/menu/{item_id}")
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/orders")
def get_orders():
    return orders

@app.get("/menu/summary")
def menu_summary():
    return {"total_items": len(menu)}

# -----------------------------
# Day 2: POST + Validation
# -----------------------------
@app.post("/menu", status_code=201)
def add_item(item: Item):
    new_item = item.dict()
    new_item["id"] = len(menu) + 1
    menu.append(new_item)
    return new_item

# -----------------------------
# Day 3: Helper Usage
# -----------------------------
@app.get("/menu/search")
def search_items(keyword: Optional[str] = Query(None)):
    return filter_logic(keyword)

# -----------------------------
# Day 4: CRUD
# -----------------------------
@app.put("/menu/{item_id}")
def update_item(item_id: int, updated: Item):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.update(updated.dict())
    return item

@app.delete("/menu/{item_id}")
def delete_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    menu.remove(item)
    return {"message": "Item deleted"}

# -----------------------------
# Day 5: Workflow
# -----------------------------
@app.post("/cart/add/{item_id}")
def add_to_cart(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    cart.append(item_id)
    return {"cart": cart}

@app.get("/cart")
def view_cart():
    return cart

@app.post("/order/create")
def create_order():
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = calculate_total(cart)
    order = {
        "order_id": len(orders) + 1,
        "items": cart.copy(),
        "total": total
    }
    orders.append(order)
    cart.clear()
    return order

# -----------------------------
# Day 6: Advanced APIs
# -----------------------------
@app.get("/menu/filter")
def filter_items(
    category: Optional[str] = None,
    max_price: Optional[float] = None
):
    result = menu

    if category:
        result = [i for i in result if i["category"].lower() == category.lower()]

    if max_price is not None:
        result = [i for i in result if i["price"] <= max_price]

    return result

@app.get("/menu/sort")
def sort_items(order: str = "asc"):
    return sorted(menu, key=lambda x: x["price"], reverse=(order == "desc"))

@app.get("/menu/paginate")
def paginate(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return menu[start:end]

@app.get("/menu/browse")
def browse(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    sort: Optional[str] = None
):
    result = filter_logic(keyword)

    if category:
        result = [i for i in result if i["category"].lower() == category.lower()]

    if sort:
        result = sorted(result, key=lambda x: x["price"], reverse=(sort == "desc"))

    return result
