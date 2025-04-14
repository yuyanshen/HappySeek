@api.route('/crawler/check-login', methods=['POST'])
def check_login_page():
    url = request.json.get('url')
    
    # 使用无头浏览器检测登录表单
    async def detect_login():
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url)
        
        has_login = await page.evaluate('''() => {
            const inputs = document.querySelectorAll('input[type="password"], input[name*="pass"]')
            return inputs.length > 0
        }''')
        
        await browser.close()
        return has_login
    
    requires_login = asyncio.run(detect_login())
    return {'requiresLogin': requires_login}