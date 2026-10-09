import json
import os
import uuid
from datetime import datetime, timezone
from typing import List

import boto3
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel, Field

# Set by template.yaml when deployed. Leave unset locally to skip EventBridge.
EVENT_BUS_NAME = os.environ.get("EVENT_BUS_NAME")

events = boto3.client("events") if EVENT_BUS_NAME else None

app = FastAPI(title="E-Commerce Orders API")

PRODUCTS = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 50},
    2: {"id": 2, "name": "Headphones", "price": 149.99, "stock": 120},
    3: {"id": 3, "name": "Mouse", "price": 29.99, "stock": 75},
}

# In-memory only — resets whenever Lambda starts a new container.
ORDERS = {}


class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderRequest(BaseModel):
    customer_email: str
    items: List[OrderItem]


def publish_order_placed(order):
    if not events:
        print(f"[local] would publish OrderPlaced: {order['order_id']}")
        return
    events.put_events(
        Entries=[
            {
                "EventBusName": EVENT_BUS_NAME,
                "Source": "ecommerce.orders",
                "DetailType": "OrderPlaced",
                "Detail": json.dumps(order),
            }
        ]
    )


@app.get("/products")
def list_products():
    return {"total": len(PRODUCTS), "products": list(PRODUCTS.values())}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = PRODUCTS.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/orders", status_code=201)
def create_order(request: OrderRequest):
    lines = []
    for item in request.items:
        product = PRODUCTS.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        lines.append({
            "product_id": product["id"],
            "name": product["name"],
            "quantity": item.quantity,
            "price": product["price"],
        })

    order = {
        "order_id": str(uuid.uuid4()),
        "customer_email": request.customer_email,
        "items": lines,
        "total": round(sum(l["price"] * l["quantity"] for l in lines), 2),
        "status": "PLACED",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ORDERS[order["order_id"]] = order
    publish_order_placed(order)
    return {"message": "Order placed", "order": order}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Lambda entry point — Mangum converts API Gateway events into ASGI requests for FastAPI.
handler = Mangum(app)
