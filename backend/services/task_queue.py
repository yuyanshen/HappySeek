import asyncio
from collections import deque

class CrawlQueue:
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.active_tasks = set()
        self.pending_queue = deque()
        self.loop = asyncio.get_event_loop()
        
    async def add_task(self, task_func, *args):
        """添加任务到队列"""
        if len(self.active_tasks) >= self.max_concurrent:
            future = self.loop.create_future()
            self.pending_queue.append((future, task_func, args))
            await future
        else:
            await self._execute(task_func, *args)
    
    async def _execute(self, task_func, *args):
        """实际执行任务"""
        task = asyncio.create_task(task_func(*args))
        self.active_tasks.add(task)
        task.add_done_callback(self._on_task_done)
        
    def _on_task_done(self, task):
        """任务完成回调"""
        self.active_tasks.remove(task)
        if self.pending_queue:
            future, task_func, args = self.pending_queue.popleft()
            future.set_result(None)
            asyncio.create_task(self._execute(task_func, *args))

# 全局队列实例
crawl_queue = CrawlQueue(max_concurrent=10)