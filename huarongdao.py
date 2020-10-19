# -*- coding: utf-8 -*-
import os
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import json
import copy
from urllib import parse
import requests

# 将图片填充为正方形
def fill_image(image):
    width, height = image.size
    # 选取长和宽中较大值作为新图片的边长
    new_image_length = width if width > height else height
    # 生成新图片[白底]
    new_image = Image.new(image.mode, (new_image_length, new_image_length), color='white')
    # 将之前的图粘贴在新图上，居中
    if width > height:  # 原图宽大于高，则填充图片的竖直维度
        new_image.paste(image, (0, int((new_image_length - height) / 2)))  # (x,y)二元组表示粘贴上图相对下图的起始位置
    else:
        new_image.paste(image, (int((new_image_length - width) / 2), 0))
    return new_image    #获得填充后的图片

# 切图(n * n)
def cut_image(image, n):
    width, height = image.size
    item_width = int(width / n) #每块切图边长为宽的n分之一
    box_list = [] #定义一个空列表用来之后保存分割的图片
    for i in range(0, n):
        for j in range(0, n):
            box = (j * item_width, i * item_width, (j + 1) * item_width, (i + 1) * item_width)
            box_list.append(box)
            #裁切图片。区域由一个4元组定义，表示为坐标是 (left, upper, right, lower)
    image_list = [image.crop(box) for box in box_list]
    return image_list 

# 保存
def save_images(image_list, content):
    index = 0
    for image in image_list:
        image.save(content + '/' + str(index) + '.jpg', 'JPEG') #将切图保存在本地方便之后匹配
        index += 1


# 输入一个文件名称（与原图文件名一样，不包括后缀）,将图像切片并新建一个与图像文件名相同的文件夹（如果该文件夹不存在的话），并将切片保存在其中
# 注意，需要在当前目录下有存放各原图切片结果文件夹的tiles文件夹，且要有存放完整原图的original_img文件夹
# 所有图片均为jpg格式
def original_partition(dir):
    dirs = 'd:/jiedui/base'  # 当前目录下的tiles目录，用于存放所有原图的切片结果
    file_path1 = "d:/jiedui/data"  # 当前目录下的original_img文件夹
    file_path2 = dir + '.jpg'  # 输入original_img文件夹中的jpg文件全名（包括.jpg后缀）
    file_path = os.path.join(file_path1, file_path2)  # 组合成完整的源文件（待切片的图片）路径

    image = Image.open(file_path)  # 打开图片
    # image.show()
    image = fill_image(image)  # 将图片填充为方形
    image_list = cut_image(image, 3)  # 切割图片（3*3）

    # 在tiles文件夹里再建一个文件夹，存放一张原图的所有切片，文件夹的名字与原图文件名（不包括后缀）一样
    dir_path = os.path.join(dirs, dir)  # 组合成完整的目标文件夹路径
    # 判断文件夹是否存在，若不存在则创建目标文件夹
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    save_images(image_list, dir_path)  # 保存切片结果



