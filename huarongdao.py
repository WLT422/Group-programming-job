# -*- coding: utf-8 -*-
import requests
import json
import base64
from PIL import Image
from io import BytesIO



url = "http://47.102.118.1:8089/api/problem?stuid=031802230"
r = requests.get(url)
json_r = r.json()

img_1 = json_r["img"]
step_1 = json_r["step"]
swap_1 = json_r["swap"]
uuid_1 = json_r["uuid"]
#print(img_1)
#print(step_1)
#print(swap_1)
#print(uuid_1)

img_1 = base64.b64decode(img_1)
#print(img_1) #得到一个表示图片的bytes
img_1 = BytesIO(img_1)
pic = Image.open(img_1)
#获得图片
#pic.show()展示图片








"""
answer_url = "http://47.102.118.1:8089/api/answer"
fina = {"uuid":"uuid_1",
        "answer":
           {
            "operation"："op_1",
            "swap":"swap_2"
            }
        }
r2 = requests.post(answer_url,json=fina)

def panduan(a[]):
    inversecnumber = 0
    for i in range(len(a)):
        j = i + 1
        for j in range(len(a)):
            if a[i] > a[j]:
                inversecnumber + = 1
        i + = 1
    if inversecnumber % 2 != 0:
        #继续拼图
    else：
        #输出成功

"""