import os
# 找一下位置，加点目录
CURRENT_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_PATH)
CURRENT_DIR = CURRENT_DIR.replace("\\","/")
RESULTS_DIR = CURRENT_DIR + "/results"

path_list = ["", "/txt", "/excel", "/json", "/words-count-txt", "/wordcloud"]
path_list = [RESULTS_DIR + path for path in path_list]
for path in path_list:
    if not os.path.exists(path):
        os.mkdir(path)
