# B站评论分析工具


一个简洁实用的桌面工具，通过关键词和时间范围搜索B站视频，分析多视频评论并生成词云图。

## 安装与运行

### Python环境运行
1. 确保安装 Python 3.9.10
2. 克隆仓库：
   ```bash
   git clone https://github.com/Bluesky303/BiliBili-Comments-Crawler.git
   cd BiliBili-Comments-Crawler
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 运行程序：
   ```bash
   python main.py
   ```
### Windows用户
1. 下载最新Release版本

2. 运行 BiliBiliCommentsCrawler.exe

### 或者自己打包
- 打包命令:
    ```bash
    pyinstaller main.spec
    ```

## 技术栈
- GUI框架: PyQt5

- B站API: 参考 [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)

- 网络请求: requests

- 文本分析: jieba 中文分词

- 可视化: wordcloud 词云生成

- 数据处理: pandas + openpyxl

## 许可证与协议
本项目其他部分采用 MIT 许可证，ui部分采用 GNU GPL v3 许可证。


## 免责声明
本工具仅用于学习交流和技术研究目的

使用本工具获取的数据不得用于任何商业用途

开发者不对使用本工具产生的任何后果负责

使用者应自行承担使用风险，不得滥用本工具