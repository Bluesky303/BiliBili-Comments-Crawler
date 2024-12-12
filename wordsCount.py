"""数据处理部分，分词，统计词频和词性"""
import jieba
import json
import jieba.posseg as pseg
import numpy as np
import wordcloud
from PIL import Image, ImageTk
def words_count(txt_name, txt_path="./new_project/result/txt/"):
    """统计词频"""
    s = open(txt_path+txt_name+'.txt', 'r', encoding='utf-8').read()
    rp_str = '： ， ；、？——‘’（）#！\n '
    for i in rp_str:
        s = s.replace(i, '')
        s = ''.join(s.split())
    jieba.load_userdict(txt_path+txt_name+'.txt')
    words = jieba.lcut(s)
    stopwords = open('./new_project/stopwords/stopwords.txt', 'r', encoding='utf-8').read()
    stopwords_list = list(stopwords.split("\n"))  # 去除停用词
    words_dict = {}
    for i in words:
        if len(i) == 1:
            continue
        if i not in stopwords_list:
            words_dict[i] = words_dict.get(i, 0) + 1  # 统计词频
    words_list = list(words_dict.items())
    words_list.sort(key=lambda x: x[1], reverse=True)  # 排序
    return words_list


def save_words_count_to_json(words_list, json_name="words_count.json", json_path="./new_project/result/json/"):
    """保存词频统计结果到./res/result/words_count.json，作为生成词云图的参数"""
    with open(json_path+json_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dict(words_list), indent=4))
    f.close()


def save_words_to_json(words_json_name="words.json", words_count_json_name="words_count.json", json_path="./new_project/result/json/"):
    """统计词性，保存进一步的处理结果到./new_project/result/json/words.json，以便筛选"""
    with open(json_path+words_count_json_name, 'r', encoding='utf-8') as f:
        words = dict(json.load(f))
    f.close()
    for k, v in words.items():
        word_cut = pseg.cut(k)
        for word, flag in word_cut:
            if word == k:
                words[k] = [str(v), flag]
                break
        else:
            words[k] = [str(v), "un"]
    with open(json_path+words_json_name, 'w', encoding='utf-8') as f:
        json.dump(words, f, indent=4)
    f.close()

def generate_wordcloud(words_dict,
                       wordcloud_name="wordcloud.png",
                       wordcloud_path='./new_project/result/wordcloud/',
                       mask_pic_path="./new_project/mask_pic/",
                       mask_pic_name='1.png',
                       background_color='white',
                       width=800,
                       height=600,
                       font_path='./new_project/font/simfang.ttf'):
    """生成词云图"""
    w = wordcloud.WordCloud(background_color=background_color,
                            width=width,
                            height=height,
                            font_path=font_path,
                            mask=np.array(Image.open(mask_pic_path + mask_pic_name)),
                            scale=20).fit_words(words_dict)
    # 词云图生成结果展示
    img = w.to_image()
    img.show()
    # 保存词云图生成结果
    w.to_file(wordcloud_path + wordcloud_name)
    
def handle(file_name):
    """更新统计数据实现删除"""
    with open("./new_project/result/json/"+file_name+'_words.json', "r", encoding="utf-8") as f:
        words = dict(json.load(f))
    f.close()
    with open("./new_project/result/json/"+file_name+'_words_count.json', "r", encoding="utf-8") as f:
        words_count = dict(json.load(f))
    f.close()
    del_list = ['c', 'm', 'u', 'b', 'e', 'p', 'q', 'o', 's', 'l', 'j']
    del_word_list = []
    for word in words:
        if words[word][1] in del_list:
            del_word_list.append(word)
            continue
    for del_word in del_word_list:
        del words_count[del_word]
        del words[del_word]
    return words_count, words

for i in range(9,10):
    file_name = f'{i*0.5+16.0}'
    word_list = words_count(file_name)
    save_words_count_to_json(word_list, file_name+'_words_count.json')
    save_words_to_json(file_name+'_words.json', file_name+'_words_count.json')
    words_dict, words = handle(file_name)
    with open('./new_project/result/wordscounttxt/'+file_name+'_words_count.txt', "w", encoding='utf-8') as f:
        for word in words_dict:
            f.write(f'{word}:{words[word][0]}, {words[word][1]}\n')
    generate_wordcloud(words_dict, wordcloud_name=file_name+'_wordcloud.png')
