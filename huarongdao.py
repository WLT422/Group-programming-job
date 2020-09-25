# -*- coding: utf-8 -*-
import requests
import json

url = "http://47.102.118.1:8089/api/problem?stuid=031802230"
r = requests.get(url)
json_r = r.json()

img_1 = json_r["img"]
step_1 = json_r["step"]
swap_1 = json_r["swap"]
uuid_1 = json_r["uuid"]
print(img_1)
print(step_1)
print(swap_1)
print(uuid_1)

answer_url = "http://47.102.118.1:8089/api/answer"
fina = {"uuid":"uuid_1",
        "answer":
            {
            "operation"："op_1",
            "swap":"swap_2"
            }
        }
r2 = requests.post(answer_url,json=fina)