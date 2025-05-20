"""内容保存的目录"""

import pathlib
import sys

# 获取目录位置
CURRENT_PATH = pathlib.Path(__file__).parent # 之后调整为自选目录
RESULTS_DIR = CURRENT_PATH / "results"
# 如果是打包后的目录
if getattr(sys, 'frozen', False):
    CURRENT_PATH = pathlib.Path(sys._MEIPASS)
    RESULTS_DIR = pathlib.Path(sys.executable).parent/"results"
    



# 创建子目录
path_list = ["txt", "excel", "json", "wordcloud"]
path_list = [RESULTS_DIR / path for path in path_list]
for path in path_list:
    path.mkdir(parents=True, exist_ok=True)