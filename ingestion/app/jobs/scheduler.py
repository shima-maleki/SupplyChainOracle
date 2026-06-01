import os
import time
from datetime import UTC, datetime

import httpx


BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
INGEST_INTERVAL_SECONDS = int(os.getenv("INGEST_INTERVAL_SECONDS", "3600"))


def run_once() -> None:
    url = f"{BACKEND_URL}/ingest/run"
    with httpx.Client(timeout=30) as client:
        response = client.post(url)
        response.raise_for_status()
        print(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "status": "ingestion_complete",
                "response": response.json(),
            },
            flush=True,
        )


def run_forever() -> None:
    while True:
        try:
            run_once()
        except Exception as exc:
            print(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "status": "ingestion_failed",
                    "error": str(exc),
                },
                flush=True,
            )
        time.sleep(INGEST_INTERVAL_SECONDS)


if __name__ == "__main__":
    if os.getenv("RUN_ONCE", "false").lower() == "true":
        run_once()
    else:
        run_forever()
