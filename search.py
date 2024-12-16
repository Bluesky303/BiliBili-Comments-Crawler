'''获取视频列表'''
import time
import csv
import requests
from playwright.sync_api import *
import os

# 找一个浏览器，我这里用edge，其实不找也行，用playwright装好的
USER_DIR_PATH = "C://Users/Blue_sky303/AppData/Local/Microsoft/Edge/User Data/Default"

#找一下位置，加点目录
CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
CURRENT_DIR = CURRENT_DIR.replace("\\","/")
if not os.path.exists(CURRENT_DIR+'/results'):
    os.mkdir(CURRENT_DIR+'/results')
if not os.path.exists(CURRENT_DIR+'/results/csv'):
    os.mkdir(CURRENT_DIR+'/results/csv')


# 获取cookies
def setBiliBiliCookies(bv='BV1GJ411x7h7') -> str: 
    url = f'https://www.bilibili.com/video/'+bv
    # 模拟浏览器方式获取cookies
    try:
        with sync_playwright() as p:
            # 打开浏览器
            browser = p.chromium.launch_persistent_context(channel="msedge",user_data_dir=USER_DIR_PATH,headless=True,accept_downloads=True)
            page = browser.new_page()
            page.goto(url, timeout=5000)  # 设置超时时间为5s
            cookies = browser.cookies()
            page.close()
            browser.close()
            # os.system("taskkill /f /im msedge.exe") # edge占后台
            # 转换格式
            runCookies = ""
            for data in cookies:
                if data['domain'] == '.bilibili.com': runCookies += data['name'] + "=" + data['value'] + "; "
        cookies = runCookies
        return cookies
    except:
        return ''

# 根据关键词和时间范围检索视频列表
def search_video_list(keyword: str, begin_time = 0, end_time = 0, maxpage = 50, order = 'click', sleeptime = 0.1) -> list:
    return_dict = []
    page = 1
    # 请求头
    headers = {
    'cookie': setBiliBiliCookies(),
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47'
}
    # 遍历页码，最大页码超出跳报错break
    while page<maxpage+1:
        print_begin_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(begin_time))
        print_end_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(end_time))
        print(f"时间段{print_begin_time}-{print_end_time}-搜索{keyword}-第{page}页")
        
        # b站搜索api
        mainUrl = 'https://api.bilibili.com/x/web-interface/search/type'
        
        # api参数
        params = {
            'search_type': 'video',
            'keyword': keyword,
            'page': page,
            'order': order,
        }
        
        # 为0则不需要设置对应时间范围
        if begin_time: params['pubtime_begin_s'] = begin_time
        if end_time: params['pubtime_end_s'] = end_time
        
        try:
            response = requests.get(mainUrl, headers=headers, params=params)
            
            # 检查响应状态码是否为200，即成功
            if response.status_code == 200:
                data = response.json()
                if not data['data']['result']: break # 没返回大概就是翻页翻完了
                # 遍历结果视频列表
                for video_num in range(20):
                    video_data = data['data']['result'][video_num]
                    
                    # 挑选需要的数据
                    video_info = {
                        'author': video_data['author'],
                        'bvid': video_data['bvid'],
                        'title': video_data['title'],
                        'play': video_data['play'],
                        'video_review': video_data['video_review'],
                        'favorites': video_data['favorites'],
                        'review': video_data['review'],
                        'date': video_data['pubdate'],
                    }
                    return_dict.append(video_info)
                    
            elif response.status_code == 412: # 412码，大概是被封ip了，歇着或者换ip罢
                print(time.asctime())
                print("412error")
                time.sleep(300)
            else:
                print(f'请求失败，状态码：{response.status_code}')
                break
            response.close()   
        except Exception as e:
            print('发生错误', e)
            break
        time.sleep(sleeptime)  # 控制请求频率
        page+=1
    print("爬取完成")
    return return_dict

# 数据写入csv
def write_csv(inputlist,filename = 'default.csv'):
    with open(CURRENT_DIR+'/result/csv/'+filename,'w',newline='',encoding='utf-8') as f:
        fields = ['author', 'bvid', 'title', 'play', 'video_review', 'favorites', 'review', 'date']
        writer = csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for item in inputlist: writer.writerow(item)
    f.close()
