from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import json
from datetime import datetime
from .proxy_pool import ProxyPool
from .anti_anti_crawl import AntiAntiCrawler

class SmartCrawler:
    def __init__(self, task_id):
        self.task_id = task_id
        self.proxy_pool = ProxyPool()
        self.anti_crawler = AntiAntiCrawler()
        self.crawl_stats = {
            'start_time': datetime.now(),
            'pages_crawled': 0,
            'elements_found': 0,
            'errors': []
        }
        
    async def detect_site_structure(self, url):
        """智能识别网站结构"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until='networkidle')
                
                # 分析页面结构
                structure = await page.evaluate('''() => {
                    return {
                        links: Array.from(document.querySelectorAll('a')).map(a => ({
                            href: a.href,
                            text: a.textContent.trim(),
                            location: {
                                x: a.getBoundingClientRect().x,
                                y: a.getBoundingClientRect().y
                            }
                        })),
                        forms: Array.from(document.querySelectorAll('form')).map(form => ({
                            action: form.action,
                            method: form.method,
                            fields: Array.from(form.elements).map(el => ({
                                name: el.name,
                                type: el.type
                            }))
                        })),
                        possibleLoginForm: document.querySelector('input[type="password"]') !== null
                    }
                }''')
                
                return structure
                
            finally:
                await browser.close()
    
    async def adaptive_crawl(self, url, depth=2):
        """自适应爬取策略"""
        structure = await self.detect_site_structure(url)
        browser_context_args = {
            'proxy': self.proxy_pool.get_random(),
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': self.anti_crawler.get_random_ua()
        }
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(**browser_context_args)
            
            try:
                page = await context.new_page()
                await page.goto(url, wait_until='networkidle')
                
                # 智能提取关键信息
                content = await self._extract_content(page)
                self.crawl_stats['elements_found'] += len(content)
                
                # 递归爬取子页面
                if depth > 0:
                    for link in structure['links']:
                        try:
                            await self.adaptive_crawl(link['href'], depth - 1)
                        except Exception as e:
                            self.crawl_stats['errors'].append({
                                'url': link['href'],
                                'error': str(e)
                            })
                
                return content
                
            finally:
                await browser.close()
    
    async def _extract_content(self, page):
        """智能内容提取"""
        return await page.evaluate('''() => {
            const results = [];
            
            // 提取文本内容
            document.querySelectorAll('p, h1, h2, h3, article').forEach(el => {
                if (el.textContent.trim().length > 50) {
                    results.push({
                        type: 'text',
                        content: el.textContent.trim(),
                        element: el.tagName
                    });
                }
            });
            
            // 提取图片
            document.querySelectorAll('img').forEach(img => {
                if (img.naturalWidth > 100 && img.naturalHeight > 100) {
                    results.push({
                        type: 'image',
                        src: img.src,
                        alt: img.alt
                    });
                }
            });
            
            return results;
        }''')