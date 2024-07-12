import numpy as np
from keras_preprocessing.image import ImageDataGenerator
from sklearn.metrics import confusion_matrix

# 加载模型
from tensorflow.keras.models import load_model
model = load_model('final_model.h5')

# 加载测试数据
test_dir = "./fandv/test"
test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(180, 180),
    batch_size=32,
    class_mode='categorical',
    shuffle=False)

# 评估模型
loss, accuracy = model.evaluate(test_generator)

print("Test Accuracy:", accuracy)
print("Test Loss:", loss)

# 预测测试数据
predictions = model.predict(test_generator)
y_true = test_generator.classes
y_pred = np.argmax(predictions, axis=1)

# 生成混淆矩阵
conf_matrix = confusion_matrix(y_true, y_pred)
print("Confusion Matrix:")
print(conf_matrix)


from tensorflow.keras.models import load_model

# 加载模型
loaded_model = load_model('final_model.h5')

# 打印模型摘要
loaded_model.summary()
