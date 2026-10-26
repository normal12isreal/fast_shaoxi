"""阻塞模型调用的执行边界：限额跟随真实线程，而不是 HTTP 等待时间。"""

import asyncio
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")


class BusyError(Exception):
    pass


class ExecutionPool:
    def __init__(self, workers: int = 1, timeout: float = 180):
        self.timeout = timeout
        self._slots = threading.BoundedSemaphore(workers)
        self._executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="model")

    async def run(self, function: Callable[[], T]) -> T:
        if not self._slots.acquire(blocking=False):
            raise BusyError
        try:
            future = self._executor.submit(function)
        except BaseException:
            self._slots.release()
            raise
        # 只有底层调用真正结束才还名额；HTTP 超时、取消都不会提前释放。
        future.add_done_callback(lambda _: self._slots.release())
        wrapped = asyncio.wrap_future(future)
        # HTTP 已离开时也消费后台异常，避免无人读取的 future 警告。
        wrapped.add_done_callback(lambda done: None if done.cancelled() else done.exception())
        return await asyncio.wait_for(asyncio.shield(wrapped), timeout=self.timeout)

    def close(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=False)
