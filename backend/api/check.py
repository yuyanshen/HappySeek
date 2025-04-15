from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from . import api
import aiohttp
import asyncio
from urllib.parse import urlparse
import re

class UrlValidationAPI(Resource):
    @jwt_required()
    def post(self):
        """验证URL的可访问性和合法性"""
        data = request.get_json()
        urls = data.get('urls', [])
        
        if isinstance(urls, str):
            urls = [urls]
            
        if not urls:
            return {'error': 'No URLs provided'}, 400
            
        results = asyncio.run(self._check_urls(urls))
        return {'results': results}
        
    async def _check_urls(self, urls):
        async def check_single_url(url):
            # 基本URL格式验证
            if not self._is_valid_url_format(url):
                return {
                    'url': url,
                    'valid': False,
                    'error': 'Invalid URL format'
                }
                
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.head(url, allow_redirects=True, timeout=5) as response:
                        return {
                            'url': url,
                            'valid': response.status < 400,
                            'status': response.status,
                            'content_type': response.headers.get('content-type', ''),
                            'redirected': response.real_url != url if response.real_url else False
                        }
            except aiohttp.ClientError as e:
                return {
                    'url': url,
                    'valid': False,
                    'error': str(e)
                }
                
        tasks = [check_single_url(url) for url in urls]
        return await asyncio.gather(*tasks)
        
    def _is_valid_url_format(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

class RobotsCheckAPI(Resource):
    @jwt_required()
    def post(self):
        """检查网站的robots.txt规则"""
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return {'error': 'URL is required'}, 400
            
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        try:
            response = asyncio.run(self._fetch_robots(robots_url))
            return response
        except Exception as e:
            return {'error': str(e)}, 500
            
    async def _fetch_robots(self, robots_url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=5) as response:
                    if response.status == 200:
                        text = await response.text()
                        return {
                            'exists': True,
                            'content': text,
                            'rules': self._parse_robots(text)
                        }
                    return {
                        'exists': False,
                        'status': response.status
                    }
        except aiohttp.ClientError as e:
            return {
                'exists': False,
                'error': str(e)
            }
            
    def _parse_robots(self, content):
        rules = []
        current_agent = '*'
        
        for line in content.split('\n'):
            line = line.strip().lower()
            if not line or line.startswith('#'):
                continue
                
            if line.startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
            elif line.startswith('disallow:') or line.startswith('allow:'):
                rule_type, path = line.split(':', 1)
                rules.append({
                    'agent': current_agent,
                    'type': rule_type.strip(),
                    'path': path.strip()
                })
                
        return rules

class SitemapCheckAPI(Resource):
    @jwt_required()
    def post(self):
        """检查网站的sitemap.xml"""
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return {'error': 'URL is required'}, 400
            
        parsed = urlparse(url)
        sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
        
        try:
            response = asyncio.run(self._fetch_sitemap(sitemap_url))
            return response
        except Exception as e:
            return {'error': str(e)}, 500
            
    async def _fetch_sitemap(self, sitemap_url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sitemap_url, timeout=5) as response:
                    if response.status == 200:
                        text = await response.text()
                        return {
                            'exists': True,
                            'content': text,
                            'urls': self._extract_urls(text)
                        }
                    return {
                        'exists': False,
                        'status': response.status
                    }
        except aiohttp.ClientError as e:
            return {
                'exists': False,
                'error': str(e)
            }
            
    def _extract_urls(self, content):
        urls = []
        url_pattern = re.compile(r'<loc>(.*?)</loc>')
        matches = url_pattern.findall(content)
        return matches

# 注册API路由
api.add_resource(UrlValidationAPI, '/check/url')
api.add_resource(RobotsCheckAPI, '/check/robots')
api.add_resource(SitemapCheckAPI, '/check/sitemap')