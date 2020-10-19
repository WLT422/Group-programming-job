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



class Board:
    def __init__(oneself, ori_list, pos, step=0, preboard=None, prepath=""):
        oneself.ori_list = ori_list
        oneself.pos = pos
        oneself.step = step
        oneself.cost = oneself.cal_cost()
        oneself.preboard = preboard
        oneself.prepath = prepath
    #计算移动代价
    def cal_cost(oneself):
        count = 0
        sheet = [[0, 0], [0, 1], [0, 2],
                 [1, 0], [1, 1], [1, 2],
                 [2, 0], [2, 1], [2, 2]]#每个位置的坐标
        for i in range(9):
            if oneself.ori_list[i] < 0:
                continue
            count += abs(sheet[i][0] - sheet[oneself.ori_list[i]][0]) + abs(sheet[i][1] - sheet[oneself.ori_list[i]][1]) #启发函数
        # cost = count + oneself.step
        # return cost
        return count + oneself.step


class IDAstar:
    # 当白块在9个位置时可以移动的方向，-1代表无法移动
    # w上, d右, s下, a左
    d = [[-1, 1, 3, -1],  # 0
         [-1, 2, 4, 0],  # 1
         [-1, -1, 5, 1],  # 2
         [0, 4, 6, -1],  # 3
         [1, 5, 7, 3],  # 4
         [2, -1, 8, 4],  # 5
         [3, 7, -1, -1],  # 6
         [4, 8, -1, 6],  # 7
         [5, -1, -1, 7]]  # 8
    # 将移动方向的序列转化为'w', 'd', 's', 'a'，上，右，下，左
    index_to_direct = ['w', 'd', 's', 'a']
    swap_record = {}    # 用于记录强制交换阶段的交换方案
    # forced_mark = True  # 标记最初的强制交换是否可解，若可解则不能自由交换
    no_swap_exe = True  # 标记是否执行了强制交换
    find_sol = False  # 标记是否解决8 puzzle问题

    def __init__(oneself, start, pos, target, step_num, swap_scheme):
        # 初始状态、白块初始位置、目标状态、第几步进行强制交换、强制交换的最初方案
        # step_num为数字、swap_scheme为两个元素的列表
        IDAstar.start = start
        IDAstar.pos = pos
        IDAstar.target = target
        IDAstar.init = Board(start, pos)
        IDAstar.maxdep = 0   # 搜索的最大深度
        IDAstar.path = ""
        IDAstar.step_num = step_num
        IDAstar.swap_scheme = swap_scheme
        # 判断目标状态的逆序对数是奇数还是偶数，当前状态必须与目标状态同奇同偶才可解
        IDAstar.solvable = Judge_even(target)
        swap_record = {}    # 用于记录强制交换阶段的交换方案
        # print("IDAstar.solvable: ", IDAstar.solvable)

    def dfs(oneself, now, lastd, n):
        if now.ori_list == oneself.target: 
            oneself.find_sol = True
            return True

        # swap_mark = False  # 强制交换的标记，若本次搜索用到了强制交换，则为True
        # 强制交换, n 表示当前的步数

        if oneself.no_swap_exe and n == oneself.step_num:
            scheme = oneself.forced_exchange(now.ori_list)
            oneself.no_swap_exe = False
            now.ori_list[scheme[0]], now.ori_list[scheme[1]] = now.ori_list[scheme[1]], now.ori_list[scheme[0]]
            now.step = 0    # 强制交换后，从头搜索
            # 记录白块位置
            for i in range(len(now.ori_list)):
                if now.ori_list[i] < 0:
                    now.pos = i
                    break
            now.cost = now.cal_cost()  # 交换后重新计算代价
            oneself.maxdep = now.cost  # 重新计算最大深度
            oneself.init.ori_list = copy.deepcopy(now.ori_list)
            oneself.init.pos = now.pos
            oneself.init.step = now.step
            oneself.init.cost = now.cost
            oneself.swap_scheme = copy.deepcopy(scheme)  # 记录交换方案
            return True

        # 基于f值的强力剪枝
        if now.cost > oneself.maxdep:
            return False

        pos = now.pos
        step = now.step
        for i in range(4):
            # 方向不可走时
            if oneself.d[pos][i] == -1:
                continue
            # 0, 1, 2, 3
            # w, d, s, a
            # 上一步为向左，此步则不能向右走老路，其他方向同理。
            if (lastd == -1) or (lastd % 2) != (i % 2) or (lastd == i):
                ori_list = copy.deepcopy(now.ori_list)
                ori_list[pos], ori_list[oneself.d[pos][i]] = ori_list[oneself.d[pos][i]], ori_list[pos]
                # 构造函数形式：
                temp = Board(ori_list, oneself.d[pos][i], step + 1, now, oneself.index_to_direct[i])
                # 如果找到最短路径，递归地记录路径
                if oneself.dfs(temp, i, n+1):
                    oneself.path += temp.prepath
                    return True
        return False

    def IDA(oneself):
        oneself.maxdep = oneself.init.cost
        while not oneself.dfs(oneself.init, -1, 0):
            oneself.maxdep += 1
        #迭代加深
        tmp_path = oneself.path[::-1]
        oneself.path = ""
        if not oneself.find_sol:
            while not oneself.dfs(oneself.init, -1, 0):
                oneself.maxdep += 1
        oneself.path = tmp_path + oneself.path[::-1]
        return oneself.path

    # 在当前状态ori_list进行强制交换，若强制交换导致无解，则紧接着进行一次自由交换
    # 返回强制交换的方案
    def forced_exchange(oneself, ori_list):
        # 交换两个块
        tmp0 = copy.deepcopy(ori_list)
        if oneself.swap_scheme[0] != oneself.swap_scheme[1]:
            tmp0[oneself.swap_scheme[0]], tmp0[oneself.swap_scheme[1]] = tmp0[oneself.swap_scheme[1]], tmp0[oneself.swap_scheme[0]]
        # 若最初的强制交换不会造成无解，则返回
        if Judge_even(tmp0) == oneself.solvable:
            return oneself.swap_scheme
        # 否则，进行自由交换
        else:
            # 先要强制交换，在强制交换的基础上自由交换
            ori_list[oneself.swap_scheme[0]], ori_list[oneself.swap_scheme[1]] = ori_list[oneself.swap_scheme[1]], ori_list[oneself.swap_scheme[0]]
            # 双重循环，遍历可自由交换出的所有状态
            for i in range(8):
                for j in range(i+1, 9):
                    tmp = copy.deepcopy(tmp0)
                    tmp[i], tmp[j] = tmp[j], tmp[i]
                    if Judge_even(tmp) == oneself.solvable:
                        for k in range(len(tmp)):
                            if tmp[k] < 0:
                                break
                        tmp_board = Board(tmp, k)
                        cost_h = tmp_board.cost
                        # 以cost_h为键，交换方案为值，可能会有多个方案的cost_h相同的情况，但字典中只记录一个
                        oneself.swap_record[cost_h] = [i, j]
            m = min(oneself.swap_record)  # 找到最小的代价
            oneself.swap_scheme = copy.deepcopy(oneself.swap_record[m])
            return oneself.swap_scheme  # 返回最小代价对应的交换方案

