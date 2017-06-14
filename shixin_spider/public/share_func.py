#coding=utf-8
import os
import time
import json
import random
from io import BytesIO
from PIL import Image
from time import strftime, localtime
from pytesseract import image_to_string


def getIp():
    """ 为X-Forwarded-For构造ip地址
    :return:ipv4字符串 """
    a = random.randint(128, 223)
    b = random.randint(128, 223)
    c = random.randint(128, 223)
    d = random.randint(128, 223)
    return '{0}.{1}.{2}.{3}'.format(a,b,c,d)
# end

def getTimestamp(length=13):
    """ 获得指定长度的时间戳
    :param length: 时间戳长度
    :return: 时间戳字符串 """
    temp = str(time.time()).split('.')
    temp = ''.join(temp)
    str_time_stamp = temp[0:length] if len(temp) > length else  temp + '0'*(length-len(temp))
    return str_time_stamp
# end

def recogImage(content):
    """ 识别仅有有数字的简单验证码
    :param content: response.content
    :return: 数字字符串/False """
    file = BytesIO(content)
    img = Image.open(file)
    result = image_to_string(img)
    result = result if result.isdigit() else False
    img.close()
    file.close()
    return result
# end

def getUserAgent():
    """ 获取随机的头代理
    :return: 头代理 """
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.154 Safari/537.36 LBBROWSER',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.69 Safari/537.36 QQBrowser/9.1.3876.400'
    ]
    return random.choice(user_agent_list)
# end

def getUniqueFileName(num=2):
    """ 时间戳+随机数构造唯一文件名
    :param num: 随机次数
    :return: 数字字符串 """
    result = ''
    for i in range(num):
        result += str(random.randint(1, 200000))
    return getTimestamp() + result
# end

def saveImage(response, img_dire='code', img_name='', img_type='.jpg'):
    """ 保存图片
    :param response: request返回对象
    :param img_dire:  当前目录下的文件夹
    :param img_name:  图片文件名
    :param img_type: 图片格式
    :return: 图片的绝对路径 """
    path = os.path.join(os.getcwd(), img_dire)
    if not os.path.exists(path):
        os.mkdir(path)
    image_path = os.path.join(path, getUniqueFileName() + str(img_name) + img_type)
    with open(image_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):   #chunk_size=1024
            if chunk:
                f.write(chunk)
                f.flush()
    return image_path
# end

def removeAllFiles(dires):
    """ 删除指定目录的所有文件，异常则跳过
    :param dires: 目录列表
    :return: None """
    if not isinstance(dires, list):
        raise ValueError
    for dire in dires:
        for file in os.listdir(dire):
            try:
                os.remove(os.path.join(dire, file))
            except Exception:
                pass
# end

def clawLog(group, result, other=''):
    """ 在当前目录下的clawed_log目录下打log
    :param group: id列表
    :param result: 字符串统计结果
    :return: None"""
    dire = './clawed_log'
    if not os.path.exists(dire):
        os.mkdir(dire)

    log_name = strftime('%Y-%m-%d.%Hh',localtime()) + '.log' # 格式为：年-月-日.时h.log
    log_path = os.path.join(dire, log_name)
    with open(log_path, 'a') as f:
        f.write(time.ctime() + ':\t' + result + '\n' +  json.dumps(dict(sys_id=group)) + '\n'*2)
# end

def makeDirs(dirs=None):
    """ 在当前目录下创建目录
    :param dirs: list
    :return: None
    """
    if not dirs:
        dirs = ['clawed_log']
    current_dire = os.getcwd()
    for dir in dirs:
        abs_path = os.path.join(current_dire, dir)
        if not os.path.isdir(abs_path):
            os.mkdir(abs_path)
# end


if __name__ == '__main__':
    pass


