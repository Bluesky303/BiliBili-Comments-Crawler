from functools import partial
from PyQt5.QtGui import QPixmap

from .generateQR import generateQR, CheckQRThread

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui import MainWindow

# Cookies部分
def CookiesInit(MainWindow: 'MainWindow'):
    # 纯文本
    MainWindow.cookies = ""
    MainWindow.CookiesInput.textChanged.connect(CookiesInputChanged(MainWindow))
    MainWindow.RefreshButton.clicked.connect(RefreshButtonClicked(MainWindow))
    # 二维码
    QRCodeStart(MainWindow)

def CookiesInputChanged(MainWindow: 'MainWindow'):
    MainWindow.cookies = MainWindow.CookiesInput.toPlainText()
    MainWindow.updateTimeKeyword()
    
def QRCodeStart(MainWindow: 'MainWindow'):
    try:
        MainWindow.QRCodeKey = generateQR()
        QRCode = QPixmap("./QRCode.png")
        MainWindow.QRCode.setPixmap(QRCode)
        MainWindow.QRCodeThread = CheckQRThread(MainWindow.QRCodeKey)
        MainWindow.QRCodeThread.returnStatus.connect(partial(update_result, MainWindow))
        MainWindow.QRCodeThread.returnCookies.connect(partial(returnCookies, MainWindow))
        
        MainWindow.QRCodeThread.start()
    except Exception as e:
        MainWindow.QRCodeStatus.setText(f"error:{str(e)}")
        MainWindow.QRCodeThread = None
    

def update_result(MainWindow: 'MainWindow', message):
    MainWindow.QRCodeStatus.setText(message)
    if message == "代理错误":
        MainWindow.QRCode.setText("无法获取二维码状态")

def returnCookies(MainWindow: 'MainWindow', cookies):
    MainWindow.cookies = cookies
    MainWindow.CookiesInput.setPlainText(MainWindow.cookies)
    MainWindow.QRCodeThread.quit()
    MainWindow.QRCodeThread.wait()
    MainWindow.QRCodeThread = None
    
    QRCodeStart(MainWindow)

def RefreshButtonClicked(MainWindow: 'MainWindow'):
    if MainWindow.QRCodeThread is not None:
        MainWindow.QRCodeThread.terminate()
        MainWindow.QRCodeThread.wait()
        MainWindow.QRCodeThread = None
    QRCodeStart(MainWindow)
