from .loop import _get_event_loop, _create_event_loop
from .task import Task
from .sleep import sleep
from .sync import *
from .socket import asocket


def run(main):
    return _create_event_loop(main).run()


async def gather(*coros, raise_exception=False):
    tasks = [create_task(coro) for coro in coros]
    results = []
    for t in tasks:
        try:
            results.append(await t)
        except Exception as e:
            if raise_exception:
                raise e
            raise StopIteration
    return results


def create_task(coro):
    return _get_event_loop().create_task(coro)
