from crawler import time_list_allworks

from PyQt5.QtCore import QThread, pyqtSignal

import traceback

class Options:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class RequestThread(QThread):
    message = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.options = Options()
    def run(self):
        try:
            time_list_allworks(callback=self.message.emit, **self.options.__dict__)
        except Exception as e:
            print(traceback.format_exc())
            self.message.emit({'end': f'出现错误:{str(e)}'})
            
    def update(self,**kwargs):
        self.options.__dict__.update(kwargs)
        
        