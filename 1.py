import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenu, QAction,
    QStackedWidget, QWidget, QVBoxLayout, QLabel
)
from PyQt5.QtCore import Qt
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QMenu页面切换示例")
        self.setGeometry(100, 100, 600, 400)
        
        # 初始化堆叠页面容器
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 添加三个示例页面
        self.add_page("页面1", "background-color: #FFCCCB;")  # 浅红色
        self.add_page("页面2", "background-color: #90EE90;")  # 浅绿色
        self.add_page("页面3", "background-color: #87CEEB;")  # 浅蓝色
        
        # 默认显示第一个页面
        self.stacked_widget.setCurrentIndex(0)
        
        # 创建菜单系
        self.create_menus()
    
    def add_page(self, title: str, style_sheet: str):
        """动态添加页面到堆叠容器"""
        page = QWidget()
        page.setStyleSheet(style_sheet)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(title, alignment=Qt.AlignCenter))
        page.setLayout(layout)
        self.stacked_widget.addWidget(page)
    
    def create_menus(self):
        """构建菜单栏和切换动作"""
        menu_bar = self.menuBar()
        
        # 创建页面切换菜单
        switch_menu = menu_bar.addMenu("导航(&N)")
        
        # 添加切换动作
        self.add_menu_action(switch_menu, "首页", 0)
        self.add_menu_action(switch_menu, "数据看板", 1)
        self.add_menu_action(switch_menu, "设置中心", 2)
        
        # 可选：添加分隔线和其他菜单项
        switch_menu.addSeparator()
        exit_action = QAction("退出(&X)", self)
        exit_action.triggered.connect(self.close)
        switch_menu.addAction(exit_action)
    
    def add_menu_action(self, menu: QMenu, text: str, index: int):
        """为菜单添加带切换功能的动作"""
        action = QAction(text, self)
        action.triggered.connect(lambda: self.switch_page(index))
        menu.addAction(action)
    
    def switch_page(self, index: int):
        """执行页面切换并验证有效性"""
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
        else:
            print(f"警告：无效的页面索引 {index}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())