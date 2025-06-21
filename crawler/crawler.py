from .search import time_list_search
from .reviews import fetch_comments, purify
from .wordsCount import save_words_to_all

import pandas as pd
import time

from .path import RESULTS_DIR

from typing import Dict, Callable


def time_list_allworks(keyword_list: list, 
                       cookies: str, 
                       time_list: list, 
                       callback: Callable[[Dict[str, str]], None] = print,
                       video_max_page: int = 1,
                       video_sort_key: str = 'review',
                       video_list_name: str = '',
                       comments_max_page: int = 99,
                       wordcloud_mask_pic_name: str = '1.png',
                       wordcloud_background_color: str = 'white',
                       wordcloud_width: int = 800,
                       wordcloud_height: int = 600,
                       wordcloud_if_show: bool = False,
                       ):
    if video_list_name == '':
        video_list_name = keyword_list[0]
    
    callback({'search': '正在准备开始搜索...'})
    time_list_search(keyword_list=keyword_list, 
                     time_list=time_list, 
                     callback=callback, 
                     maxpage=video_max_page, 
                     cookies=cookies, 
                     time_list_name=video_list_name,
                     sort_key=video_sort_key)
    callback({'fetch': '正在读取获取到的视频列表信息...'})
    data = pd.read_excel(RESULTS_DIR / f'video_list/{video_list_name}.xlsx', sheet_name=None)
    names = data.keys()
    time.sleep(0.5)
    for name in names:
        if not name == 'all':
            bvlist = data[name].iloc[:, 2]
            for num in range(len(bvlist)):
                callback({'fetch': f'正在获取{name}的第{num+1}/{len(bvlist)}个视频的评论...'})
                fetch_comments(bvlist[num], 
                               cookies=cookies, 
                               max_pages=comments_max_page, 
                               filename=video_list_name + ' ' + name, 
                               callback=callback)
            callback({'fetch_end': '获取评论结束'})
            callback({'words': '正在统计词频...'})
            save_words_to_all(file_name=video_list_name + ' ' + name, mask_pic_name=wordcloud_mask_pic_name, background_color=wordcloud_background_color, width=wordcloud_width, height=wordcloud_height, if_show=wordcloud_if_show)
            callback({'words_end': '统计词频结束'})
    callback({'end': '所有工作已完成'})



