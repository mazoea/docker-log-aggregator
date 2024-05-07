import docker
import time
import argparse
import logging
import os
from datetime import datetime


logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger("dlog")
_logger.setLevel(logging.DEBUG)


class ts:
    def __init__(self):
        self.since = None
        self.until = None
        self.update()

    def update(self):
        self.since = self.until
        self.until = datetime.utcnow()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Log docker container logs to a file.')
    parser.add_argument('--log', help='Output file', type=str, default="./__docker.log")
    parser.add_argument('--sleep', type=int, default=10)
    flags = parser.parse_args()

    _logger.info(f"Logs written to {flags.log}")
    os.makedirs(os.path.dirname(flags.log), exist_ok=True)
    curts = ts()

    if os.path.exists(flags.log):
        _logger.info(f"Removing {flags.log}")
        os.remove(flags.log)

    client = docker.from_env()
    while True:
        with open(flags.log, 'a', newline="\n") as fout:
            containers = client.containers.list(all=False)
            for c in containers:
                logs = c.logs(since=curts.since, until=curts.until,
                              timestamps=True).decode('utf-8')
                logs = "\n".join(
                    f"{'|'.join(c.image.tags)}:{c.name}:{x}" for x in logs.splitlines())
                fout.write(logs)
        time.sleep(flags.sleep)
        curts.update()
