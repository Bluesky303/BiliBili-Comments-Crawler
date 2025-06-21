from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from .main_ui import Ui_MainWindow
from .generateQR import generateQR, CheckQRThread
from .delegate import TimeDelegate
from .startrequest import RequestThread
from crawler.path import RESULTS_DIR, CURRENT_PATH

import pathlib
from functools import partial

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
        self.windowIcon = QIcon('./icon.ico')
        self.setupUi(self)
        self.retranslateUi(self) 
        self.setWindowTitle("B站评论获取")
        
        self.setWindowIcon(QIcon('./icon.ico'))
        
        self.OptionInit()
        self.CookiesInit()
        self.TimeKeywordInit()
        self.MenuInit()
        
        self.StartButtonInit()

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
        self.updateOptions()
    
    def QRCodeStart(self):
        try:
            self.QRCodeKey = generateQR()
            QRCode = QPixmap("./QRCode.png")
            self.QRCode.setPixmap(QRCode)
            self.QRCodeThread = CheckQRThread(self.QRCodeKey)
            self.QRCodeThread.returnStatus.connect(self.update_result)
            self.QRCodeThread.returnCookies.connect(self.returnCookies)
            
            self.QRCodeThread.start()
        except Exception as e:
            self.QRCodeStatus.setText(f"error:{str(e)}")
            self.QRCodeThread = None
    
    def update_result(self, message):
        self.QRCodeStatus.setText(message)
        if message == "代理错误":
            self.QRCode.setText("无法获取二维码状态")
    
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
        if self.QRCodeThread is not None:
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
        self.timeModel.dataChanged.connect(self.updateOptions)
        
        self.keywordModel = QStandardItemModel()
        self.Keywords.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.Keywords.setModel(self.keywordModel)
        self.KeywordNew.clicked.connect(self.KeywordNewClicked)
        self.KeywordDelete.clicked.connect(self.KeywordDeleteClicked)
        self.keywordModel.dataChanged.connect(self.updateOptions)
        
        self.requestThread = RequestThread()
        self.requestThread.message.connect(self.receive_message)
        
        self.updateOptions()
    
    def TimeNewClicked(self):
        default_time = "2020/1/1-2021/1/1"
        row = QStandardItem(default_time)
        self.timeModel.appendRow(row)
        self.Time.scrollToBottom()
        self.updateOptions()
        
    def TimeDeleteClicked(self):
        indexes = self.Time.selectedIndexes()
        for index in reversed(indexes):
            self.timeModel.removeRow(index.row())
        self.updateOptions()
    
    def KeywordNewClicked(self):
        default_keyword = "关键词"
        row = QStandardItem(default_keyword)
        self.keywordModel.appendRow(row)
        self.Keywords.scrollToBottom()
        self.updateOptions()
        
    def KeywordDeleteClicked(self):
        indexes = self.Keywords.selectedIndexes()
        for index in reversed(indexes):
            self.keywordModel.removeRow(index.row())
        self.updateOptions()
        
    def updateOptions(self):
        self.time = [item.text().split("-") for item in self.timeModel.findItems("", Qt.MatchContains)]
        self.keyword = [item.text() for item in self.keywordModel.findItems("", Qt.MatchContains)]
        self.videolistmaxpage = int(self.VideoListMaxpage.text())
        self.videolistsortkey = self.VideoListSortkey.currentText()
        self.videolistname = self.VideoListName.text()
        self.commentsmaxpage = int(self.CommentsMaxpage.text())
        self.wordcloudmaskpicname = self.WordcloudMaskpicName.text()
        self.wordcloudwidth = int(self.WordcloudWidth.text())
        self.wordcloudheight = int(self.WordcloudHeight.text())
        self.wordcloudifshow = self.WordcloudIfshow.isChecked()
        self.requestThread.update(time_list = self.time, 
                                  keyword_list = self.keyword, 
                                  cookies = self.cookies, 
                                  video_max_page = self.videolistmaxpage, 
                                  video_sort_key = self.videolistsortkey,
                                  video_list_name = self.videolistname,
                                  comments_max_page = self.commentsmaxpage-1,
                                  wordcloud_mask_pic_name = self.wordcloudmaskpicname,
                                  wordcloud_width = self.wordcloudwidth,
                                  wordcloud_height = self.wordcloudheight,
                                  wordcloud_if_show = self.wordcloudifshow
                                  )
    
    # 选项部分
    def OptionInit(self):
        self.VideoListMaxpage.editingFinished.connect(self.VideoListMaxpageChanged)
        self.videoListMaxpage = 50
        
        self.VideoListSortkey.currentIndexChanged.connect(self.updateOptions)
        self.videoListSortkey = 'scores'
        
        self.VideoListName.textChanged.connect(self.updateOptions)
        self.videolistname = ''
        
        self.CommentsMaxpage.editingFinished.connect(self.CommentsMaxpageChanged)
        self.commentsmaxpage = 100
        
        self.WordcloudMaskpicName.textChanged.connect(self.WordcloudMaskpicNameChanged)
        self.wordcloudmaskpicname = '1.png'

        self.WordcloudWidth.editingFinished.connect(self.WordcloudWidthChanged)
        self.wordcloudwidth = 800
        
        self.WordcloudHeight.editingFinished.connect(self.WordcloudHeightChanged)
        self.wordcloudheight = 600
        
        self.WordcloudIfshow.stateChanged.connect(self.updateOptions)
        self.wordcloudifshow = False
        
        
    def VideoListMaxpageChanged(self):
        if not self.VideoListMaxpage.text().isdigit():
            self.VideoListMaxpage.setText("50")
            QMessageBox.critical(self, "错误", "最大页数必须为数字")
        else:
            self.updateOptions()
    
    def CommentsMaxpageChanged(self):
        if not self.CommentsMaxpage.text().isdigit():
            self.CommentsMaxpage.setText("100")
            QMessageBox.critical(self, "错误", "最大页数必须为数字")
        else:
            self.updateOptions()
    
    def WordcloudMaskpicNameChanged(self):
        if not pathlib.Path(self.WordcloudMaskpicName.text()).exists() or not pathlib.Path(self.WordcloudMaskpicName.text()).suffix == '.png':
            self.WordcloudMaskpicName.setText("1.png")
            QMessageBox.critical(self, "错误", "请选择正确的图片")
        else:
            self.updateOptions()
    
    def WordcloudWidthChanged(self):
        if not self.WordcloudWidth.text().isdigit():
            self.WordcloudWidth.setText("800")
            QMessageBox.critical(self, "错误", "宽度必须为数字")
        else:
            self.updateOptions()
    
    def WordcloudHeightChanged(self):
        if not self.WordcloudHeight.text().isdigit():
            self.WordcloudHeight.setText("600")
            QMessageBox.critical(self, "错误", "高度必须为数字")
        else:
            self.updateOptions()
            
    
    # 运行部分
    def StartButtonInit(self):
        self.StartButton.clicked.connect(self.StartButtonClicked)
            
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
        
    # 菜单部分
    def MenuInit(self):
        self.actionMain_Page.triggered.connect(partial(self.stackedWidget.setCurrentIndex, 0))
        self.actionOption.triggered.connect(partial(self.stackedWidget.setCurrentIndex, 1))
