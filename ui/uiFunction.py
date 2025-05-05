from PyQt5.QtWidgets import QMainWindow, QAbstractItemView
from PyQt5.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from .main_ui import Ui_MainWindow
from .generateQR import generateQR, CheckQRThread
from .delegate import TimeDelegate
from .startrequest import RequestThread

from typing import List, Dict, Tuple, Callable

#设置运行图标
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.QRCodeThread = None
        
        self.initUI()
        
    def initUI(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowTitle("B站评论获取")
        
        self.setWindowIcon(QIcon('./icon.ico'))
        
        self.CookiesInit()
        self.TimeKeywordInit()
        
        self.StartButton.clicked.connect(self.StartButtonClicked)

    # Cookies部分
    def CookiesInit(self):
        # 纯文本
        self.cookies = ""
        self.CookiesInput.textChanged.connect(self.CookiesInputChanged)
        self.RefreshButton.clicked.connect(self.RefreshButtonClicked)
        # 二维码
        self.QRCodeStart()
    
    def CookiesInputChanged(self):
        self.cookies = self.CookiesInput.toPlainText()
        self.updateTimeKeyword()
    
    def QRCodeStart(self):
        try:
            self.QRCodeKey = generateQR()
        except Exception as e:
            self.QRCodeStatus.setText(f"error:{str(e)}")
        QRCode = QPixmap("./QRCode.png")
        self.QRCode.setPixmap(QRCode)
        self.QRCodeThread = CheckQRThread(self.QRCodeKey)
        self.QRCodeThread.returnStatus.connect(self.update_result)
        self.QRCodeThread.returnCookies.connect(self.returnCookies)
        
        self.QRCodeThread.start()
    
    def update_result(self, message):
        self.QRCodeStatus.setText(message)
    
    def returnCookies(self, cookies):
        self.cookies = cookies
        self.CookiesInput.setPlainText(self.cookies)
        self.QRCodeThread.quit()
        self.QRCodeThread.wait()
        self.QRCodeThread = None
        
        self.QRCodeStart()

    def hasCookies(self):
        return self.cookies != ""
    
    def RefreshButtonClicked(self):
        self.QRCodeThread.terminate()
        self.QRCodeThread.wait()
        self.QRCodeThread = None
        self.QRCodeStart()
    
    # 时间关键词部分
    def TimeKeywordInit(self):
        self.timeModel = QStandardItemModel()
        self.Time.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.Time.setItemDelegate(TimeDelegate()) # 检测时间格式
        self.Time.setModel(self.timeModel)
        self.TimeNew.clicked.connect(self.TimeNewClicked)
        self.TimeDelete.clicked.connect(self.TimeDeleteClicked)
        
        self.keywordModel = QStandardItemModel()
        self.Keywords.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.Keywords.setModel(self.keywordModel)
        self.KeywordNew.clicked.connect(self.KeywordNewClicked)
        self.KeywordDelete.clicked.connect(self.KeywordDeleteClicked)
        
        self.requestThread = RequestThread()
        self.requestThread.message.connect(self.receive_message)
        
        self.updateTimeKeyword()
    
    def TimeNewClicked(self):
        default_time = "2020/1/1-2021/1/1"
        row = QStandardItem(default_time)
        self.timeModel.appendRow(row)
        self.Time.scrollToBottom()
        self.updateTimeKeyword()
        
    def TimeDeleteClicked(self):
        indexes = self.Time.selectedIndexes()
        for index in reversed(indexes):
            self.timeModel.removeRow(index.row())
        self.updateTimeKeyword()
    
    def KeywordNewClicked(self):
        default_keyword = "关键词"
        row = QStandardItem(default_keyword)
        self.keywordModel.appendRow(row)
        self.Keywords.scrollToBottom()
        self.updateTimeKeyword()
        
    def KeywordDeleteClicked(self):
        indexes = self.Keywords.selectedIndexes()
        for index in reversed(indexes):
            self.keywordModel.removeRow(index.row())
        self.updateTimeKeyword()
        
    def updateTimeKeyword(self):
        self.time = [item.text().split("-") for item in self.timeModel.findItems("", Qt.MatchContains)]
        self.keyword = [item.text() for item in self.keywordModel.findItems("", Qt.MatchContains)]
        self.requestThread.update(self.time, self.keyword, self.cookies)
    
    # 运行部分
    def StartButtonClicked(self):
        self.log: Dict[str, str] = {}
        if not self.hasCookies():
            self.LogPrinter.setText("请先填写Cookies")
            return
        if self.time == [] or self.keyword == []:
            self.LogPrinter.setText("请先填写时间和关键词")
            return
        self.StartButton.setEnabled(False)
        self.requestThread.start()

    def receive_message(self, message: Dict[str, str]):
        for key in message:
            self.log[key] = message[key]
            if key[:-4] in self.log:
                del self.log[key[:-4]]
            self.log_show()
            if key + '_end' in self.log:
                del self.log[key + '_end']
                
            if key != 'error' and 'error' in self.log:
                del self.log['error']
        if 'end' in self.log:
            self.StartButton.setEnabled(True)
            self.requestThread.quit()
            self.requestThread.wait()
            
    def log_show(self):
        s = ""
        for key, value in self.log.items():
            if key == 'error':
                continue
            s += f"{value}\n"
        s += self.log['error'] if 'error' in self.log else ""
        self.LogPrinter.setText(s)