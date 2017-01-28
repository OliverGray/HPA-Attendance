import subprocess

# faceproc = subprocess.Popen(['python3 subprocess-video.py'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            # universal_newlines=True, bufsize=1)

faceproc = subprocess.Popen(['python3 video-process.py'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize = 1 )
#
while faceproc.poll() is None:

    rfid = '1234'

    if rfid is not False:
        print('writing to Face:', rfid)
        faceproc.stdin.write(rfid + '\n')

        print('sucessful write')

        while True:
            face = faceproc.stdout.readline()
            if face != '' and face != '\n':
                print("test:", face.rstrip())
                break

# print('thread finished: ' + FACE_Process.name)