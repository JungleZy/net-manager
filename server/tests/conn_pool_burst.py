import threading
import time
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from src.database.connection_pool import ConnectionPool

def worker(pool, results, idx):
    try:
        with pool.get_connection_context() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            results[idx] = True
    except Exception:
        results[idx] = False

def run():
    pool = ConnectionPool(db_path="net_manager_server.db", max_connections=5, acquire_timeout=1.0)
    threads = []
    results = [False] * 20
    for i in range(20):
        t = threading.Thread(target=worker, args=(pool, results, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    ok = sum(1 for r in results if r)
    print(f"success={ok} fail={len(results)-ok}")

if __name__ == "__main__":
    run()
