from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uuid

app = FastAPI(title="orders-service")

class OrderIn(BaseModel):
    items: list[str]
    total: float

orders: dict[str, dict] = {}

PAYMENTS_URL = "http://localhost:8001/pay"

@app.post("/orders")
def create_order(order: OrderIn):
    oid = str(len(orders) + 1)
    orders[oid] = {"id": oid, "status": "CREATED", "total": order.total, "items": order.items}

    idem = str(uuid.uuid4())
    try:
        resp = httpx.post(
            PAYMENTS_URL,
            json={"order_id": oid, "amount": order.total, "idempotency_key": idem},
            timeout=3.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "AUTHORIZED":
            orders[oid]["status"] = "CONFIRMED"
        else:
            orders[oid]["status"] = "REJECTED"
    except Exception as e:
        orders[oid]["status"] = "PENDING_PAYMENT"
        orders[oid]["error"] = str(e)

    return orders[oid]


@app.get("/orders/{oid}")
def get_order(oid: str):
    if oid not in orders:
        raise HTTPException(status_code=404, detail="not found")
    return orders[oid]
