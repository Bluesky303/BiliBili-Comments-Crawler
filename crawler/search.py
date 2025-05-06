"""获取视频列表"""
import time
import requests
import pandas as pd

from .path import RESULTS_DIR

from typing import List, Dict, Tuple, Callable, Optional


'''
from playwright.sync_api import *
# 找一个浏览器，我这里用edge，其实不找也行，用playwright装好的
USER_DIR_PATH = "C://Users/Blue_sky303/AppData/Local/Microsoft/Edge/User Data/Default"

def _setBiliBiliCookies(bv='BV1GJ411x7h7') -> str: 
    """获取cookies, 由于懒得自己复制所以写了这个函数
    需要在playwright打开的浏览器中默认登录才能用这个函数
    不过如果需要用户操作这个函数还是不用比较好
    ((自用

    Args:
        bv (str, optional): 选自己喜欢的视频

    Returns:
        str: cookies
    """
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
            # 转换格式，原格式是List[Cookie]
            runCookies = ""
            for data in cookies:
                if data['domain'] == '.bilibili.com': 
                    runCookies += data['name'] + "=" + data['value'] + "; " # 只要domain是bilibili.com全部拿出来就行应该
        cookies = runCookies
        return cookies
    except:
        return ''
'''

def search_video_list(keyword: str, 
                      begin_time: int = 0, end_time: int = 0, 
                      cookies: str = '',
                      maxpage: int = 50, 
                      order: str = 'click', 
                      sleeptime: float = 0.1, 
                      error_sleeptime: float = 300,
                      callback: Callable[[Dict[str, str]], None] = print) -> List[Dict]:
    """根据关键词和时间范围检索视频列表

    Args:
        keyword (str): 关键词
        begin_time (int, optional): 起始时间, 默认0就是不设置
        end_time (int, optional): 结束时间, 默认0就是不设置
        maxpage (int, optional): 最大页码, 默认50
        order (str, optional): 搜索排序, 默认播放量
            综合排序: totalrank
            最多点击: click
            最新发布: pubdate
            最多弹幕: dm
            最多收藏: stow
            最多评论: scores
            最多喜欢: attention(仅用于专栏)
        sleeptime (float, optional): 爬取间隔时间, 默认0.1秒
        error_sleeptime (float, optional): 错误重试间隔时间, 默认300秒
        callback (Callable[[Dict[str, str]], None], optional): 回调函数, 默认print

    Returns:
        List[Dict]: 视频列表
        单个视频内容: 
            author: 作者
            bvid: bv号
            title: 标题
            play: 播放量
            video_review: 弹幕数
            favorites: 收藏数
            review: 评论数
            date: 发布时间, 格式为"%Y-%m-%d %H:%M:%S"
    """
    return_dict = []
    page = 1
    stoptime = 0
    # 请求头
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47',
        'Cookie': cookies,
    }
    # 遍历页码，最大页码超出跳报错break
    while page<maxpage+1:
        if begin_time or end_time:
            callback({'search': f"时间段{begin_time}-{end_time}-搜索{keyword}-第{page}/{maxpage}页"})
        else:
            callback({'search': f"搜索{keyword}-第{page}/{maxpage}页"})
        
        # b站分类搜索api https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/search/search_request.md
        mainUrl = 'https://api.bilibili.com/x/web-interface/search/type'
        
        # api参数
        params = {
            'search_type': 'video',
            'keyword': keyword,
            'page': page,
            'order': order,
        }
        
        if begin_time and end_time: 
            params['pubtime_begin_s'] = int(time.mktime(time.strptime(begin_time, "%Y/%m/%d")))
            params['pubtime_end_s'] = int(time.mktime(time.strptime(end_time, "%Y/%m/%d")))
        
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
                print(response)
                for i in range(error_sleeptime):
                    time.sleep(1)
                    callback({'error': f"412了, 从{stoptime}歇到现在, {error_sleeptime-i}秒后继续"})
#                page -= 1
            else:
                callback({'error': f'请求失败，状态码：{response.status_code}'})
                break
            response.close()
        except Exception as e:
            callback({'error': f'发生错误, 错误信息: {e}'})
            break
        time.sleep(sleeptime)  # 控制请求频率
        page += 1
    callback({'search_end': f"搜索视频列表结束"})
    return return_dict

