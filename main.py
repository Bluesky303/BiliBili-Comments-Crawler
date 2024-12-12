from search import *
import pandas as pd
import reviews
#时间戳常数，16-24每半年一个
TIMEARRAY = [1451577600,1467302400,1483200000,1498838400,1514736000,1530374400,1546272000,1561910400,1577808000,1593532800,1609430400,1625068800,1640966400,1656604800,1672502400,1688140800,1704038400,1719763200,1735660800]
#搜索列表
SEARCHARRAY = ['懂王', '川普', '特朗普', '川建国']

#遍历时间列表和搜索列表
def list_search():
    all_list = []
    for timepoint in range(len(TIMEARRAY)-1):
        result_list = []
        for search in SEARCHARRAY: result_list += search_video_list(search, begin_time=TIMEARRAY[timepoint], end_time=TIMEARRAY[timepoint+1])
        
        #去重，以bvid作为特征
        bvlist = []
        for video in result_list:
            if not video['bvid'] in bvlist:
                result_list.remove(video)
                bvlist.append(video['bvid'])
                all_list.append(video)
        
        #排序，以播放量为key
        result_list = sorted(result_list, key = lambda x: x['review'], reverse=True)
        
        #写入对应csv
        write_csv(result_list, filename = f'{16+timepoint*0.5:.1f}.csv')
        
    all_list = sorted(all_list, key = lambda x: x['review'], reverse=True)
    write_csv(all_list, filename = 'all.csv')

#去重+写入excel
def write_excel():
    bvlist = []
    with pd.ExcelWriter('./new_project/result/all.xlsx',engine='openpyxl') as writer:
        for i in range(18):
            csv = pd.read_csv(f'./new_project/result/csv/{16.0+0.5* i}.csv',encoding="utf-8")
            for index,rows in csv.iterrows():
                if rows['bvid'] in bvlist:
                    csv.drop(index,inplace=True)
                else: bvlist.append(rows['bvid'])
                    
            csv.to_excel(writer, sheet_name=f'{16.0+0.5*i}')
        csv = pd.read_csv('./new_project/result/csv/all.csv')
        csv.to_excel(writer,sheet_name='all')

if __name__ == '__main__':
    '''主程序'''
    bvlist_file = './new_project/all.xlsx'
    for review_year in range(11,12):
        print(f'第{review_year*0.5+16}')
        data = pd.read_excel(bvlist_file, sheet_name = review_year, usecols= [2])
        comment_list = []
        with open('./new_project/cookies.txt', 'r') as r:
            cookies = r.read()
        r.close()
        #遍历bv列表
        for video_num in range(len(data['bvid'])): 
            comments = reviews.fetch_comments(data.iloc[video_num,0], cookies)
            for comment in comments:
                if TIMEARRAY[review_year] <= comment['time'] and comment['time'] <= TIMEARRAY[review_year+1]:#过滤评论时间
                    comment_list.append(reviews.purify(comment['content'])+'\n')
        #写入txt
        print(f'正在写入{16.0+0.5*review_year}.txt')
        with open(f'./new_project/result/txt/{16.0+0.5*review_year}.txt',mode = 'a+', encoding='utf-8') as f:
            f.write(f'{str(len(comment_list))}\n')
            f.writelines(comment_list)
        f.close()