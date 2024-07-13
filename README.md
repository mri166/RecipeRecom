# RecipeRecom
基于视觉识别和知识图谱的饮食推荐系统
## 1.运行环境
python                    3.7.16
tensorflow-gpu            2.6.0       
Neo4j
py2neo                    2021.2.4                 
PyQt5                     5.15.9                 
pyqt5-plugins             5.15.9.2.3            
PyQt5-Qt5                 5.15.2               
PyQt5-sip                 12.13.0              
pyqt5-tools               5.15.9.3.3             
qt5-applications          5.15.2.2.3           
qt5-tools                 5.15.2.1.3          
sqlite                    3.41.2              
opencv-python             3.4.10.35    
## 2.实现逻辑
tensorflow训练图像识别模型，图像数据集来源于Kaggle。
Neo4j构建知识图谱。
PyQt5绘制前端界面。
## 3.软件功能
点击摄像头识别食材。识别出的食材将展示在前端界面中。
点击食材可以弹出营养含量。
在身体健康界面可以统计身体健康情况。
根据现有食材和身体健康情况进行菜品推荐。
## 4.数据集

