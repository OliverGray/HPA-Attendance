#!/usr/bin/env python

try:
    import subprocess
    import threading
    import cv2
    import sys
    import time
    import os
    import datetime
    import config
    import MySQLdb as mysql

except:
    print("initialization error")
    exit(1)


output = ''
db = mysql.connect(host="localhost",user="monitor",passwd="raspberry",db="Attendance")
cur = db.cursor()
camera = config.get_camera()
haar_faces = cv2.CascadeClassifier(config.HAAR_FACES)
owd = os.getcwd()

# make this iterative
cur.execute("SELECT * FROM users;")
data = cur.fetchall()
usernames = [row[2] for row in data]
users = []
for user in usernames:
    us = user.split(", ")
    users.append(us[1].lower()+"_"+us[0].lower())
   
cards = [str(row[1]) for row in data]

models = [cv2.face.createEigenFaceRecognizer() for user in users]
for model in models:
    os.chdir(config.POSITIVE_DIR+"/"+user)
    model.load(config.TRAINING_FILE)
    os.chdir(owd)

identities = zip(users,cards,models)
for i in identities:
    print i
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
    print 'beginning recognition on '+tagID

    usident = None

    for ident in identities:
        if tagID == ident[1]:
            usident = ident
            print 'user accepted as',usident
            break
        else:
            print tagID,ident[1]

    if usident is not None:
        image = camera.read()
        # Convert image to grayscale.
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        for a in range(10):
            result = detect_single(image)
            if result is None:
                print('Could not detect single face! Trying again... Check the image in capture.pgm')
                image = camera.read()
                # Convert image to grayscale.
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                print("Detected a face! Recognizing (this may take a while)...")
                break

        if result is None:
            print('Detection failed.')
            return False

        x, y, w, h = result
        cropped = resize(crop(image, x, y, w, h))
        
    ##    print('For user "'+user+'", predicted {0} face.'.format(
    ##                                'POSITIVE' if prediction == config.POSITIVE_LABEL else 'NEGATIVE'))

        return (usident[2].predict(cropped) == config.POSITIVE_LABEL)               

    else:
        return False


def subRFID():
    # RFID sbprocess
    readings = 2
    print('rfid started')

    while readings > 0:
        os.chdir(owd)
        rfidproc = subprocess.Popen('python RFID-process.py', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        (output, errors) = rfidproc.communicate()
        readings -= 1
        
        card_id = output.split(':')[-1][:-1]
        if recognize(card_id):
            query = 'INSERT into log (card_id, time_stamp) VALUES ("'+card_id+'", NOW());'
            print query
            cur.execute(query)
            db.commit()
            
        time.sleep(1)

    db.close()
    print('thread finished')
    rfidproc.terminate()



try:
    
    RFID_Process = threading.Thread(target=subRFID, name="RFID_PROCESS",)
    RFID_Process.start()

except:
    print('threading error')
    db.close()
    exit(1)