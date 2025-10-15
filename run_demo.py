"""run_demo.py

Script minimal para la demo:
- crea una orden (POST /orders)
- consulta el estado (GET /orders/{id})

Úsalo mientras ambos servicios están levantados.
"""
import json
import time
import httpx

ORDERS_URL = "http://localhost:8000/orders"

def main():
    payload = {"items": ["sku-1", "sku-2"], "total": 99.9}
    print("Creando orden...")
    try:
        resp = httpx.post(ORDERS_URL, json=payload, timeout=5.0)
        resp.raise_for_status()
    except Exception as e:
        print("Error al crear orden (¿payments levantado?):", e)
        return

    data = resp.json()
    print("Respuesta POST /orders:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    oid = data.get("id")
    if not oid:
        print("La respuesta no contiene id de orden. Fin.")
        return

    # Espera corta para que el state se actualice si es necesario
    time.sleep(0.5)

    print(f"Consultando estado de la orden {oid}...")
    try:
        resp2 = httpx.get(f"http://localhost:8000/orders/{oid}", timeout=5.0)
        resp2.raise_for_status()
    except Exception as e:
        print("Error al consultar la orden:", e)
        return

    print("Respuesta GET /orders/{id}:")
    print(json.dumps(resp2.json(), indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
