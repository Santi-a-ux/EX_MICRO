# Microservicios de ejemplo (orders + payments)

Este repositorio contiene un ejemplo mínimo en Python con FastAPI para ilustrar una arquitectura tipo microservicios y una mini-saga: OrderCreated → PaymentAuthorized → OrderConfirmed.

Estructura:

- `orders.py` — Servicio de Pedidos (orquesta la saga, puerto 8000)
- `payments.py` — Servicio de Pagos (autoriza pagos, puerto 8001)
- `requirements.txt` — dependencias mínimas

Cómo ejecutarlo (Windows / PowerShell)

1. Crear un entorno virtual (opcional pero recomendado):

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```


2. En terminal 1 — arrancar Payments (puerto 8001):

```pwsh
uvicorn payments:app --reload --port 8001
```

3. En terminal 2 — arrancar Orders (puerto 8000):

```pwsh
uvicorn orders:app --reload --port 8000
```


Prueba rápida (curl o httpie):

```pwsh
curl -X POST http://localhost:8000/orders -H "Content-Type: application/json" -d '{"items":["sku-1","sku-2"], "total": 99.9}'
curl http://localhost:8000/orders/1
```

Flujo recomendado para una presentación (sencillo y claro)

- Objetivo: mostrar los conceptos clave de microservicios y una saga sin entrar en infraestructura compleja.
- Por qué es buena opción: todo es local, pocas dependencias, se ve la llamada HTTP entre servicios, hay idempotencia demostrable y se puede simular fallos fácilmente.

Pasos para la demo (PowerShell):

1. Abrir Terminal 1 y arrancar Payments:

```pwsh
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

Qué mostrar mientras corre:

- Menciona el diagrama simple: OrderService crea orden -> llama Payments -> Payments responde AUTHORIZED -> OrderService marca CONFIRMED.
- Explica la idempotencia (payments guarda por idempotency_key).
- Simular fallo: cierra el servicio de payments y vuelve a ejecutar `run_demo.py` o la petición manual; la orden quedará en PENDING_PAYMENT y puedes explicar técnicas para resolverlo (retries, outbox, compensaciones).

Notas adicionales:

- Si prefieres usar la import path `orders_service.main` / `payments_service.main` como en el ejemplo original, mueve los archivos a carpetas y ajusta los comandos uvicorn.
- Para una versión más avanzada, puedo añadir un script que simule rechazos aleatorios en `payments.py` y mostrar compensaciones.


Qué falta / notas:

- Los módulos en este ejemplo están en archivos llamados `orders.py` y `payments.py`, pero el README asume paquetes `orders_service.main` y `payments_service.main`. Puedes ejecutar directamente los archivos (por ejemplo `uvicorn orders:app`) o renombrar/reestructurar en carpetas `orders_service` y `payments_service` si prefieres mantener esa convención.
- No hay persistencia real: ambos servicios usan estructuras en memoria. Reiniciar el proceso borra los datos.
- No hay autenticación ni TLS.
- No hay retries/exponential backoff ni outbox pattern — para una demo más realista se pueden añadir.
- Para un ejemplo con eventos (desacoplado), usar un broker (RabbitMQ/Kafka) y un patrón de sagas con compensaciones.
