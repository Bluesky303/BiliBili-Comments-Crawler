from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, QEvent, QModelIndex, QAbstractItemModel

from typing import Tuple

import re
from datetime import datetime

class TimeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(TimeDelegate, self).__init__(parent)
        self.timelist: list = []

    def eventFilter(self, editor: QLineEdit, event: QEvent):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return: # 回车键
            self.onEditorClosed(editor)
            return True
        elif event.type() == QEvent.FocusOut: # 失去焦点, 然而警示窗口的弹出会触发这个事件, 需要判断editor是不是在最前端
            if editor.isActiveWindow():
                self.onEditorClosed(editor)
            return True
        return super().eventFilter(editor, event)
    
    def onEditorClosed(self, editor: QLineEdit):
        text = editor.text()
        isvalid, error_message = self.validTime(text)
        if isvalid:
            self.commitData.emit(editor)
            self.closeEditor.emit(editor)
        else:
            QMessageBox.critical(editor, "日期错误", f"错误：{error_message}", QMessageBox.Ok)

    def validTime(self, text: str) -> Tuple[bool, str]:
        # 检查格式
        pattern = r'^(\d{4})/(\d{1,2})/(\d{1,2})-(\d{4})/(\d{1,2})/(\d{1,2})$'
        match = re.match(pattern, text)
        if not match:
            return False, "必须符合格式：YYYY/M/D-YYYY/M/D"
        
        # 检查日期存在
        begin_time, end_time = text.split('-')
        date_format = '%Y/%m/%d'
        try:
            begin_time = datetime.strptime(begin_time, date_format)
        except ValueError:
            return False, "开始日期无效"
        
        try:
            end_time = datetime.strptime(end_time, date_format)
        except ValueError:
            return False, "结束日期无效"
        
        # 日期先后
        if begin_time >= end_time:
            return False, "开始日期必须早于结束日期"
        
        return True, ""
            
        
            