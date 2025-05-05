from crawler import time_list_allworks

from PyQt5.QtCore import QThread, pyqtSignal

import traceback

class RequestThread(QThread):
    message = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            time_list_allworks(keyword_list=self.keyword_list, cookies=self.cookies, time_list=self.time_list, callback=self.message.emit)
        except Exception as e:
            print(traceback.format_exc())
            
    def update(self, time_list: list, keyword_list: list, cookies: str):
        self.time_list = time_list
        self.keyword_list = keyword_list
        self.cookies = cookies