def write_excel(inputlist: List[Dict], filename: str = 'default.xlsx'):
    """将数据写入excel

    Args:
        inputlist (List[Dict]): 
        filename (str, optional): 文件名, 默认default.xlsx
    
    Results:
        产生一个excel文件, 内容为视频信息
    """
    # 数据预处理
    data = {'author': [], 'bvid': [], 'title': [], 'play': [], 'video_review': [], 'favorites': [], 'review': [], 'date': []}
    for video in inputlist:
        for key in video:
            data[key].append(video[key])
    data = pd.DataFrame(data)
    # 写入excel
    with pd.ExcelWriter(RESULTS_DIR / 'excel' / filename, engine='openpyxl') as writer:
        data.to_excel(writer)

def sheets_write_excel(inputdict: Dict[str, List[Dict]], filename: str = 'default.xlsx'):
    """写入多个工作表，输入字典，key为工作表名字

    Args:
        inputdict (Dict[str, List[Dict]]): 按照多个时间搜索时需要这个函数, 输入字典key为时间段, value为时间段对应视频列表
        filename (str, optional): 文件名, 默认default.xlsx
    
    Results:
        产生一个excel文件, 内容为多个工作表，每个工作表为对应时间段下的视频信息
    """
    with pd.ExcelWriter(RESULTS_DIR / 'excel' / filename, engine='openpyxl') as writer:
        for name in inputdict:
            # 数据预处理
            data = {'author': [], 'bvid': [], 'title': [], 'play': [], 'video_review': [], 'favorites': [], 'review': [], 'date': []}
            for video in inputdict[name]:
                for key in video:
                    data[key].append(video[key])
            data = pd.DataFrame(data)
            # 写入excel
            data.to_excel(writer,sheet_name=name)
    
def keyword_list_search(keyword_list: list, 
                        begin_time: Optional[str], 
                        end_time: Optional[str], 
                        cookies: str = '',
                        maxpage: int = 50, 
                        sort_key: str = 'review', 
                        to_excel: bool = True, 
                        callback: Callable[[Dict[str, str]], None] = print
                        ) -> List:
    """关键词列表搜索, 合并关键词列表在同一时间段下的所有视频, 写入excel文件待用

    Args:
        maxpage (int, optional): 搜索页面最大页码, 默认50
        sort_key (str, optional): 排序依据, 默认评论数
        to_excel (bool, optional): 是否写入excel, 默认True, 这里主要是给time_list_search留的, 笑死
        callback (Callable[[Dict[str, str]], None], optional): 回调函数, 默认print

    Returns:
        List[Dict]: 视频列表
    
    Results:
        产生一个excel文件, 内容为搜索到的视频信息, 文件名用第一个关键词, 工作表名用开始时间-结束时间, 没有输入时间不用时间
    """
    result_list = []
    for keyword in keyword_list:
        if not begin_time and not end_time:
            result_list += search_video_list(keyword, begin_time=begin_time, end_time=end_time, maxpage=maxpage, callback=callback, cookies=cookies)
        else:
            result_list += search_video_list(keyword, maxpage=maxpage, callback=callback, cookies=cookies)
    # 多个关键词会有重复视频，需要去重，以bvid作为特征
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
        if begin_time and end_time:
            excel_file_name = f'{keyword_list[0]}-{begin_time.replace("/", "-")} to {end_time.replace("/", "-")}.xlsx'
        else:
            excel_file_name = f'{keyword_list[0]}.xlsx'
        write_excel(result_list, filename = excel_file_name)
    return result_list
    
def time_list_search(keyword_list: List, 
                     time_list: List[Tuple[str, str]], 
                     cookies: str = '',
                     maxpage: int = 50, 
                     sort_key: str = 'review', 
                     callback: Callable[[Dict[str, str]], None] = print):
    """时间列表搜索, 合并关键词列表在对应时间段下的所有视频

    Args:
        keyword_list (List): 关键词列表
        time_list (List[Tuple[str, str]]): 时间列表, 每个元素是开始时间和结束时间的元组, 格式是"%Y/%m/%d"
        maxpage (int, optional): 最大页码, 默认50
        sort_key (str, optional): 排序依据, 默认评论数
        callback (Callable[[Dict[str, str]], None], optional): 回调函数, 默认print
        
    Results:
        产生一个excel文件, 名字为第一个关键词, 有多个工作表
        工作表名是 开始时间-结束时间 , 还有一个all工作表, 包含所有搜索到的视频
        每个工作表包含对应时间段下的视频信息
    """
    result_dict = {'all':[]}
    for (begin_time, end_time) in time_list:
        return_result = keyword_list_search(keyword_list, begin_time, end_time, maxpage = maxpage, sort_key=sort_key, to_excel=False, callback=callback, cookies=cookies)
        result_dict[f'{begin_time.replace("/", "-")}-{end_time.replace("/", "-")}'] = return_result
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