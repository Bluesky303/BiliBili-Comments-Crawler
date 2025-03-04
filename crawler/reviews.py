'''评论获取'''
import time
import requests
import os

from .path import RESULTS_DIR

# 爬取评论
def fetch_comments(video_bv, cookies, max_pages=100, sleeptime = 1):
    # 构造请求头
    headers = {
        'Cookie': cookies,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }
    comments = []
    page = 1
    last_count = 0
    stoptime = 0
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
                stoptime = 0
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
                if last_count == len(comments): # 说明到底了
                    break
                last_count = len(comments)
            elif response.status_code == 412: # 412码歇着
                if not stoptime:
                    stoptime = time.asctime()
                print(f"412了, 哥们从{stoptime}歇到现在")
                time.sleep(300)
                page -= 1
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            break
        response.close()
        page += 1
        time.sleep(sleeptime)  # 控制请求频率
    print('爬取完成')
    return comments

# 去除评论中的表情文本，以免影响分词和词云图结果
# 后果是所有[]中括号以及里面的都被删了，建立表情列表可能可以解决
def purify(comment):    
    return_comment = ''
    open_braket_stack = []
    current_pos = 0
    delete_count = 0
    while current_pos < len(comment):
        #记录所有左中括号位置
        if comment[current_pos] == '[':
            open_braket_stack.append(current_pos-delete_count)
        #遇到右中括号删去到上一个左中括号之间的内容并记录区间长度
        elif comment[current_pos] == ']' and open_braket_stack != []:
            return_comment = return_comment[:open_braket_stack[-1]]
            delete_count = current_pos-open_braket_stack[-1]+1
            open_braket_stack.pop()
        #啥都不是直接加进来
        if comment[current_pos] != ']':
            return_comment += comment[current_pos]
        current_pos += 1
    return return_comment

def write_txt(comments, filename='default.txt'):
    with open(RESULTS_DIR+'/txt/'+filename, 'w', encoding='utf-8') as w:
        w.write(str(len(comments))+'\n')
        w.writelines(comments)
        w.close()