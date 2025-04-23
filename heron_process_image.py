from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ultralytics import YOLO
import os
import time

import logging
from tuya_connector import TuyaOpenAPI, TUYA_LOGGER

ACCESS_ID = "ed8gtgj49j8ydsdtrjr9"
ACCESS_KEY = "49623eecc5784eec998312370bddca81"
API_ENDPOINT = "https://openapi.tuyacn.com"


# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

# Init openapi and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

# set up device_id
DEVICE_ID ="6c1bd2460126cde002mwqa"

model = YOLO("best.pt")
class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # print("any_event", event)
        if (((event.src_path).strip().endswith("jpg") or (event.src_path).strip().endswith("png")) and event.event_type=='modified'):
            os.remove((event.src_path).strip())
        # print(event.event_type, event.src_path)

    def on_created(self, event):
        # print("on_created", event.src_path)
        # print(event.src_path.strip())
        if((event.src_path).strip().endswith("jpg") or (event.src_path).strip().endswith("png") ):
            try:
                print(event.src_path, "path")
                results = model((event.src_path).strip())
                # print("results", results)
                conf = results[0][0].boxes.conf[0].item()
                cls = results[0][0].boxes.cls[0].item()
                # print("??", type(results[0][0]))
                print("conf", conf)
                print("cls", cls)
                if conf >= 0.7 and cls == 1:
                    print("blue heron!!")
                    commands = {'commands': [{'code': 'switch_1', 'value': True}]}
                    openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                    time.sleep(2)
                    commands = {'commands': [{'code': 'switch_1', 'value': False}]}
                    openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID), commands)
                elif conf >= 0.7 and cls == 0:
                    print("other birds")
                else:
                    print("no birds detected")
            except:
                print("no birds detected")
            time.sleep(5)

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=False)
observer.start()

input()




