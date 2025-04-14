from flask import request
from urllib.parse import urlparse
import requests

@api.route('/check/url', methods=['POST'])
def check_url():
    url = request.json.get('url')
    try:
        # 快速HEAD请求检测
        resp = requests.head(
            url, 
            timeout=3,
            headers={'User-Agent': 'Mozilla/5.0'},
            allow_redirects=True
        )
        return {'status': 'success', 'code': resp.status_code}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 400