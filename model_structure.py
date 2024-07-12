from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import load_model
# 加载模型
model = load_model('best_model.h5')

# 打印完整模型摘要
print("Complete Model Summary:")
model.summary()
