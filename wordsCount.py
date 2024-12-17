"""数据处理部分，分词，统计词频和词性"""
import jieba
import json
import jieba.posseg as pseg
import numpy as np
import wordcloud
import os
from PIL import Image

# 找一下位置，建一点目录
CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
CURRENT_DIR = CURRENT_DIR.replace("\\","/")
RESULTS_DIR = CURRENT_DIR + "/results"
if not os.path.exists(CURRENT_DIR+'/results/json'):
    os.mkdir(CURRENT_DIR+'/results/json')
if not os.path.exists(CURRENT_DIR+'/results/words-count-txt'):
    os.mkdir(CURRENT_DIR+'/results/words-count-txt')
if not os.path.exists(CURRENT_DIR+'/results/wordcloud'):
    os.mkdir(CURRENT_DIR+'/results/wordcloud')

# 统计词频
def words_count(txt_name='default.txt', txt_path = RESULTS_DIR+"/txt/") -> list:
    s = open(txt_path+txt_name, 'r', encoding='utf-8').read()
    # 结巴分词，分词表见./resources/stopwords
    jieba.load_userdict(txt_path+txt_name)
    allwords = jieba.lcut(s)
    # 加载停用词用于删除，不统计这些词
    stopwords = open(CURRENT_DIR+'/resources/stopwords/stopwords.txt', 'r', encoding='utf-8').read()
    stopwords_list = list(stopwords.split("\n"))  
    words_dict = {}
    for word in allwords:
        if len(word) == 1:
            continue
        if word not in stopwords_list: 
            words_dict[word] = words_dict.get(word, 0) + 1  # 记录词频
    words_list = list(words_dict.items())
    words_list.sort(key=lambda x: x[1], reverse=True)  # 排序
    return words_list # 返回词汇-词频元组的列表

# 保存词频统计结果到./results/words_count.json，用于后续处理
def save_words_count_to_json(words_list: list, words_count_json_name="default_words_count.json", json_path=RESULTS_DIR+"/json/"):
    print("write into "+words_count_json_name)
    with open(json_path+words_count_json_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dict(words_list), indent=4))
    f.close()

# 保存到txt方便查看词语内容
def save_words_count_to_txt(words_dict, file_name="default_words_count.txt"):
    with open(RESULTS_DIR + '/words-count-txt/'+file_name, "w", encoding='utf-8') as f:
        for word in words_dict:
            f.write(f'{word}:{words_dict[word][0]}, {words_dict[word][1]}\n')

# 统计词性，保存到./results/json/words_class.json，以便筛选
def save_words_class_to_json(words_class_json_name="default_words_class.json", words_count_json_name="default_words_count.json", json_path=RESULTS_DIR + "/json/"):
    with open(json_path+words_count_json_name, 'r', encoding='utf-8') as f:
        words = dict(json.load(f))
    f.close()
    
    for word_uncut, count in words.items():
        word_cut = pseg.cut(word_uncut)
        for word, word_class in word_cut:
            if word == word_uncut:
                words[word] = [str(count), word_class]
                break
        else:
            words[word_uncut] = [str(count), "un"] # 如果能被进一步切分则标注为unkown类型
    with open(json_path+words_class_json_name, 'w', encoding='utf-8') as f:
        json.dump(words, f, indent=4)
    f.close()

# 生成词云图
def generate_wordcloud(words_dict,
                       wordcloud_name="wordcloud.png",
                       wordcloud_path=RESULTS_DIR + '/wordcloud/',
                       mask_pic_path=CURRENT_DIR + "/resources/mask_pic/",
                       mask_pic_name='1.png',
                       background_color='white',
                       width=800,
                       height=600,
                       font_name='simfang.ttf', 
                       font_path=CURRENT_DIR + '/resources/font/'):
    print("generate " + wordcloud_name)
    w = wordcloud.WordCloud(background_color=background_color,
                            width=width,
                            height=height,
                            font_path=font_path + font_name,
                            mask=np.array(Image.open(mask_pic_path + mask_pic_name)),
                            scale=20).fit_words(words_dict)
    # 词云图生成结果展示
    img = w.to_image()
    img.show()
    # 保存词云图生成结果
    w.to_file(wordcloud_path + wordcloud_name)

# 更新统计数据实现部分词性的删除
def handle(file_name, del_list = ['c', 'm', 'u', 'b', 'e', 'p', 'q', 'o', 's', 'l', 'j']):
    with open(RESULTS_DIR + "/json/"+file_name+'_words_class.json', "r", encoding="utf-8") as f:
        words_class = dict(json.load(f))
    f.close()
    with open(RESULTS_DIR + "/json/"+file_name+'_words_count.json', "r", encoding="utf-8") as f:
        words_count = dict(json.load(f))
    f.close()
    del_word_list = []
    # 记录具有对应词性的待删除单词
    for word in words_class:
        if words_class[word][1] in del_list:
            del_word_list.append(word)
            continue
    # 删除
    for del_word in del_word_list:
        del words_count[del_word]
        del words_class[del_word]
    return words_count, words_class

# 完成以上操作(丝滑小连招
def save_words_to_all(file_name='default'):
    word_list = words_count(txt_name=file_name+'.txt')
    save_words_count_to_json(word_list, file_name+'_words_count.json')
    save_words_class_to_json(file_name+'_words_class.json', file_name+'_words_count.json')
    words_dict, words_class = handle(file_name)
    save_words_count_to_txt(words_class, file_name = file_name+"_words_count.txt")
    generate_wordcloud(words_dict, wordcloud_name = file_name+'_wordcloud.png')
