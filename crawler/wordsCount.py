"""数据处理部分，分词，统计词频和词性，制作词云图"""
import jieba
import json
import jieba.posseg as pseg
import numpy as np
import pandas as pd
import wordcloud
from PIL import Image

from .path import RESULTS_DIR

import pathlib
from typing import List, Tuple, Dict

def words_count(excel_name: str, excel_path: pathlib.Path = RESULTS_DIR / "excel") -> List[Tuple[str, Tuple[int, str]], ]:
    """读取整个评论excel文件, 分词并统计词频和词性 (所有sheet, 即多个视频整合)
    停用词不被统计, 可以在./resources/stopwords.txt中添加


    Returns:
        (List[Tuple[str, Tuple[int, str]]]): 词频统计结果, 是元组列表, 每个元组为(词, (词频, 词性)), 有利于排序
    """
    # 加载停用词，这些词不会被统计
    stopwords = open(RESULTS_DIR.parent / 'resources/stopwords.txt', 'r', encoding='utf-8').read()
    stopwords_list = list(stopwords.split("\n"))
    
    data = pd.read_excel(excel_path / excel_name, sheet_name=None)
    bvs = data.keys()
    words_dict = {}
    
    for bv in bvs:
        comments = data[bv]['content']
        # 遍历评论
        for comment in comments:
            if not pd.notna(comment):
                continue
            count = jieba.lcut(comment) # 切分
            # 遍历切分
            for word in count:
                # 单字和停用词不记录
                if len(word) == 1 or word in stopwords_list:
                    continue
                # 词性切分，能进一步切分标记为un
                formercut = pseg.cut(word)
                formercut = {word: flag for word, flag in formercut}
                if word in formercut:
                    words_dict[word] = [words_dict.get(word, [0])[0] + 1, words_dict.get(word, [0, formercut[word]])[1]]
                else:
                    words_dict[word] = [words_dict.get(word, [0])[0] + 1, 'un']
    words_list = list(words_dict.items())
    words_list.sort(key=lambda x: x[1][0], reverse=True)  # 按词频排序
    return words_list

# 保存词频统计结果到./results/words_count.json，用于后续处理
def save_words_count_to_json(words_list: list, 
                             words_count_json_name: str = "default_words_count.json", 
                             json_path: pathlib.Path = RESULTS_DIR / "json"
                             ):
    """保存词频统计结果到./results/words_count.json, 用于后续处理
    
    """
    json.dump(dict(words_list), open(json_path / words_count_json_name, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

# 生成词云图
def generate_wordcloud(words_dict: Dict[str, Tuple[int, str]],
                       wordcloud_name: str = "wordcloud.png",
                       wordcloud_path: pathlib.Path = RESULTS_DIR / 'wordcloud',
                       mask_pic_path: pathlib.Path = RESULTS_DIR.parent / "resources/mask_pic",
                       mask_pic_name: str = '1.png',
                       background_color: str = 'white',
                       width: int = 800,
                       height: int = 600,
                       font_name: str = 'simfang.ttf', 
                       font_path: pathlib.Path = RESULTS_DIR.parent / 'resources/font', 
                       if_show: bool = False, 
                       ):
    """生成词云图

    Args:
        words_count_json (str): 词频统计结果json文件名
        mask_pic_name (str, optional): 蒙版图片名, 默认1.png, 修改这个可以改词云图样式
    """
    # 预处理
    for word in words_dict:
        words_dict[word] = words_dict[word][0] # 转化成 词语, 词频 对
    w = wordcloud.WordCloud(background_color=background_color,
                            width=width,
                            height=height,
                            font_path=font_path / font_name,
                            mask=np.array(Image.open(mask_pic_path / mask_pic_name)),
                            scale=20).fit_words(words_dict)
    # 词云图生成结果展示
    img = w.to_image()
    if if_show:
        img.show()
    # 保存词云图生成结果
    w.to_file(wordcloud_path / wordcloud_name)

# 更新统计数据实现部分词性的删除
def handle(file_name, del_list = ['c', 'm', 'u', 'b', 'e', 'p', 'q', 'o', 's', 'l', 'j']) -> Dict[str, Tuple[int, str]]:
    """部分词性词汇不会展示在词云图中, 以后可能会写单个词汇的删除

    Args:
        del_list (list, optional): 筛选词性列表

    Returns:
        Dict[str, Tuple[int, str]]: 筛选后的词频统计结果, 里面的Tuple实际是List(因为json的load就这样, 但是List不能标注两个类型)
    """
    words_count = json.load(open(RESULTS_DIR / "json" / (file_name + '_words_count.json'), "r", encoding="utf-8"))
    del_word_list = []
    # 记录具有对应词性的待删除单词
    for word in words_count:
        if words_count[word][1] in del_list:
            del_word_list.append(word)
            continue
    # 删除
    for del_word in del_word_list:
        del words_count[del_word]
    return words_count

# 完成以上操作(丝滑小连招
def save_words_to_all(file_name='default'):
    word_list = words_count(file_name+'.xlsx')
    save_words_count_to_json(word_list, file_name+'_words_count.json')
    wordscount = handle(file_name)
    generate_wordcloud(wordscount, wordcloud_name = file_name+'_wordcloud.png')
