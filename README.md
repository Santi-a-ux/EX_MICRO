# Microservicios de ejemplo (orders + payments)

Este repositorio contiene un ejemplo mínimo en Python con FastAPI para ilustrar una arquitectura tipo microservicios y una mini-saga: OrderCreated → PaymentAuthorized → OrderConfirmed.

Estructura:

- `orders.py` — Servicio de Pedidos (orquesta la saga, puerto 8000)
- `payments.py` — Servicio de Pagos (autoriza pagos, puerto 8001)
- `requirements.txt` — dependencias mínimas

Cómo ejecutarlo (Windows / PowerShell)

1. Abrir Terminal 1 y arrancar Payments:

```pwsh
pip install -r requirements.txt
uvicorn payments:app --reload --port 8001
```

2. Abrir Terminal 2 y arrancar Orders:

```pwsh
uvicorn orders:app --reload --port 8000
```

3. En Terminal 3 (o la misma), ejecutar el script de demostración automático:

```pwsh
python run_demo.py
```
