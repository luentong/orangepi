from ultralytics import YOLO
import time

import requests
from requests.auth import HTTPDigestAuth
from PIL import Image
from io import BytesIO

# 请求头
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'curl/4.7.1',
    'Cache-Control': 'no-cache',
    'Postman-Token': 'cfdf0937-f7a5-4b79-8c39-42eb232d4c0b',
}
username = 'admin'
password = '123456'  # 密码通常需要填写，但在此示例中未提供

def http_post_light_capture():
    
    url = 'http://192.168.1.188/digest/CaptureV2'
    data = {
        "Type": 1,
        "Ch": 1,
        "Dev": 1,
        "Data": {
            "DataType": 0,
            "StreamNo": 0
        }
    }

    response = requests.post(url, json=data, headers=headers, auth=HTTPDigestAuth(username, password))

    image_bytes = BytesIO(response.content)

    # 使用Pillow来打开图像
    image = Image.open(image_bytes)

    # 保存图像
    print("image saved")
    image.save(r'/home/orangepi/Desktop/image.jpg')

def http_post_light_turn_on():

    url = 'http://192.168.1.188/digest/frmIotLightCfg'

    data = {
        "Type": 1,
        "Ch": 1,
        "Dev": 1,
        "Data": {
            "Mode": 'Warm',
            "Control": 1,
            "LightOnTime": 2,
            "Brightness": 100
        }
    }
    response = requests.post(url, json=data, headers=headers, auth=HTTPDigestAuth(username, password))

def http_post_light_turn_off():
    url = 'http://192.168.1.188/digest/frmIotLightCfg'

    data = {
        "Type": 1,
        "Ch": 1,
        "Dev": 1,
        "Data": {
            "Mode": 'Warm',
            "Control": 0,
            "LightOnTime": 2,
            "Brightness": 100
        }
    }
    response = requests.post(url, json=data, headers=headers, auth=HTTPDigestAuth(username, password))

model = YOLO("best.pt")
print("started!!!!")

while(True):
    try:
        src_path = '/home/orangepi/Desktop/image.jpg'
        http_post_light_capture()
        print("after capture")
        results = model((src_path).strip())
        print("results", results)
        conf = results[0][0].boxes.conf[0].item()
        cls = results[0][0].boxes.cls[0].item()
        # print("??", type(results[0][0]))
        print("conf", conf)
        print("cls", cls)
        if conf >= 0.45 and cls == 1:
            print("blue heron!!")
            http_post_light_turn_on()
            time.sleep(2)
            http_post_light_turn_off()
        elif conf >= 0.45 and cls == 0:
            print("other birds")
            http_post_light_turn_off()
        else:
            http_post_light_turn_off()
            print("no birds detected")
    except:
        print("no birds detected exception")
    time.sleep(2)




