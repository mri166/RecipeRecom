import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, \
    QGridLayout, QSizePolicy, QSpacerItem, QFormLayout, QLineEdit,QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPalette, QColor, QFont, QBrush, QPixmap, QIcon
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import subprocess

class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super(CameraWidget, self).__init__(parent)
        self.image_label = QLabel()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def display_frame(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        q_img = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.image_label.setPixmap(pixmap)


class CameraWindow(QWidget):
    def __init__(self):
        super(CameraWindow, self).__init__()
        self.setWindowTitle('识别系统')
        self.setWindowIcon(QIcon('icon.png'))  # 设置窗口图标
        self.setGeometry(100, 100, 640, 480)

        # 设置背景图片
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap('./background.jpeg')))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.camera_widget = CameraWidget(self)
        layout = QVBoxLayout()

        spacer = QSpacerItem(20, 45, QSizePolicy.Minimum, QSizePolicy.Maximum)
        layout.addItem(spacer)

        # 添加标题
        self.title_label = QLabel('健康饮食推荐系统')
        self.title_label.setFont(QFont('幼圆', 45, QFont.Bold))
        self.title_label.setStyleSheet("color: white;")
        self.title_label.setAlignment(Qt.AlignCenter)

        # 添加一个 QSpacerItem 用于调整标题位置

        layout.addWidget(self.title_label)

        # 添加用户名和密码输入框
        form_layout = QFormLayout()
        spacer = QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Maximum)
        layout.addItem(spacer)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        self.username_input.setStyleSheet("""
               QLineEdit {
                   border: 2px solid #8f8f91;
                   border-radius: 10px;
                   padding: 5px 5px;
                   background-color: #f0f0f0;
                   font-size: 13px;
               }
               QLineEdit:focus {
                   border: 2px solid #0078d7;
                   background-color: #e0f7ff;
               }
           """)
        self.username_input.setFixedSize(150, 40)  # width, height
        self.username_label = QLabel("用户名:")
        self.username_label.setStyleSheet("""
            QLabel {
                font-size: 20px; /* 标签文本字体大小 */
                font-family: 微软雅黑; /* 标签文本字体 */
                color: black; /* 标签文本颜色 */
                padding: 5px; /* 标签内边距 */
            }
        """)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
                      QLineEdit {
                          border: 2px solid #8f8f91;
                          border-radius: 10px;
                          padding: 5px 5px;
                          background-color: #f0f0f0;
                          font-size: 13px;
                      }
                      QLineEdit:focus {
                          border: 2px solid #0078d7;
                          background-color: #e0f7ff;
                      }
                  """)
        self.password_input.setFixedSize(150, 40)  # width, height

        # 添加行到表单布局
        form_layout.addRow(self.username_label, self.username_input)

        self.password_label = QLabel(" 密码:")
        self.password_label.setStyleSheet("""
                  QLabel {
                      font-size: 20px; /* 标签文本字体大小 */
                      font-family: 微软雅黑; /* 标签文本字体 */
                      color: black; /* 标签文本颜色 */
                      padding: 5px; /* 标签内边距 */
                  }
              """)
        form_layout.addRow(self.password_label, self.password_input)

        # 创建一个水平布局，并将表单布局添加到其中
        hbox_layout = QHBoxLayout()
        hbox_layout.addStretch(1)
        hbox_layout.addLayout(form_layout)
        hbox_layout.addStretch(1)

        # 将水平布局添加到主布局中
        layout.addLayout(hbox_layout)

        layout.addWidget(self.camera_widget)

        self.start_button = QPushButton('登录', self)
        self.start_button.setFixedSize(150, 50)
        self.start_button.setStyleSheet("""
            QPushButton{
                background: orange;
                color: white;
                box-shadow: 1px 1px 3px;
                font-size: 18px;
                border-radius: 24px;
                font-family: 微软雅黑;
            }
            QPushButton:pressed{
                background: black;
            }
        """)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        self.health_button = QPushButton('注册', self)
        self.health_button.setFixedSize(150, 50)
        self.health_button.setStyleSheet("""
            QPushButton{
                background: orange;
                color: white;
                box-shadow: 1px 1px 3px;
                font-size: 18px;
                border-radius: 24px;
                font-family: 微软雅黑;
            }
            QPushButton:pressed{
                background: black;
            }
        """)
        layout.addWidget(self.health_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Connect the start button to the get_credentials method
        self.start_button.clicked.connect(self.get_credentials)

    def get_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()
        print(f"Username: {username}, Password: {password}")
        if(username=='taster' and password=='123456'):
            QMessageBox.warning(self, '登陆成功', '正在跳转系统界面')
            self.close()
            subprocess.run(["python", "ui.py"])
        elif (username == '' and password == ''):
            QMessageBox.warning(self, '错误', '用户名不能为空')
        else:
            QMessageBox.warning(self, '密码错误', '密码错误')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())
