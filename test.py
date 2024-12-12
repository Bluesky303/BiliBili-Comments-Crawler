import requests
from playwright.sync_api import *
url = "https://www.baidu.com"  # 测试网站url地址
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',}  # 请求头
proxies = {
    'http': 'http://47.98.100.129:80',
} 

with sync_playwright() as p:
    # 显示浏览器
    USER_DIR_PATH = f"C://Users/Blue_sky303/AppData/Local/Microsoft/Edge/User Data/Default"
    browser = p.chromium.launch_persistent_context(channel="msedge",user_data_dir=USER_DIR_PATH,headless=False,accept_downloads=True,args= ['--no-sandbox','--proxy-server=47.98.100.129:80'])
    # context.add_init_script(js)
    page = browser.new_page()
    page.pause()