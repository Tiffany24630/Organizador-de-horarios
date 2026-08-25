"""Entry point used by Electron and by the PyInstaller desktop bundle."""

import multiprocessing
import os

import uvicorn
from app.main import app


def main():
    host = os.environ.get("SCHEDULER_HOST", "127.0.0.1")
    port = int(os.environ.get("SCHEDULER_PORT", "8765"))
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=os.environ.get("SCHEDULER_LOG_LEVEL", "warning"),
        access_log=False,
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
