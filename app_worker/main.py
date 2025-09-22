from __future__ import annotations

import logging

from rq import Connection, Worker

from core.config import get_settings
from core.queue import get_queue, get_redis_connection

logging.basicConfig(level=logging.INFO)


def main() -> None:
    settings = get_settings()
    queue = get_queue(settings.RQ_QUEUE_NAME)

    with Connection(get_redis_connection()):
        worker = Worker([queue.name])
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
