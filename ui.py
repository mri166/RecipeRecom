from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QStackedWidget, \
    QHBoxLayout, QDialog, QScrollArea,QTextEdit,QLineEdit
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
import gc
import os
from py2neo import Graph
import subprocess
import sys
from PyQt5.QtCore import QDateTime, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPalette, QPixmap, QColor, QFont,QBrush, QPalette, QPixmap, QIcon
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sqlite3

matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号
class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Loading')
        self.setFixedSize(300, 100)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        # 设置米色背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 220))  # 米色
        self.setPalette(palette)

        layout = QVBoxLayout()
        self.label = QLabel('请稍候...')
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def closeEvent(self, event):
        # 在关闭对话框时显式调用垃圾回收
        gc.collect()
        super().closeEvent(event)

class ObjectDetectionThread(QThread):
    finished = pyqtSignal()

    def run(self):
        subprocess.run(["python", "object_detection.py"])
        self.finished.emit()

    def __del__(self):
        self.wait()

class DetailView(QWidget):
    def __init__(self, object_name):
        super().__init__()

        self.setWindowTitle('营养含量')
        self.setFixedSize(320, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        # 设置米色背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))  # 米色
        self.setPalette(palette)

        layout = QVBoxLayout()

        # 标签
        chinese_name = MainWindow.translate_to_chinese(object_name)
        text_label = QLabel(chinese_name)
        font = QFont()
        font.setFamily("幼圆")  # 设置字体
        font.setPointSize(20)  # 设置字体大小
        text_label.setFont(font)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)

        # 图片
        image_label = QLabel()
        pixmap = QPixmap(f"./nutrient content/{object_name}.png")
        target_size = QSize(300, 600)  # 设置目标大小
        pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)


        # 返回按钮
        back_button = QPushButton('返回')
        back_button.clicked.connect(self.close)
        layout.addWidget(back_button, alignment=Qt.AlignBottom)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initDB()

        # 设置米色背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 220))  # 米色

        self.setPalette(palette)

        self.setWindowTitle('推荐系统')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建按钮布局
        self.button_layout = QHBoxLayout()

        self.btn1 = QPushButton('我的食材')
        self.btn1.setFixedSize(150, 50)
        self.btn1.setStyleSheet("""
                    QPushButton{
                        background: #FFCC99;
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
        self.btn1.clicked.connect(self.check_file_and_update_label)
        self.btn2 = QPushButton('饮食推荐')
        self.btn2.setFixedSize(150, 50)
        self.btn2.setStyleSheet("""
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
        self.btn2.clicked.connect(self.recommendation)
        self.btn3 = QPushButton('健康管理')
        self.btn3.setFixedSize(150, 50)
        self.btn3.setStyleSheet("""
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

        self.button_layout.addWidget(self.btn1)
        self.button_layout.addWidget(self.btn2)
        self.button_layout.addWidget(self.btn3)

        self.button_widget = QWidget()
        self.button_widget.setLayout(self.button_layout)

        # 创建 QStackedWidget 并添加子界面
        self.stacked_widget = QStackedWidget()

        # 界面1：我的冰箱
        self.page1 = QWidget()
        self.page1_layout = QVBoxLayout()

        # 在这里定义标签
        self.page1_result_label = QLabel('')
        font = QFont('幼圆', 16, QFont.Bold)
        self.page1_result_label.setFont(font)

        self.page1_result_label.setAlignment(Qt.AlignLeft)
        self.page1_result_label.setStyleSheet('color: green')

        # 创建一个 QScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # 创建一个 QWidget 作为 QScrollArea 的内容
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        # 将标签添加到滚动区域的布局中
        self.scroll_layout.addWidget(self.page1_result_label)

        # 将滚动内容设置为 QScrollArea 的小部件
        self.scroll_area.setWidget(self.scroll_content)

        # 将 QScrollArea 添加到 page1 的布局中
        self.page1_layout.addWidget(self.scroll_area)

        # 添加食物按钮
        self.addFoodButton = QPushButton()
        self.addFoodButton.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                text-align: center;
            }
            QPushButton::icon {
                padding-bottom: 5px;  /* 调整文字和图标的距离 */
            }
            QPushButton:pressed{
                        background: black;
                    }
            """
        )
        buttonIcon = QIcon("./addPic.png")
        self.addFoodButton.setIcon(buttonIcon)
        self.addFoodButton.setIconSize(QSize(70, 70))
        self.addFoodButton.setStyleSheet("background: transparent;")
        self.addFoodButton.clicked.connect(self.start_detection)
        self.page1_layout.addWidget(self.addFoodButton, alignment=Qt.AlignBottom)

        self.page1.setLayout(self.page1_layout)

        # 界面2：饮食推荐
        self.page2 = QWidget()
        self.page2_layout = QVBoxLayout()
        #self.page2_label = QLabel('这是界面 2')
        #self.page2_layout.addWidget(self.page2_label)

        # 创建一个 QScrollArea
        self.scroll_area2 = QScrollArea()
        self.scroll_area2.setWidgetResizable(True)

        # 创建一个 QWidget 作为 QScrollArea 的内容
        self.scroll_content2 = QWidget()
        self.scroll_layout2 = QVBoxLayout(self.scroll_content2)

        # 将标签添加到滚动区域的布局中
        #self.scroll_layout.addWidget(self.page2_result_label)

        # 将滚动内容设置为 QScrollArea 的小部件
        self.scroll_area2.setWidget(self.scroll_content2)

        # 将 QScrollArea 添加到 page2 的布局中
        self.page2_layout.addWidget(self.scroll_area2)
        self.page2.setLayout(self.page2_layout)

        # 界面3：健康管理
        self.page3 = QWidget()
        self.page3_layout = QVBoxLayout()

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 220))  # 米色
        self.setPalette(palette)

        # 设置窗口的标题和尺寸
        self.setWindowTitle('健康数据记录')
        self.setGeometry(300, 300, 800, 700)

        # 身高和体重输入框布局
        height_and_weight_layout = QHBoxLayout()

        self.height_label = QLabel('身高 (cm):', self)
        self.height_label.setFont(QFont('微软雅黑', 10, QFont.Bold))
        height_and_weight_layout.addWidget(self.height_label)

        self.height_input = QLineEdit(self)
        self.height_input.setStyleSheet("""
                                           border:2px solid rgb(186,186,186);
                                           border-radius:10px
                                       """)
        height_and_weight_layout.addWidget(self.height_input)

        self.weight_label = QLabel('体重 (kg):', self)
        self.weight_label.setFont(QFont('微软雅黑', 10, QFont.Bold))
        height_and_weight_layout.addWidget(self.weight_label)

        self.weight_input = QLineEdit(self)
        self.weight_input.setStyleSheet("""
                                           border:2px solid rgb(186,186,186);
                                           border-radius:10px
                                       """)
        height_and_weight_layout.addWidget(self.weight_input)

        self.page3_layout.addLayout(height_and_weight_layout)

        # 血压输入框布局
        blood_press_layout = QHBoxLayout()

        self.sbp_label = QLabel('收缩压 (mmHg):', self)
        self.sbp_label.setFont(QFont('微软雅黑', 10, QFont.Bold))
        blood_press_layout.addWidget(self.sbp_label)

        self.sbp_input = QLineEdit(self)
        self.sbp_input.setStyleSheet("""
                                           border:2px solid rgb(186,186,186);
                                           border-radius:10px
                                       """)
        blood_press_layout.addWidget(self.sbp_input)

        self.dbp_label = QLabel('舒张压 (mmHg):', self)
        self.dbp_label.setFont(QFont('微软雅黑', 10, QFont.Bold))
        blood_press_layout.addWidget(self.dbp_label)

        self.dbp_input = QLineEdit(self)
        self.dbp_input.setStyleSheet("""
                                           border:2px solid rgb(186,186,186);
                                           border-radius:10px
                                       """)
        blood_press_layout.addWidget(self.dbp_input)

        self.page3_layout.addLayout(blood_press_layout)

        # 血糖输入框布局
        blood_sugar_layout = QHBoxLayout()

        self.bs_label = QLabel('血糖 (mg/dL):', self)
        self.bs_label.setFont(QFont('微软雅黑', 10, QFont.Bold))
        blood_sugar_layout.addWidget(self.bs_label)

        self.bs_input = QLineEdit(self)
        self.bs_input.setStyleSheet("""
                                           border:2px solid rgb(186,186,186);
                                           border-radius:10px
                                       """)
        blood_sugar_layout.addWidget(self.bs_input)

        self.page3_layout.addLayout(blood_sugar_layout)

        # 保存和清空按钮布局
        button_layout = QHBoxLayout()

        self.save_button = QPushButton('保存信息', self)
        self.save_button.clicked.connect(self.save_data)
        self.save_button.setFixedSize(100, 50)
        self.save_button.setStyleSheet("""
                                   QPushButton{
                                       background: blue;
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
        button_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.clear_button = QPushButton('清空数据', self)
        self.clear_button.clicked.connect(self.clear_data)
        self.clear_button.setFixedSize(100, 50)
        self.clear_button.setStyleSheet("""
                                           QPushButton{
                                               background: red;
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
        button_layout.addWidget(self.clear_button, alignment=Qt.AlignCenter)

        self.page3_layout.addLayout(button_layout)

        # 收缩压和舒张压的图表布局
        h_layout = QHBoxLayout()

        self.canvas_sbp = FigureCanvas(Figure(figsize=(5, 3)))
        h_layout.addWidget(self.canvas_sbp)

        self.canvas_dbp = FigureCanvas(Figure(figsize=(5, 3)))
        h_layout.addWidget(self.canvas_dbp)

        self.page3_layout.addLayout(h_layout)

        # 血糖图表布局
        self.canvas_bs = FigureCanvas(Figure(figsize=(5, 3)))
        self.page3_layout.addWidget(self.canvas_bs)

        self.page3.setLayout(self.page3_layout)
        self.load_initial_data()
        self.conn = sqlite3.connect('health_data.db')
        self.cursor = self.conn.cursor()

        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.addWidget(self.page2)
        self.stacked_widget.addWidget(self.page3)

        # 创建主布局并添加按钮和堆栈窗口
        self.main_layout = QVBoxLayout()
        self.top_layout = QVBoxLayout()
        self.top_layout.addWidget(self.button_widget)
        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.stacked_widget)

        self.central_widget.setLayout(self.main_layout)

        # 连接按钮点击信号到槽函数
        self.btn1.clicked.connect(lambda: self.change_page(self.page1, self.btn1))
        self.btn2.clicked.connect(lambda: self.change_page(self.page2, self.btn2))
        self.btn3.clicked.connect(lambda: self.change_page(self.page3, self.btn3))

        # 初始化按钮样式
        self.update_button_styles(self.btn1)

        # 调用文件检查方法
        self.check_file_and_update_label()
        self.recommendation()

    def initDB(self):
        self.conn = sqlite3.connect('health_data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
              CREATE TABLE IF NOT EXISTS health_data (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  blood_pressure_systolic TEXT,
                  blood_pressure_diastolic TEXT,
                  blood_sugar TEXT,
                  height TEXT,
                  weight TEXT
              )
          ''')
        self.cursor.execute('''
              CREATE TABLE IF NOT EXISTS user_info (
                  id INTEGER PRIMARY KEY,
                  height TEXT,
                  weight TEXT
              )
          ''')
        self.conn.commit()

    def load_initial_data(self):
        self.cursor.execute('SELECT height, weight FROM user_info WHERE id = 1')
        result = self.cursor.fetchone()
        if result:
            height, weight = result
            self.height_input.setText(height)
            self.weight_input.setText(weight)
        self.plot_health_data()

    def save_data(self):
        try:
            current_date = QDateTime.currentDateTime().toString('MM-dd HH:mm')

            blood_pressure_systolic = self.sbp_input.text()
            blood_pressure_diastolic = self.dbp_input.text()
            blood_sugar = self.bs_input.text()
            height = self.height_input.text()
            weight = self.weight_input.text()

            if not blood_pressure_systolic or not blood_pressure_diastolic or not blood_sugar:
                QMessageBox.warning(self, '输入错误', '需要输入血压血糖数据')
                return

            if not height or not weight:
                QMessageBox.warning(self, '输入错误', '需要输入身高体重')
                return

            # 保存健康数据到数据库
            self.cursor.execute('''
                  INSERT INTO health_data (date, blood_pressure_systolic, blood_pressure_diastolic, blood_sugar, height, weight)
                  VALUES (?, ?, ?, ?, ?, ?)
              ''', (current_date, blood_pressure_systolic, blood_pressure_diastolic, blood_sugar, height, weight))
            self.conn.commit()

            # 更新用户信息表
            self.cursor.execute('SELECT COUNT(*) FROM user_info WHERE id = 1')
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute('''
                      INSERT INTO user_info (id, height, weight)
                      VALUES (1, ?, ?)
                  ''', (height, weight))
            else:
                self.cursor.execute('''
                      UPDATE user_info
                      SET height = ?, weight = ?
                      WHERE id = 1
                  ''', (height, weight))
            self.conn.commit()

            QMessageBox.information(self, '成功', '健康数据保存成功')

            # 重新绘制推荐内容
            self.recommendation()
            self.plot_health_data()
            # 清空输入框内容
            self.sbp_input.clear()
            self.dbp_input.clear()
            self.bs_input.clear()

        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存健康数据时发生错误：{str(e)}')

    def clear_data(self):
        conn = sqlite3.connect('health_data.db')
        cursor = conn.cursor()

        cursor.execute('DELETE FROM health_data')
        conn.commit()

        cursor.execute('DELETE FROM user_info')
        conn.commit()

        cursor.execute('VACUUM')
        conn.commit()

        QMessageBox.information(self, '成功', '数据清空成功！')

        # 重新绘制推荐内容
        self.recommendation()
        self.height_input.clear()
        self.weight_input.clear()
        self.sbp_input.clear()
        self.dbp_input.clear()
        self.bs_input.clear()
        self.plot_health_data()


    def plot_health_data(self):
        # 查询健康数据
        self.cursor.execute(
            'SELECT date, blood_pressure_systolic, blood_pressure_diastolic, blood_sugar FROM health_data ORDER BY date')
        data = self.cursor.fetchall()

        dates = []
        sbp_values = []
        dbp_values = []
        bs_values = []

        for row in data:
            dates.append(row[0])
            sbp_values.append(float(row[1]))
            dbp_values.append(float(row[2]))
            bs_values.append(float(row[3]))

        # 绘制收缩压折线图
        fig_sbp = self.canvas_sbp.figure
        fig_sbp.clear()
        ax_sbp = fig_sbp.add_subplot(111)
        ax_sbp.plot(dates, sbp_values, marker='o', linestyle='-', color='b')
        ax_sbp.set_title('收缩压')
        ax_sbp.set_xlabel('日期')
        ax_sbp.set_ylabel('血压值 (mmHg)')
        fig_sbp.set_facecolor('none')  # Set transparent background
        fig_sbp.autofmt_xdate()
        self.canvas_sbp.draw()

        # 绘制舒张压折线图
        fig_dbp = self.canvas_dbp.figure
        fig_dbp.clear()
        ax_dbp = fig_dbp.add_subplot(111)
        ax_dbp.plot(dates, dbp_values, marker='o', linestyle='-', color='b')
        ax_dbp.set_title('舒张压')
        ax_dbp.set_xlabel('日期')
        ax_dbp.set_ylabel('血压值 (mmHg)')
        fig_dbp.set_facecolor('none')  # Set transparent background
        fig_dbp.autofmt_xdate()
        self.canvas_dbp.draw()

        # 绘制血糖折线图
        fig_bs = self.canvas_bs.figure
        fig_bs.clear()
        ax_bs = fig_bs.add_subplot(111)
        ax_bs.plot(dates, bs_values, marker='o', linestyle='-', color='r')
        ax_bs.set_title('血糖')
        ax_bs.set_xlabel('日期')
        ax_bs.set_ylabel('血糖值 (mg/dL)')
        fig_bs.set_facecolor('none')  # Set transparent background
        fig_bs.autofmt_xdate()
        self.canvas_bs.draw()

    def closeEvent(self, event):
        # 关闭数据库连接
        self.conn.close()
        event.accept()
    def change_page(self, page, button):
        self.stacked_widget.setCurrentWidget(page)
        self.update_button_styles(button)

    def health_condition(self):
        self.cursor.execute('''
            SELECT blood_pressure_systolic, blood_pressure_diastolic, blood_sugar, weight 
            FROM health_data ORDER BY id DESC LIMIT 1
        ''')
        latest_health_data = self.cursor.fetchone()

        if latest_health_data is None:
            print("没有找到健康数据")
            return 0, 0, 0

        blood_pressure_systolic, blood_pressure_diastolic, blood_sugar, weight = latest_health_data
        flag1, flag2, flag3 = 0, 0, 0

        if float(blood_pressure_systolic) >= 140 or float(blood_pressure_diastolic) >= 90:
            flag1 = 1  # 高血压
        elif float(blood_pressure_systolic) < 140 and float(blood_pressure_diastolic) < 90:
            flag1 = 0

        if float(blood_sugar) >= 126:
            flag2 = 1  # 糖尿病
        elif float(blood_sugar) < 126:
            flag2 = 0

        if float(weight) >= 100:
            flag3 = 1  # 肥胖
        elif float(weight) < 100:
            flag3 = 0

        print(flag1, flag2, flag3)
        return flag1, flag2, flag3

    def update_button_styles(self, active_button):
        buttons = [self.btn1, self.btn2, self.btn3]
        for button in buttons:
            if button == active_button:
                button.setStyleSheet("""
                                   QPushButton{
                                       background: #FFCC99;
                                       color: white;
                                       box-shadow: 1px 1px 3px;
                                       font-size: 18px;
                                       border-radius: 24px;
                                       font-family: 黑体;
                                       font-weight
                                   bold;
                                   }
                                   QPushButton:pressed{
                                       background: black;
                                   }
                               """)
            else:
                button.setStyleSheet("""
                                   QPushButton{
                                       background: lightgray;
                                       color: white;
                                       box-shadow: 1px 1px 3px;
                                       font-size: 18px;
                                       border-radius: 24px;
                                       font-family: 黑体;
                                       font-weight: bold;
                                   }
                                   QPushButton:pressed{
                                       background: black;
                                   }
                               """)

    @staticmethod
    def translate_to_chinese(english_name):
        # 这里我们用一个字典来进行翻译，你可以根据需要扩展这个字典
        translations = {
            'apple': '苹果',
            'banana': '香蕉',
            'beetroot': '甜菜根',
            'bell pepper': '甜椒',
            'cabbage': '白菜',
            'capsicum': '辣椒',
            'carrot': '胡萝卜',
            'cauliflower': '花椰菜',
            'chilli pepper': '辣椒',
            'corn': '玉米',
            'cucumber': '黄瓜',
            'eggplant': '茄子',
            'garlic': '大蒜',
            'ginger': '生姜',
            'grapes': '葡萄',
            'jalepeno': '墨西哥辣椒',
            'kiwi': '猕猴桃',
            'lemon': '柠檬',
            'lettuce': '生菜',
            'mango': '芒果',
            'onion': '洋葱',
            'orange': '橙子',
            'paprika': '红辣椒',
            'pear': '梨',
            'peas': '豌豆',
            'pineapple': '菠萝',
            'pomegranate': '石榴',
            'potato': '土豆',
            'raddish': '小红萝卜',
            'soy beans': '大豆',
            'spinach': '菠菜',
            'sweetcorn': '甜玉米',
            'sweetpotato': '甘薯',
            'tomato': '番茄',
            'turnip': '萝卜',
            'watermelon': '西瓜',
            'meat': '肉'
        }
        return translations.get(english_name.lower(), english_name)

    def check_file_and_update_label(self):
        results_file = 'object_detection_results.txt'
        base_image_path = r'E:\meal_recommend\pythonProject\imgs'
        try:
            with open(results_file, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    self.page1_result_label.setText("点击下方摄像头按钮添加食材")
                else:
                    # 清除旧有的所有子控件
                    while self.scroll_layout.count():
                        item = self.scroll_layout.takeAt(0)
                        widget = item.widget()
                        if widget is not None:
                            widget.deleteLater()
                        else:
                            # Clear nested layouts
                            sub_layout = item.layout()
                            if sub_layout is not None:
                                while sub_layout.count():
                                    sub_item = sub_layout.takeAt(0)
                                    sub_widget = sub_item.widget()
                                    if sub_widget is not None:
                                        sub_widget.deleteLater()

                    # 提取对象名称并去重
                    object_names = list(set(line.strip() for line in content.split('\n')))

                    # 创建图片布局
                    row_layout = None
                    for idx, object_name in enumerate(object_names):
                        # 每两个图片一行，创建一个新的水平布局
                        if idx % 2 == 0:
                            row_layout = QHBoxLayout()
                            self.scroll_layout.addLayout(row_layout)

                        # 垂直布局包含图片和标签
                        vbox = QVBoxLayout()

                        # 图片
                        image_path = os.path.join(base_image_path, f'{object_name}.jpg')
                        if os.path.exists(image_path):
                            image_label = ClickableImageLabel(object_name)
                            pixmap = QPixmap(image_path)
                            target_size = QSize(200, 200)  # 设置目标大小
                            pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio)
                            image_label.setPixmap(pixmap)
                            image_label.setAlignment(Qt.AlignCenter)
                            image_label.clicked.connect(self.show_detail_view)
                            vbox.addWidget(image_label)

                        # 标签
                        chinese_name = self.translate_to_chinese(object_name)
                        text_label = QLabel(chinese_name)
                        font = QFont()
                        font.setFamily("Arial")  # 设置字体
                        font.setPointSize(12)  # 设置字体大小
                        text_label.setFont(font)
                        text_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
                        vbox.addWidget(text_label)

                        # 将垂直布局添加到当前行的水平布局中
                        row_layout.addLayout(vbox)

                    # 更新滚动区域
                    self.scroll_content.setLayout(self.scroll_layout)

        except FileNotFoundError:
            self.page1_result_label.setText("文件不存在")

    def clear_recommendations(self):
        while self.scroll_layout2.count():
            item = self.scroll_layout2.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())



    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())
        layout.deleteLater()

    def recommendation(self):
        # 清空之前的推荐内容
        self.clear_recommendations()

        if os.path.getsize('./object_detection_results.txt') == 0:
            label = QLabel('请在“我的冰箱”添加食材')
            font = QFont('幼圆', 16, QFont.Bold)
            label.setFont(font)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet('color: green')
            label.setAlignment(Qt.AlignTop)
            self.scroll_layout2.addWidget(label)
            return

        node_names = set()
        with open("./object_detection_results.txt", "r", encoding="utf-8") as file:
            for line in file:
                node_names.add(line.strip())

        uri = "bolt://localhost:7687"
        username = "neo4j"  # 默认用户名
        password = "your_password"  # 请替换为您的实际密码
        self.graph = Graph(uri, auth=(username, password))

        cypher_query = """
            MATCH (r:Recipe)-[:INCLUDES]->(i:Ingredient) 
            WHERE ANY(name IN $english_names WHERE name IN i.english_name)
            WITH DISTINCT r
            MATCH (r)-[:INCLUDES]->(i:Ingredient)
            RETURN DISTINCT r.name AS chinese_name
            """
        parameters = {"english_names": list(node_names)}

        result = self.graph.run(cypher_query, parameters)
        recipes = [record["chinese_name"] for record in result]

        # 获取健康状况
        flg1, flg2, flg3 = self.health_condition()
        diseases_to_avoid = []

        if flg1 == 1:
            diseases_to_avoid.append('高血压')
        if flg2 == 1:
            diseases_to_avoid.append('糖尿病')
        if flg3 == 1:
            diseases_to_avoid.append('肥胖')

        filtered_recipes = []
        for recipe in recipes:
            query = """
                MATCH (r:Recipe {name: $dish})-[:CANTEAT]->(d:DISEASE)
                RETURN d.name AS DISEASE_name
                """
            parameters = {"dish": recipe}
            disease_results = self.graph.run(query, parameters)
            diseases = [record["DISEASE_name"] for record in disease_results]

            if not any(disease in diseases for disease in diseases_to_avoid):
                filtered_recipes.append(recipe)

        # 创建图片布局
        row_layout = None
        count = 0
        for dish_name in filtered_recipes:
            # 图片路径
            photo_path = f'./photos/{dish_name}.png'  # 假设图片路径为 './photos/菜名.png'

            # 创建垂直布局
            vbox = QVBoxLayout()

            # 图片
            if os.path.exists(photo_path):
                image_label = ClickableImageLabel(dish_name)  # 使用菜名作为参数
                pixmap = QPixmap(photo_path)
                target_size = QSize(200, 200)  # 设置目标大小
                pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio)
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                image_label.clicked.connect(self.show_food_detail_view)  # 连接点击信号到显示详情界面的槽函数
                vbox.addWidget(image_label)

            # 中文标签
            chinese_label = QLabel(dish_name)
            font = QFont()
            font.setFamily("Arial")  # 设置字体
            font.setPointSize(12)  # 设置字体大小
            chinese_label.setFont(font)
            chinese_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            vbox.addWidget(chinese_label)

            # 每行两个图片
            if count % 2 == 0:
                row_layout = QHBoxLayout()
                self.scroll_layout2.addLayout(row_layout)

            # 将垂直布局添加到水平布局中
            row_layout.addLayout(vbox)
            count += 1

        # 更新滚动区域
        self.scroll_content2.setLayout(self.scroll_layout2)

    def start_detection(self):
        self.loading_dialog = LoadingDialog()
        self.loading_dialog.show()

        self.thread = ObjectDetectionThread()
        self.thread.finished.connect(self.on_detection_finished)
        self.thread.start()

        QTimer.singleShot(5000, self.loading_dialog.close)

    def on_detection_finished(self):
        self.check_file_and_update_label()
        self.thread.deleteLater()  # 删除线程对象，释放内存
        gc.collect()  # 显式调用垃圾回收

    def show_detail_view(self, object_name):
        self.detail_view = DetailView(object_name)
        self.detail_view.show()

    def show_food_detail_view(self, object_name):
        self.detail_view = RecipeDetailView(object_name)
        self.detail_view.show()
    def closeEvent(self, event):
        # 在关闭主窗口时显式调用垃圾回收
        gc.collect()
        super().closeEvent(event)

class RecipeDetailView(QWidget):
    def __init__(self, object_name):
        super().__init__()

        self.setWindowTitle('详细信息')
        self.setFixedSize(400, 800)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)

        # 设置米色背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))  # 米色
        self.setPalette(palette)

        layout = QVBoxLayout()

        # 标签
        chinese_name = MainWindow.translate_to_chinese(object_name)
        text_label = QLabel(chinese_name)
        font = QFont()
        font.setFamily("幼圆")  # 设置字体
        font.setPointSize(20)  # 设置字体大小
        text_label.setFont(font)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)

        # 图片
        image_label = QLabel()
        pixmap = QPixmap(f"./photos/{object_name}.png")
        target_size = QSize(200, 400)  # 设置目标大小
        pixmap = pixmap.scaled(target_size, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        extra_info_label = QLabel("食材")
        layout.addWidget(extra_info_label)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.set_text_font(self.detail_text)
        layout.addWidget(self.detail_text)

        extra_info_label2 = QLabel("调料")
        layout.addWidget(extra_info_label2)

        self.detail_text2 = QTextEdit()
        self.detail_text2.setReadOnly(True)
        self.set_text_font(self.detail_text2)
        layout.addWidget(self.detail_text2)

        extra_info_label3 = QLabel("步骤")
        layout.addWidget(extra_info_label3)

        self.detail_text3 = QTextEdit()
        self.detail_text3.setReadOnly(True)
        self.set_text_font(self.detail_text3)
        layout.addWidget(self.detail_text3)

        # 返回按钮
        back_button = QPushButton('返回')
        back_button.clicked.connect(self.close)
        layout.addWidget(back_button, alignment=Qt.AlignBottom)

        self.setLayout(layout)
        self.graph = None

        self.runDatabase()
        self.showDetailRecipe(object_name)

    def set_text_font(self, text_widget):
        font = QFont()
        font.setFamily("黑体")  # 设置字体
        font.setPointSize(13)  # 设置字体大小
        text_widget.setFont(font)

    def runDatabase(self):
        if os.path.getsize('./object_detection_results.txt') == 0:
            label = QLabel('请在“我的食材”添加食材')
            return

        node_names = set()
        with open("./object_detection_results.txt", "r", encoding="utf-8") as file:
            for line in file:
                node_names.add(line.strip())

        uri = "bolt://localhost:7687"
        username = "neo4j"  # 默认用户名是neo4j
        password = "your_password_here"  # 请替换为您的实际密码
        self.graph = Graph(uri, auth=(username, password))


    def showDetailRecipe(self, object_name):
        if self.graph is None:
            return

        dish_name = object_name
        cypher_query = """
               MATCH (r:Recipe {name: $dish})-[:INCLUDES]->(i:Ingredient) 
               RETURN i.name AS ingredient_name, i.quantity AS ingredient_quantity
               """
        parameters = {"dish": dish_name}

        result = self.graph.run(cypher_query, parameters)
        ingredients = [{'name': record['ingredient_name'], 'quantity': record['ingredient_quantity']} for record in result]

        cypher_query = """
               MATCH (r:Recipe {name: $dish})-[:INCLUDES]->(s:Seasoning) 
               RETURN s.name AS seasoning_name, s.quantity AS seasoning_quantity
               """
        result = self.graph.run(cypher_query, parameters)
        seasonings = [{'name': record['seasoning_name'], 'quantity': record['seasoning_quantity']} for record in result]

        cypher_query = """
               MATCH (r:Recipe {name: $dish})-[:HAS_STEP]->(step:Step) 
               RETURN step.description AS step_description
               """
        result = self.graph.run(cypher_query, parameters)
        steps = [record['step_description'] for record in result]

        self.detail_text.clear()
        for ingredient in ingredients:
            self.detail_text.append(f"{ingredient['name']}: {ingredient['quantity']}")

        self.detail_text2.clear()
        for seasoning in seasonings:
            self.detail_text2.append(f"{seasoning['name']}: {seasoning['quantity']}")

        self.detail_text3.clear()
        for i, step in enumerate(steps, 1):
            self.detail_text3.append(f"{i}. {step}")
class ClickableImageLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, object_name):
        super().__init__()
        self.object_name = object_name

    def mousePressEvent(self, event):
        self.clicked.emit(self.object_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
