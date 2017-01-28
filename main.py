#!/usr/bin/env python3

try:
    import subprocess
    import threading
    import cv2
    import sys
    import time
    import os
    import datetime
##    import pymysql as mysql

except:
    print("initialization error")
    exit(1)


output = ''
##video_capture = cv2.VideoCapture(0)
models = []
run = True

def subRFID():
    # RFID sbprocess
    readings = 5
    print('rfid started')

    while readings > 0:
        rfidproc = subprocess.Popen('python RFID-process.py', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        (output, errors) = rfidproc.communicate()
        readings -= 1
        print(output.split(':')[-1])
        time.sleep(1)

    print('thread finished')
    rfidproc.terminate()



try:
    
    RFID_Process = threading.Thread(target=subRFID, name="RFID_PROCESS",)
    RFID_Process.start()

except:
    print('threading error')
    exit(1)