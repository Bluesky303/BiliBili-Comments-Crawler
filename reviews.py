'''评论获取'''
import time
import search
import requests
import random

def fetch_comments(video_bv, cookies, max_pages=100):
    '''爬取评论'''
    # 构造请求头
    headers = {
        'Cookie': cookies,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    }
    comments = []
    page = 1
    last_count = 0
    last_page = 0
    last_cookies = headers['Cookie']
    while page <= max_pages+1:
        # b站评论api
        url = f'https://api.bilibili.com/x/v2/reply'
        params = {
            'type': 1,
            'oid': video_bv,
            'pn': page,
            'sort': 1,
            'nohot': 1,
            
        }
        print(f'正在爬取{video_bv}第{page}页')
        try:
            response = requests.get(url,params=params, headers=headers, timeout=20)
            # 检查响应状态码是否为200，即成功
            if response.status_code == 200:
                data = response.json()
                
                if data['data']['replies'] is None:
                    page -= 1
                elif data and 'replies' in data['data']:
                    for comment in data['data']['replies']:
                        comment_info = {
                            'name': comment['member']['uname'],
                            'content': comment['content']['message'],
                            'sex': comment['member']['sex'],
                            'current level': comment['member']['level_info']['current_level'],
                            'likes': comment['like'],
                            'time': comment['ctime']
                        }
                        comments.append(comment_info)
                if last_count == len(comments):
                    break
                last_count = len(comments)
            elif response.status_code == 412:#412码更换
                headers['Cookie'] = search._setCookies(bv= video_bv)
                
                print('reset Cookies')
                page -= 1
                if(page == last_page):
                    if headers['Cookie'] == last_cookies:
                        time.sleep(10)
                        last_cookies = headers['Cookie']
                    time.sleep(random.uniform(1,5))
                last_page = page
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            break
        response.close()
        page += 1
        time.sleep(1)  #控制请求频率
    print('爬取完成')
    return comments

def purify(comment):
    """去除评论中的表情文本，以免影响分词和词云图结果"""
    s = ''
    stack = []
    i = 0
    cnt = 0
    while i < len(comment):
        if comment[i] == '[':
            stack.append(i-cnt)
        elif comment[i] == ']' and stack != []:
            s = s[:stack[-1]]
            cnt += i-cnt-stack[-1]+1
            stack.pop()
        if comment[i] != ']':
            s += comment[i]
        i += 1
    return s