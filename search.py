'''获取视频列表'''
import time
import requests
from playwright.sync_api import *
import os
import pandas as pd

# 找一个浏览器，我这里用edge，其实不找也行，用playwright装好的
USER_DIR_PATH = "C://Users/Blue_sky303/AppData/Local/Microsoft/Edge/User Data/Default"

# 找一下位置，加点目录
CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
CURRENT_DIR = CURRENT_DIR.replace("\\","/")
RESULTS_DIR = CURRENT_DIR + "/results"
if not os.path.exists(CURRENT_DIR+'/results'):
    os.mkdir(CURRENT_DIR+'/results')
if not os.path.exists(CURRENT_DIR+'/results/excel'):
    os.mkdir(CURRENT_DIR+'/results/excel')


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
        if begin_time or end_time:
            print_begin_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(begin_time))
            print_end_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(end_time))
            print(f"时间段{print_begin_time}-{print_end_time}-搜索{keyword}-第{page}页")
        else:
            print(f"搜索{keyword}-第{page}页")
        
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
                stoptime = 0
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
                        'date': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(video_data['pubdate'])),
                    }
                    return_dict.append(video_info)
                    
            elif response.status_code == 412: # 412码，大概是被封ip了，歇着或者换ip罢
                if not stoptime:
                    stoptime = time.asctime()
                print(f"412了, 哥们从{stoptime}歇到现在")
                time.sleep(300)
                page -= 1
            else:
                print(f'请求失败，状态码：{response.status_code}')
                break
            response.close()   
        except Exception as e:
            print('发生错误', e)
            break
        time.sleep(sleeptime)  # 控制请求频率
        page += 1
    print("爬取完成")
    return return_dict

# 数据写入excel
def write_excel(inputlist: list, filename = 'default.xlsx'): # 输入数据列表，格式与上面video_info相同
    # 数据预处理
    data = {'author': [], 'bvid': [], 'title': [], 'play': [], 'video_review': [], 'favorites': [], 'review': [], 'date': []}
    for video in inputlist:
        for key in video:
            data[key].append(video[key])
    data = pd.DataFrame(data)
    # 写入excel
    with pd.ExcelWriter(RESULTS_DIR+'/excel/'+filename, engine='openpyxl') as writer:
        data.to_excel(writer)

#写入多个工作表，输入字典，key为工作表名字
def sheets_write_excel(inputdict: dict, filename = 'default.xlsx'):
    with pd.ExcelWriter(RESULTS_DIR+'/excel/'+filename, engine='openpyxl') as writer:
        for name in inputdict:
            # 数据预处理
            data = {'author': [], 'bvid': [], 'title': [], 'play': [], 'video_review': [], 'favorites': [], 'review': [], 'date': []}
            for video in inputdict[name]:
                for key in video:
                    data[key].append(video[key])
            data = pd.DataFrame(data)
            # 写入excel
            data.to_excel(writer,sheet_name=name)
    
# 关键词列表搜索，合并关键词列表在同一时间段下的所有视频,开始时间和结束时间为时间戳
# 写入excel文件待用，名字用第一个关键词,工作表名用开始时间-结束时间，没有输入时间不用时间
def keyword_list_search(keyword_list: list, begin_time=0, end_time=0, maxpage = 50, sort_key = 'review', to_excel = True) -> list:
    result_list = []
    for keyword in keyword_list: 
        result_list += search_video_list(keyword, begin_time=begin_time, end_time=end_time, maxpage=maxpage)
    # 去重，以bvid作为特征
    bvlist = []
    for video in result_list:
        if video['bvid'] not in bvlist:
            bvlist.append(video['bvid'])
        else: 
            result_list.remove(video)
    # 排序，以评论数为key
    result_list = sorted(result_list, key = lambda x: x[sort_key], reverse=True)
    # 写入对应excel
    if to_excel:
        if not begin_time and not end_time:
            begin_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(begin_time))
            end_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(end_time))
            excel_file_name = f'{keyword_list[0]}-{begin_time} to {end_time}.xlsx'
        else:
            excel_file_name = f'{keyword_list[0]}.xlsx'
        write_excel(result_list, filename = excel_file_name)
    return result_list
    
# 时间列表搜索，其中时间列表每个元素是开始时间和结束时间的元组，
def time_list_search(keyword_list, time_list = [], maxpage = 50, sort_key = 'review'):
    result_dict = {'all':[]}
    for time_tuple in time_list:
        return_result = keyword_list_search(keyword_list, time_tuple[0], time_tuple[1], maxpage = maxpage, sort_key=sort_key, to_excel=False)
        begin_time = time.strftime("%Y%m%d.%H%M%S",time.localtime(time_tuple[0]))
        end_time = time.strftime("%Y%m%d.%H%M%S",time.localtime(time_tuple[1]))
        result_dict[f'{begin_time}-{end_time}'] = return_result
        result_dict['all'] += return_result
    # 总列表去重排序
    bvlist = []
    for video in result_dict['all']:
        if video['bvid'] not in bvlist:
            bvlist.append(video['bvid'])
        else: 
            result_dict['all'].remove(video)
    result_dict['all'] = sorted(result_dict['all'], key = lambda x: x[sort_key], reverse=True)
    # 写入excel
    sheets_write_excel(result_dict, filename=f'{keyword_list[0]}.xlsx')