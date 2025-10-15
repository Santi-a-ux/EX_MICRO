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

# POR SI FALLA UVICORN
if __name__ == '__main__':
    import sys

    def start_service(module: str, port: int):
        import subprocess

        cmd = [sys.executable, "-m", "uvicorn", f"{module}:app", "--port", str(port)]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return proc
        except Exception as e:
            print(f"Error al arrancar {module} en el puerto {port}: {e}")
            return None

    def wait_for(url: str, timeout: float = 10.0):
        start = time.time()
        while time.time() - start < timeout:
            try:
                r = httpx.get(url, timeout=1.0)
                if r.status_code < 500:
                    return True
            except Exception:
                pass
            time.sleep(0.2)
        return False

    def demo_auto_start():
        print("Arrancando servicios (payments y orders)...")
        p_pay = start_service("payments", 8001)
        if not p_pay:
            print("No se pudo arrancar payments. Asegúrate de tener uvicorn instalado en el entorno.")
            return

        if not wait_for("http://localhost:8001/docs", timeout=10):
            print("Payments no respondió a tiempo. Abortando.")
            p_pay.terminate()
            return

        p_ord = start_service("orders", 8000)
        if not p_ord:
            print("No se pudo arrancar orders. Terminando payments.")
            p_pay.terminate()
            return

        if not wait_for("http://localhost:8000/docs", timeout=10):
            print("Orders no respondió a tiempo. Terminando procesos.")
            p_ord.terminate()
            p_pay.terminate()
            return

        try:
            main()
        finally:
            print("Deteniendo servicios...")
            for proc in (p_ord, p_pay):
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass

    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        demo_auto_start()
    else:
        main()
