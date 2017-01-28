#!/usr/bin/env python3

try:
    import subprocess
    import threading
    import cv2
    import sys
    import time
    import os
    import datetime
    import config
##    import pymysql as mysql

except:
    print("initialization error")
    exit(1)


output = ''
##video_capture = cv2.VideoCapture(0)

camera = config.get_camera()
haar_faces = cv2.CascadeClassifier(config.HAAR_FACES)

owd = os.getcwd()
# make this iterative
user = "oliver_grayson"
models = [cv2.face.createEigenFaceRecognizer()]
os.chdir(config.POSITIVE_DIR+"/"+user)
for model in models:
    model.load(config.TRAINING_FILE)

run = True

def crop(image, x, y, w, h):
        """Crop box defined by x, y (upper left corner) and w, h (width and height)
        to an image with the same aspect ratio as the face training data.  Might
        return a smaller crop if the box is near the edge of the image.
        """
        crop_height = int((config.FACE_HEIGHT / float(config.FACE_WIDTH)) * w)
        midy = int(y + h/2)
        y1 = max(0, int(midy-crop_height/2))
        y2 = min(image.shape[0]-1, midy+int(crop_height/2))
        try:
                return image[y1:y2, x:x+w]
        except:
                pass

def resize(image):
    """Resize a face image to the proper size for training and detection.
    """
    return cv2.resize(image, (config.FACE_WIDTH, config.FACE_HEIGHT), interpolation=cv2.INTER_LANCZOS4)

def detect_single(image):
    """Return bounds (x, y, width, height) of detected face in grayscale image.
       If no face or more than one face are detected, None is returned.
    """
    faces = haar_faces.detectMultiScale(image, 
                scaleFactor=config.HAAR_SCALE_FACTOR, 
                minNeighbors=config.HAAR_MIN_NEIGHBORS, 
                minSize=config.HAAR_MIN_SIZE, 
                flags=cv2.CASCADE_SCALE_IMAGE)
    if len(faces) != 1:
        return None
    return faces[0]

def recognize(tagID):
    print('beginning recognition on %i', (tagID) )

    image = camera.read()
    # Convert image to grayscale.
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    for a in range(10):
        result = detect_single(image)
        if result is None:
                print('Could not detect single face! Trying again... Check the image in capture.pgm')
        else:
            print("Detected a face! Recognizing (this may take a while)...")
            break

    if result is None:
        print('Detection failed.')
        return False

    x, y, w, h = result
    cropped = resize(crop(image, x, y, w, h))
    
    prediction = models[0].predict(cropped)
    print('For user "'+user+'", predicted {0} face.'.format(
                                'POSITIVE' if prediction == config.POSITIVE_LABEL else 'NEGATIVE'))

    return (prediction == config.POSITIVE_LABEL)                    

def subRFID():
    # RFID sbprocess
    readings = 5
    print('rfid started')

    while readings > 0:
        os.chdir(owd)
        rfidproc = subprocess.Popen('python RFID-process.py', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        (output, errors) = rfidproc.communicate()
        readings -= 1
        recognize(output.split(':')[-1])
        time.sleep(1)

    print('thread finished')
    rfidproc.terminate()



try:
    
    RFID_Process = threading.Thread(target=subRFID, name="RFID_PROCESS",)
    RFID_Process.start()

except:
    print('threading error')
    exit(1)