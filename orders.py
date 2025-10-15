# orders_service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uuid

app = FastAPI(title="orders-service")

class OrderIn(BaseModel):
    items: list[str]
    total: float

orders: dict[str, dict] = {}  # "BD" en memoria

PAYMENTS_URL = "http://localhost:8001/pay"  # endpoint del servicio de pagos

@app.post("/orders")
def create_order(order: OrderIn):
    oid = str(len(orders)+1)
    orders[oid] = {"id": oid, "status": "CREATED", "total": order.total, "items": order.items}

    # Paso 1 de la saga: autorizar pago (sincrónico aquí, podría ser evento)
    idem = str(uuid.uuid4())
    try:
        resp = httpx.post(PAYMENTS_URL, json={
            "order_id": oid, "amount": order.total, "idempotency_key": idem
        }, timeout=3.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "AUTHORIZED":
            orders[oid]["status"] = "CONFIRMED"  # Paso 2: confirmar orden
        else:
            orders[oid]["status"] = "REJECTED"
    except Exception as e:
        # Mitigaciones típicas: retry/backoff, cola outbox, compensación, etc.
        orders[oid]["status"] = "PENDING_PAYMENT"
        orders[oid]["error"] = str(e)

    return orders[oid]

@app.get("/orders/{oid}")
def get_order(oid: str):
    if oid not in orders:
        raise HTTPException(status_code=404, detail="not found")
    return orders[oid]
