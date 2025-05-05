"""评论获取"""
import time, requests, re
import pandas as pd

from .path import RESULTS_DIR

from typing import List, Dict, Callable

def fetch_comments(video_bv: str, cookies: str, filename: str, max_pages: int = 100, sleeptime: int = 1, error_sleeptime: int = 300, callback: Callable[[Dict[str, str]], None] = print) -> List[Dict]:
    """获取单个视频评论
    412时会歇5分钟, 还没想好怎么处理这个
    Args:
        video_bv (str): 视频bv号
        cookies (str): cookies, 具体只需要SESSDATA字段
        max_pages (int, optional): 获取的评论页数, 默认101页
        sleeptime (int, optional): 爬取评论的间隔时间, 默认1秒
        callback (Callable[[Dict[str, str]], None], optional): 回调函数, 默认print

    Returns:
        list: 评论列表, 每个评论为一个字典, 包含name, content, sex, current level, likes, time字段
    """
    # 构造请求头
    headers = {
        'Cookie': cookies,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }
    
    file_path = RESULTS_DIR / 'excel' / (filename + '.xlsx')
    page = 1
    # 记录上轮获取评论数
    # 当评论页面数小于max_pages时，上轮评论数和本轮相同，因此可以结束
    # 这同样会导致其他错误时抛出报错然后结束
    last_count = 0
    stoptime = 0
    comments: Dict[str, List] = {'name': [], 'content': [], 'sex': [], 'current level': [], 'likes': [], 'time': []}
    while page <= max_pages+1:
        # b站评论api，参数可见https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/comment/list.md
        url = f'https://api.bilibili.com/x/v2/reply'
        params = {
            'type': 1, 
            'oid': video_bv,
            'pn': page,
            'sort': 1,
            'nohot': 1,
        }
        callback({'fetch1': f'正在爬取{video_bv}第{page}页'})
        try:
            response = requests.get(url,params=params, headers=headers, timeout=20)
            # 检查响应状态码是否为200，即成功
            if response.status_code == 200:
                data = response.json()
                stoptime = 0
                if data['data']['replies'] is None:
                    callback({'error': f'获取{video_bv}第{page}页失败，返回空，正在重试\n{data}'})
                    time.sleep(10)
                    page += 1
                    continue
                if data and 'replies' in data['data']:
                    for comment in data['data']['replies']: # 获取每一条评论信息
                        comment_info = {
                            'name': comment['member']['uname'],
                            'content': purify(comment['content']['message']),
                            'sex': comment['member']['sex'],
                            'current level': comment['member']['level_info']['current_level'],
                            'likes': comment['like'],
                            'time': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(comment['ctime'])),
                        }
                        for key in comments:
                            comments[key].append(comment_info[key])
                    
                if last_count == len(comments['name']): # 说明到底了
                    break
                last_count = len(comments['name'])
            elif response.status_code == 412: # 412码歇着
                if not stoptime:
                    stoptime = time.asctime()
                for i in range(error_sleeptime):
                    time.sleep(1)
                    callback({'error': f"412了, 从{stoptime}歇到现在, {error_sleeptime-i}秒后继续"})
                page -= 1
            
        except requests.RequestException as e:
            callback({'error': f'请求失败，状态码：{response.status_code}'})
            break
        response.close()
        # 暂存
        if not file_path.exists():
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                pd.DataFrame(comments).to_excel(writer, sheet_name=video_bv, index=False)
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                pd.DataFrame(comments).to_excel(writer, sheet_name=video_bv, index=False)
        page += 1
        time.sleep(sleeptime)  # 控制请求频率
    callback({'fetch1_end': f'获取{video_bv}评论结束'})

def purify(content: str) -> str:
    """去除评论中的表情文本，以免影响分词和词云图结果
    后果是所有[]中括号以及里面的都被删了，包括正常评论内容
    建立表情列表可能可以解决，但是b站表情列表会更新可能导致新表情无法去除
    不过中括号频率不高，所以不会有太大影响
    以及非贪婪匹配会导致多层中括号剩余右半括号
    例如: [[123]] -> ]
    不过也很少见就是了
    之前使用了类似栈的方法不过好像也没写对
    总之这样应该最好了
    Args:
        content (str): 评论内容

    Returns:
        str: 去除中括号及其内容后的评论内容
    """
    return re.sub(r'\[.*?\]', '', content)
