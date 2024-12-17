import search
import reviews
import wordsCount
import os
import pandas as pd

# 找一下位置，加点目录
CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
CURRENT_DIR = CURRENT_DIR.replace("\\","/")
RESULTS_DIR = CURRENT_DIR + "/results"

time_list = [(1451577600,1467302400),(1467302400,1483200000)]
keyword_list = ['川普','特朗普']
cookies = ""

if __name__ == '__main__':
    '''执行所有操作'''
    search.time_list_search(keyword_list=keyword_list, time_list=time_list)
    data = pd.read_excel(RESULTS_DIR + f'/excel/{keyword_list[0]}.xlsx', sheet_name=None)
    names = data.keys()
    for name in names:
        if not name == 'all':
            filename=f'{keyword_list[0]}-{name}'
            bvlist = data[name].iloc[:, 2]
            comments = []
            for num in range(len(bvlist)):
                print(f'{name}-{num+1}/{len(bvlist)}')
                comments += reviews.fetch_comments(bvlist[num], cookies=cookies, max_pages=2)
            contents = []
            for comment in comments:
                contents.append(reviews.purify(comment['content']))
            reviews.write_txt(contents, filename=filename+'.txt')
            wordsCount.save_words_to_all(file_name=filename)