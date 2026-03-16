from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
]

orders = []
feedback_list = []

class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]

@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}

@app.post("/products", status_code=201)
def add_product(product: Product):
    for p in products:
        if p["name"].lower() == product.name.lower():
            return {"error": "Product with this name already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }

@app.put("/products/discount")
def apply_discount(
    category: str = Query(...),
    discount_percent: int = Query(..., ge=1, le=99)
):

    updated_products = []

    for product in products:

        if product["category"].lower() == category.lower():

            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price

            updated_products.append({
                "name": product["name"],
                "new_price": new_price
            })

    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated_products),
        "products": updated_products
    }

@app.get("/products/audit")
def products_audit():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }

@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {"products": result, "count": len(result)}

@app.get("/products/instock")
def get_instock_products():

    instock_products = [p for p in products if p["in_stock"]]

    return {
        "in_stock_products": instock_products,
        "count": len(instock_products)
    }

@app.get("/products/filter")
def filter_products(
    category: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    in_stock: bool = Query(None)
):

    result = products

    if category:
        result = [p for p in result if p["category"] == category]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"filtered_products": result, "count": len(result)}

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matched = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not matched:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched,
        "count": len(matched)
    }

@app.get("/products/deals")
def get_product_deals():

    best_deal = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])

    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:

        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    price: int = Query(None),
    in_stock: bool = Query(None)
):

    for product in products:

        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": product
            }

    return {"error": "Product not found"}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for product in products:

        if product["id"] == product_id:

            products.remove(product)

            return {
                "message": f"Product '{product['name']}' deleted"
            }

    return {"error": "Product not found"}

@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:

        if product["id"] == product_id:
            return {"product": product}

    return {"error": "Product not found"}

@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock = len([p for p in products if p["in_stock"]])

    out_of_stock = len([p for p in products if not p["in_stock"]])

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }

@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_of_stock_count = len([p for p in products if not p["in_stock"]])

    cheapest = min(products, key=lambda p: p["price"])
    most_expensive = max(products, key=lambda p: p["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

@app.post("/feedback")
def submit_feedback(feedback: CustomerFeedback):

    feedback_list.append(feedback.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": feedback,
        "total_feedback": len(feedback_list)
    }

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

@app.post("/orders")
def create_order(order: BulkOrder):

    order_id = len(orders) + 1

    new_order = {
        "order_id": order_id,
        "company": order.company_name,
        "items": order.items,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:

        if order["order_id"] == order_id:
            return order

    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:

        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}
