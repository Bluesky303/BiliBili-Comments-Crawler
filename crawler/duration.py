import time
import requests
import os
import pandas as pd

# 找一下位置，加点目录
CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
CURRENT_DIR = CURRENT_DIR.replace("\\","/")
RESULTS_DIR = CURRENT_DIR + "/results"


data = pd.read_excel(CURRENT_DIR + '/ai-筛选视频信息.xlsx', sheet_name=None)
names = data.keys()
duration = 0
for name in names:
    if not name == 'all':
        filename=f'{name}'
        bvlist = data[name].iloc[:, 2]
        stoptime = 0
        for i in range(len(bvlist)):
            bv = bvlist[i]
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
            }
            url = 'https://api.bilibili.com/x/web-interface/view'
            params = {
                'bvid': bv
            }
            print(f'try {name}: {bv}')
            try:
                response = requests.get(url, params, headers=headers, timeout=20)
                if response.status_code == 200:
                    data1 = response.json()
                    if 'data' in data1 and data1['code'] == 0:
                        d = data1['data']['duration']
                        duration += d
                        print(f'{bv}时长: {d//3600:0>2d}:{d%3600 //60:0>2d}:{d%60:0>2d}, 总时长: {duration//3600:0>2d}:{duration%3600 //60:0>2d}:{duration%60:0>2d}')
                    else: 
                        print('wdf no info')
                        i -= 1
                        input()
                else: 
                    print('寄')
                    time.sleep(300)
                    
                    input()
            except requests.RequestException as e:
                print(f"请求出错: {e}")
                break
            response.close()
            time.sleep(0.8)
print(f'完成, 总时长: {duration//3600:0>2d}:{duration%3600 //60:0>2d}:{duration%60:0>2d}')
