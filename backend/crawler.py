# backend/crawler.py
class AdvancedCrawler:
    def __init__(self, task_id):
        self.task_id = task_id
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=1)

    async def update_progress(self, current, total):
        progress = int((current / total) * 100)
        self.redis.hset(self.task_id, 'progress', str(progress))

    async def run(self, urls, max_depth):
        total_urls = len(urls)
        for i, url in enumerate(urls):
            await self.crawl_page(url, 0, max_depth)
            await self.update_progress(i+1, total_urls)
        
        # 返回采集到的元素总数
        return self.get_element_count()

    # ... (保留之前的爬虫方法)