import requests
import time
import pandas as pd

data = pd.read_excel("./Codes/1.xlsx", sheet_name="Sheet1")
bvlist = data.iloc[:, 2]
cookies = "SESSDATA=779d6160%2C1758799715%2C6db2e%2A32CjBPtZzrDj2TEzrY-9_Vm1x05PMHgU-Bvnyzqto2Qsb2_htELe2GxFOT04KvE88fqKwSVmpVOWNaTThhLURQcmFONEhRY1NIa0o0UXFkYUpzQnNzMncxb2tGMW1UWUNLT1o1VFVZbHZzS2NNVzVhUGJGdEp6angxUVhHTWtZRUs2cTdTU29fc1NRIIEC;"
    
def fetch_comments(video_bv, cookies, max_pages=2, sleeptime = 1):
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
                            '名字': comment['member']['uname'],
                            '内容': comment['content']['message'],
                            '等级': comment['member']['level_info']['current_level'],
                            '点赞数': comment['like'],
                            '时间': time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(comment['ctime']))
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


for num in range(len(bvlist)):
    print(f'{num+1}/{len(bvlist)}')
    sheetname = f'{num+1}'
    comments = fetch_comments(bvlist[num], cookies)
    with pd.ExcelWriter('./Codes/2.xlsx', engine='openpyxl', mode='a') as writer:
        df = pd.DataFrame(comments)
        df.to_excel(writer, sheet_name=sheetname, index=False)
    
    
