import qrcode, requests, time, re, traceback
from PyQt5.QtCore import QThread, pyqtSignal

from crawler import CURRENT_PATH

from PIL import Image

def generateQR() -> str:
    applyurl = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }
    data = requests.get(applyurl, headers=headers)
    if data.status_code == 200:
        data = data.json()["data"]
        qrcodeurl = data["url"]
        qrcodekey = data["qrcode_key"]
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qrcodeurl)
        qr.make(fit=True)
        img: Image.Image = qr.make_image(fill_color="black", back_color="white")
        img = img.convert("RGBA")
        img = img.resize((100, 100))
        img.save(CURRENT_PATH / "QRCode.png")
    else: 
        raise Exception("获取二维码失败")
    return qrcodekey

class CheckQRThread(QThread):
    returnStatus = pyqtSignal(str)
    returnCookies = pyqtSignal(str)
    def __init__(self, qrcodekey: str, parent = None):
        super(CheckQRThread, self).__init__(parent)
        self.parent = parent
        self.qrcodekey = qrcodekey
        
    def run(self):
        loginurl = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
        }
        while True:
            try: 
                data = requests.get(loginurl, headers=headers, params={"qrcode_key": self.qrcodekey})
                # 检测状态码
                if not data.status_code == 200:
                    self.returnStatus.emit(f"error:{data.status_code}")
                    continue
                data = data.json()
                # 检测返回码
                if data["code"] != 0:
                    self.returnStatus.emit(data["message"])
                    continue
                # 检测登录状态
                if data["data"]["code"] != 0:
                    self.returnStatus.emit(data["data"]["message"])
                    continue
                # 登录成功
                self.returnStatus.emit(data["data"]["message"])
                url = data["data"]["url"]
                cookies = re.search(r"SESSDATA=[^&]*", url).group()
                self.returnCookies.emit(cookies)
                
                break     
            except requests.exceptions.ProxyError:
                self.returnStatus.emit("代理错误")
                self.quit()       
            except Exception as e:
                self.returnStatus.emit(f"error:{e}")
            time.sleep(0.5)

