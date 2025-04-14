from .services.task_queue import crawl_queue
from .services.websocket import ProgressReporter

async def crawl_site(url, depth, task_id):
    reporter = ProgressReporter(task_id)
    
    try:
        # 加入队列等待执行
        await crawl_queue.add_task(_crawl_site, url, depth, reporter)
    except Exception as e:
        reporter.update(0, 'failed', str(e))

async def _crawl_site(url, depth, reporter):
    """实际爬取逻辑"""
    reporter.update(0, 'analyzing', '开始分析页面结构')
    
    browser = await launch(headless=True)
    page = await browser.newPage()
    
    try:
        # 示例：分阶段更新进度
        await page.goto(url)
        reporter.update(30, 'running', '加载页面完成')
        
        # 爬取逻辑...
        await asyncio.sleep(1)
        reporter.update(60, 'running', '提取交互元素')
        
        # 更多操作...
        reporter.update(90, 'running', '数据存储中')
        
        reporter.update(100, 'completed', '任务完成')
    finally:
        await browser.close()