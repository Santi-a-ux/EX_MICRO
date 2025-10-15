# payments_service/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="payments-service")

class PaymentIn(BaseModel):
    order_id: str
    amount: float
    idempotency_key: str | None = None  # evita doble cobro en reintentos

# "base de datos" en memoria
authorized: dict[str, dict] = {}

@app.post("/pay")
def pay(body: PaymentIn):
    if body.idempotency_key and body.idempotency_key in authorized:
        return authorized[body.idempotency_key]  # idempotente

    result = {"order_id": body.order_id, "status": "AUTHORIZED", "amount": body.amount}
    if body.idempotency_key:
        authorized[body.idempotency_key] = result
    return result
