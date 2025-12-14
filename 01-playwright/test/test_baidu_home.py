import re
from playwright.sync_api import Page, expect

BAIDU = "https://www.baidu.com"

def test_home_title(page: Page):
    page.goto(BAIDU, wait_until="domcontentloaded")
    # 断言标题包含“百度”
    expect(page).to_have_title(re.compile("百度"))


def test_top_nav_visible(page: Page):
    page.goto(BAIDU, wait_until="domcontentloaded")
    # 断言：右上角导航中至少有“新闻/地图/贴吧”等之一出现（页面版本差异较大，用或逻辑）
    nav_text = page.locator("body").inner_text()
    assert any(k in nav_text for k in ["新闻", "地图", "贴吧", "视频", "图片"])
