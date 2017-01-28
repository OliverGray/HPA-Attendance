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
    import MySQLdb as mysql

except:
    print("initialization error")
    exit(1)


output = ''
db = mysql.connect(host="localhost",user="monitor",passwd="raspberry",db="Attendance")
cur = db.cursor()
##camera = config.get_camera()
##haar_faces = cv2.CascadeClassifier(config.HAAR_FACES)
owd = os.getcwd()

# make this iterative
cur.execute("SELECT * FROM users;")
data = cur.fetchall()
usernames = [row[2] for row in data]
users = []
for user in usernames:
    us = user.split(", ")
    users.append(us[1].lower()+"_"+us[0].lower())
    
cards = [row[1] for row in data]

##models = [cv2.face.createEigenFaceRecognizer()]


##os.chdir(config.POSITIVE_DIR+"/"+user)
##for model in models:
##    model.load(config.TRAINING_FILE)

run = True

zipped = zip(users,cards)

card_id = '4c0094beff'

print (card_id in zipped[0])

query = '''INSERT into log (card_id, time_stamp) VALUES ("4c0094beff", NOW());'''


cur.execute(query)
con.commit()

print query
db.close()