# 归并函数，返回一趟归并的逆序对数
def merge(listA, tmpA, L, R, RightEnd):
    # L为待归并数组中，左半个数组的首元素下标；R为右半个数组的首元素下标
    # RightEnd为待归并数组最后一个元素的下标
    cnt = 0
    LeftEnd = R-1  # 左半个数组最后一个元素的下标
    tmp = L
    NumElements = RightEnd-L+1  # 待归并数组元素总数
    while (L <= LeftEnd) and (R <= RightEnd):
        if listA[L] <= listA[R]:
            tmpA[tmp] = listA[L]
            tmp += 1
            L += 1
        else:
            tmpA[tmp] = listA[R]
            tmp += 1
            R += 1
            cnt += LeftEnd-L+1
    while L <= LeftEnd:
        tmpA[tmp] = listA[L]
        tmp += 1
        L += 1
    while R <= RightEnd:
        tmpA[tmp] = listA[R]
        tmp += 1
        R += 1
    for i in range(NumElements):
        listA[RightEnd] = tmpA[RightEnd]
        RightEnd -= 1
    return cnt


# 循环进行归并排序，返回以len为步长进行归并排序得到的逆序对数
def merge_pass(listA, tmpA, N, len):
    # 一趟归并（采用循环方法，非递归）
    cnt = 0
    double_len = 2*len
    i = 0  # 需要提前声明，否则会报错（变量i在声明前就被使用）
    for i in range(0, N-double_len+1, double_len):
        cnt += merge(listA, tmpA, i, i+len, i+double_len-1)
    if (i + len) < N:
        cnt += merge(listA, tmpA, i, i+len, N-1)
    else:
        for j in range(i, N):
            tmpA[j] = listA[j]
    return cnt


# 基于归并排序求列表中逆序对的数目
def inverse_number(listA, N):
    # 使用非递归的方法实现基于归并排序的逆序对数目计数
    len = 1
    cnt = 0
    tmpA = [0]
    tmpA = tmpA*N
    while len < N:
        cnt += merge_pass(listA, tmpA, N, len)
        len *= 2
        cnt += merge_pass(tmpA, listA, N, len)
        len *= 2
    return cnt


# 判断列表中逆序对数的奇偶，若为偶，返回True
# 计算逆序对数时，不算空白块
def Judge_even(listA):
    n = len(listA)
    # inverse_number函数会进行归并排序，破坏原列表，故先拷贝一份
    tmp = copy.deepcopy(listA)
    for i in range(n):
        if tmp[i] < 0:
            del tmp[i]
            n -= 1
            break
    cnt = inverse_number(tmp, n)
    if (cnt % 2) == 0:
        return True
    else:
        return False





    

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
            # print("初始状态: ", start)  # 输出乱序图片的状态，也即拼图游戏的初始状态（-1代表白块，0~8代表该切片是处于原图中的哪一位置）
            # print("白块位置: ", pos)    # 输出空白块在乱序图中的位置
            # print("目标状态: ", end)  # 输出目标状态
            # print(type(start), type(end))
    solve = IDAstar(start, pos, end, step_num, swap_scheme)
    path = solve.IDA()
            # print(path, "路径长度: ", len(path))
            # 调整编号，符合题目要求
    solve.swap_scheme[0] += 1
    solve.swap_scheme[1] += 1
            # print("交换图片: ", solve.swap_scheme)
            # print("url: ",type(url_post))
            # print("uuid: ",type(resp_g['uuid']))
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
url_7 = "http://47.102.118.1:8089/api/teamdetail/54"
req = requests.get(url=url_7)
req = json.loads(req.text)
print(req)
"""
