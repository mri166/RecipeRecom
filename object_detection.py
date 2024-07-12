import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QStackedWidget, \
    QHBoxLayout, QDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QIcon, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QSize, QTimer
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import image_dataset_from_directory
import gc


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

    def clear(self):
        # 显示空白帧
        white_image = np.full((480, 640, 3), 255, dtype=np.uint8)
        self.display_frame(white_image)

class CameraWindow(QWidget):
    def __init__(self):
        super(CameraWindow, self).__init__()
        self.setWindowTitle('识别系统')
        self.setWindowIcon(QIcon('icon.png'))  # 设置窗口图标
        self.setGeometry(100, 100, 800, 600)

        # 设置米色背景
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 220))  # 米色
        self.setPalette(palette)

        self.camera_widget = CameraWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.camera_widget)

        self.finish_button = QPushButton('返回', self)
        self.finish_button.clicked.connect(self.finishObjectDetection)
        self.finish_button.setFixedSize(150, 50)
        self.finish_button.setStyleSheet("""
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
        layout.addWidget(self.finish_button, alignment=Qt.AlignCenter)
        self.finish_button.setEnabled(False)

        self.setLayout(layout)

        self.model = None
        self.class_names = None
        self.cap = None

        self.confidence_threshold = 0.9
        self.consecutive_matches_threshold = 5
        self.match_counter = 0
        self.current_prediction = None
        self.last_content = None

    def load_model_and_classes(self):
        # 加载训练好的模型
        self.model = load_model('best_model.h5')

        # 加载类别名称列表
        train_dataset = image_dataset_from_directory("./fandv/train", image_size=(180, 180), batch_size=32)
        self.class_names = train_dataset.class_names
        print(train_dataset.class_names)

    def startObjectDetection(self):
        self.finish_button.setEnabled(True)

        self.load_model_and_classes()

        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "无法打开摄像头")
            self.cap = None
            self.finish_button.setEnabled(False)
            return

        while True:
            # 读取摄像头图像
            ret, frame = self.cap.read()
            if not ret:
                break
            # 进行图像识别
            predicted_class_name, confidence = self.object_detection(frame)
            # 在图像上绘制类别标签和置信度（当置信度大于等于0.9时）
            if confidence >= 0.9:
                text = f"{predicted_class_name}: {confidence:.2f}"
                cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (255, 0, 0), 2)  # 绘制类别标签和置信度
            # 显示图像
            self.camera_widget.display_frame(frame)

            # 如果连续5次识别到同一个结果且可信度大于0.9
            if predicted_class_name == self.current_prediction and confidence >= self.confidence_threshold:
                self.match_counter += 1
                if self.match_counter >= self.consecutive_matches_threshold:
                    new_content = f"{predicted_class_name}\n"
                    if new_content != self.last_content:
                        with open('object_detection_results.txt', 'a') as f:
                            f.write(new_content)
                        QMessageBox.information(self, 'Success', '添加成功！')
                        self.last_content = new_content
            else:
                self.match_counter = 0
                self.current_prediction = predicted_class_name

            # 检测按键，如果按下 'q' 键则退出循环
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # 检查是否需要停止图像识别
            QApplication.processEvents()
            if self.cap is None or not self.cap.isOpened():
                break

        # 释放摄像头资源
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.camera_widget.clear()

        # 进行垃圾回收
        gc.collect()

    def object_detection(self, frame):
        # 预处理图像
        resized_frame = cv2.resize(frame, (180, 180))  # 调整大小
        normalized_frame = resized_frame / 255.0  # 归一化
        input_image = np.expand_dims(normalized_frame, axis=0)  # 扩展维度以匹配模型输入

        # 进行预测
        predictions = self.model.predict(input_image)
        predicted_class_index = np.argmax(predictions)
        predicted_class_name = self.class_names[predicted_class_index]
        confidence = predictions[0, predicted_class_index]

        return predicted_class_name, confidence

    def finishObjectDetection(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.finish_button.setEnabled(False)
        self.camera_widget.clear()
        self.close()
        # 显式调用垃圾回收
        gc.collect()

    def closeEvent(self, event):
        self.finishObjectDetection()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    window.startObjectDetection()  # 开始图像识别
    sys.exit(app.exec_())
