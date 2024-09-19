import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# 目标URL
url = "https://chinanonfiction.com/"

async def main():
    # 使用 Playwright 打开网页
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)  # 无头模式，不打开浏览器窗口
        page = await browser.new_page()
        
        # 打开网页
        await page.goto(url)
        
        # 等待页面加载完成
        await page.wait_for_load_state('networkidle')  # 等待网络空闲
        
        # 获取页面源代码
        page_source = await page.content()
        
        # 关闭浏览器
        await browser.close()

    # 解析HTML内容
    soup = BeautifulSoup(page_source, 'html.parser')

    # 打印网页标题
    print("网页标题:", soup.title.string)

    # 提取所有文章标题
    articles = soup.find_all('h2', class_='entry-title')
    for article in articles:
        print("文章标题:", article.text.strip())

# 运行异步主函数
asyncio.run(main())