def img_match(img_base64):
    img = base64.b64decode(img_base64)  # 将从接口获取的base64编码转字符串
    img = BytesIO(img)  # 字符串转字节流
    pic = Image.open(img)  # 以图片形式打开img
    # 将读取的测试图片保存到本地，同目录下的test文件夹中，并命名为orig.jpg
    pic.save('d:/jiedui/test/orig.jpg', 'JPEG')
    img_list = cut_image(pic, 3)#将图片分割成九块
    save_images(img_list, 'd:/jiedui/test/ori')
    # 将原图切分为3*3片，存入img_list列表，并将切片保存到同目录ori文件夹中
    img_arr = []  # 定义一个存放乱序切片的numpy矩阵的列表
    for root, dirs, files in os.walk("d:/jiedui/test/ori"):  # 遍历存放乱序切片的test文件夹
        for file in files:  # 处理该文件夹里的所有文件
            p = Image.open(os.path.join(root, file))  # 合成绝对路径，并打开图像
            p = np.asarray(p)  # 图像转矩阵
            img_arr.append(p)  # 将得到的矩阵存入列表
    ori_list = [-1, -1, -1, -1, -1, -1, -1, -1, -1]  # 存放乱序图片的状态，-1代表白块，0~8代表该切片是处于原图中的哪一位置
    dir_path = "d:/jiedui/base"#base文件夹为本地文件夹，存放着从图片库所有图片的切割分片，并按图片名并分好类
    # 遍历同目录中文件夹中的所有文件夹
    for root, dirs, files in os.walk(dir_path):
        for dir in dirs:
            # k代表状态列表下标，cnt记录当前已匹配上的切片数
            k =  0
            cnt = 0
            # tmp_list列表存放目标状态，由于不同原图之间可能存在完全一样的切片，会影响tmp_list的最终结果
            # 因此每次与新的一张原图比较前，将tmp_list初始化为全-1
            tmp_list = [-1, -1, -1, -1, -1, -1, -1, -1, -1]
            # 从img_arr列表（即乱序切片的numpy矩阵列表）中，逐个与原图库中的切片比较
            for i in img_arr:
                # index用于指示乱序的切片在原图的哪一位置
                index = 0
                # 遍历存放原图切片的文件夹中的所有文件（即，原图切片）
                for root, dirs, files in os.walk(os.path.join(dir_path, dir)):
                    for j in files:
                        # 用os.path.join()拼接出文件的绝对路径，然后打开该文件（图片）
                        j = Image.open(os.path.join(root, j))
                        j = np.asarray(j)  # 将原图切片转换为numpy矩阵
                        if (i == j).all():  # 判断两个矩阵是否完全相同
                            ori_list[k] = index
                            tmp_list[index] = index
                            cnt += 1
                            break
                        index += 1
                    k += 1
            # 若已有8个切片匹配上则说明匹配到了原图
            if cnt > 7:
                print("该图原图是:", dir)  # 打印原图名称
                break 
        if cnt < 8:
            print("ERROR：无匹配图片，请重新确认")
    # 遍历初始状态列表，获得白块的初始位置
    for i in range(len(ori_list)):
        if ori_list[i] < 0:
            blank = i
            break
    # 返回初始状态（列表）、空白块位置、目标状态（列表）
    return  ori_list, blank, tmp_list






    

"""


url_1 = "http://47.102.118.1:8089/api/challenge/create"
jie = {
    "teamid": 54,
    "data": {
        "letter": "k",
        "exclude": 7,
        "challenge": [
            [3, 1, 4],
            [8, 5, 0],
            [6, 2, 9]
        ],
        "step": 6,
        "swap": [7,7]
    },
    "token": "c71f5f61-d994-49d1-8b2d-345b6fb15d55"
}

res = requests.post(url=url_1, json=jie)
res = json.loads(res.text)
print(res)
"""


"""

url_3 = "http://47.102.118.1:8089/api/challenge/list"
res = requests.get(url=url_3)
res = json.loads(res.text)
#print(res)
for i in range(len(res)):
    str_1 = parse.quote_plus(res[i]['uuid'])
    url_4 = "http://47.102.118.1:8089/api/challenge/start/" 
    url_5 = parse.urljoin(url_4,str_1)
    chan = {
                'teamid':54,
                'token':"c71f5f61-d994-49d1-8b2d-345b6fb15d55"
            }
    res_2 = requests.post(url=url_5,json=chan)
    res_2 = json.loads(res_2.text)
    #print(res_2)
    step_num = res_2['data']['step']  # 第几步进行强制交换
    swap_scheme = res_2['data']['swap']  # 强制交换最初方案
     # 题目中图片编号1~9，程序中为0~8，故调整一下调换图片的编号
    swap_scheme[0] -= 1
    swap_scheme[1] -= 1
    start, pos, end = img_match(res_2['data']['img'])
    #乱序图片位置，白块位置，输出目标状态，强制交换，强制交换方案
    solve = IDAstar(start, pos, end, step_num, swap_scheme)
    path = solve.IDA()
    #所求路径
    # 调整编号，符合题目要求
    solve.swap_scheme[0] += 1
    solve.swap_scheme[1] += 1
    #print(path)
    #print(solve.swap_scheme)

    url_6 = "http://47.102.118.1:8089/api/challenge/submit"
    up = {
            "uuid":res_2['uuid'],
            "teamid":54,
            "token":"c71f5f61-d994-49d1-8b2d-345b6fb15d55",
            "answer":{
                "operations":path,
                "swap":solve.swap_scheme
            }
        }
    res_3 = requests.post(url=url_6,json=up)
    res_3 = json.loads(res_3.text)
    print(res_3)
    print("################################")

"""
"""
url_7 = "http://47.102.118.1:8089/api/teamdetail/54"
req = requests.get(url=url_7)
req = json.loads(req.text)
print(req)
"""
