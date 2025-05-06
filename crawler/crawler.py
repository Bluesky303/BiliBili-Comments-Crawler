from .search import time_list_search
from .reviews import fetch_comments, purify
from .wordsCount import save_words_to_all

import pandas as pd
import time

from .path import RESULTS_DIR

from typing import Dict, Callable

def time_list_allworks(keyword_list: list, cookies: str, time_list: list, callback: Callable[[Dict[str, str]], None] = print):
    callback({'search': '正在准备开始搜索...'})
    time_list_search(keyword_list=keyword_list, time_list=time_list, callback=callback, maxpage=1, cookies=cookies)
    callback({'fetch': '正在读取获取到的视频列表信息...'})
    data = pd.read_excel(RESULTS_DIR / f'excel/{keyword_list[0]}.xlsx', sheet_name=None)
    names = data.keys()
    time.sleep(5)
    for name in names:
        if not name == 'all':
            bvlist = data[name].iloc[:, 2]
            for num in range(len(bvlist)):
                callback({'fetch': f'正在获取{name}的第{num+1}/{len(bvlist)}个视频的评论...'})
                fetch_comments(bvlist[num], cookies=cookies, max_pages=0, filename=name, callback=callback)
            callback({'fetch_end': '获取评论结束'})
            callback({'words': '正在统计词频...'})
            save_words_to_all(file_name=name)
            callback({'words_end': '统计词频结束'})
    callback({'end': '所有工作已完成'})



