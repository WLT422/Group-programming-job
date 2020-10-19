# coding=utf-8
import os
import base64
import numpy as np
# import random      # 随机打乱列表时可以用上
from PIL import Image
from io import BytesIO
import requests
import json
import copy


def fill_image(image):
    width, height = image.size
    # 选取长和宽中较大值作为新图片的
    new_image_length = width if width > height else height
    # 生成新图片[白底]
    new_image = Image.new(image.mode, (new_image_length, new_image_length), color='white')
    # 将之前的图粘贴在新图上，居中
    if width > height:  # 原图宽大于高，则填充图片的竖直维度
        new_image.paste(image, (0, int((new_image_length - height) / 2)))  # (x,y)二元组表示粘贴上图相对下图的起始位置
    else:
        new_image.paste(image, (int((new_image_length - width) / 2), 0))
    return new_image


# 切图(n * n)
def cut_image(image, n):
    width, height = image.size
    item_width = int(width / n)
    box_list = []
    # (left, upper, right, lower)
    for i in range(0, n):
        for j in range(0, n):
            # print((i*item_width,j*item_width,(i+1)*item_width,(j+1)*item_width))
            box = (j * item_width, i * item_width, (j + 1) * item_width, (i + 1) * item_width)
            # box = np.asarray(box)   # 将切片转换为numpy矩阵
            box_list.append(box)

    image_list = [image.crop(box) for box in box_list]

    return image_list  # 返回numpy矩阵列表


# 保存
def save_images(image_list, content):
    index = 0
    for image in image_list:
        image.save(content + '/' + str(index) + '.jpg', 'JPEG')
        index += 1

list_a = ['A_ (2)', 'a_', 'b_ (2)', 'B_', 'c_', 'd_ (2)', 'D_', 'e_', 'F_', 'g_', 'h_ (2)','H_', 'j_', 'k_', 'm_ (2)', 'M_', 'n_', 'o_ (2)', 'O_', 'p_ (2)', 'P_', 'q_ (2)', 'Q_', 'r_', 's_', 't_', 'u_ (2)', 'U_', 'v_', 'W_', 'x_ (2)', 'X_', 'y_ (2)', 'Y_', 'z_ (2)','Z_']




dirs = 'd:/jiedui/base'  # 当前目录下的tiles目录，用于存放所有原图的切片结果
file_path1 = "d:/jiedui/data"  # 当前目录下的original_img文件夹
for i in range(len(list_a)):
    file_path2 = list_a[i] + '.jpg'  # 输入original_img文件夹中的jpg文件全名（包括.jpg后缀）
    file_path = os.path.join(file_path1, file_path2)  # 组合成完整的源文件（待切片的图片）路径

    image = Image.open(file_path)  # 打开图片
        # image.show()
    image = fill_image(image)  # 将图片填充为方形
    image_list = cut_image(image, 3)  # 切割图片（3*3）

        # 在tiles文件夹里再建一个文件夹，存放一张原图的所有切片，文件夹的名字与原图文件名（不包括后缀）一样
    dir_path = os.path.join(dirs, list_a[i])  # 组合成完整的目标文件夹路径
        # 判断文件夹是否存在，若不存在则创建目标文件夹
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        save_images(image_list, dir_path)  # 保存切片结果