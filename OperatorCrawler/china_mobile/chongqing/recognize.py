# -*- coding:utf-8 -*-

# import random
# from PIL import Image
# from os import listdir
# from sklearn import metrics
# from sklearn import cross_validation
from customize import captcha
from sklearn import neighbors
from sklearn.externals import joblib


def save_model():
    """保存模型"""


    # 加载训练集
    train_x, train_y = captcha.loadTrainSet('train_data.csv')

    # # 交叉验证
    # train_data, test_data, train_target, test_target = \
    #     cross_validation.train_test_split(train_x, train_y, test_size=0,
    #                                       random_state=0)
    # 实例化分类器
    knn = neighbors.KNeighborsClassifier()

    #训练模型
    clf = knn.fit(train_x, train_y)

    # 保存模型
    joblib.dump(clf, 'model/knn.pkl')

def image_to_string(image):
    """识别图片，返回字符串

    :param image: Image对象
    :return: str
    """

    img = captcha.twoValueImage(image, 100)
    img = captcha.clear_frame(img, 1)
    img = captcha.clear_noise(img, (4, 4))
    images = captcha.cut_mean(img, 4)
    str = ''
    for i, each in enumerate(images):
        image = captcha.format_size(each, (30, 30))
        image = captcha.clear_noise(image, (6, 6))
        image = captcha.clear_noise(image, (3, 15))
        image = captcha.cut_around(image)
        image = captcha.format_size(image, (20, 20))
        image_metrics = captcha.two_Value(image, 'list')
        clf = joblib.load('model/knn.pkl')
        str = str + clf.predict(image_metrics)[0]

    return str

if __name__ == '__main__':

    # img = Image.open('trainset/55.png')
    # print image_to_string(img)
    # save_model()
    pass