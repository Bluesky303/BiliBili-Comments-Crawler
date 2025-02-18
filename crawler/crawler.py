import search, reviews, wordsCount
import pandas as pd
from .path import RESULTS_DIR

def allworks(time_list: list, keyword_list: list, cookies: str) -> None:
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


