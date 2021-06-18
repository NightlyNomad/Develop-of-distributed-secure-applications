import socket, time, datetime, threading, argparse
import sys
import cv2
import pickle
import numpy as np
import struct
import zlib
from flask_opencv_streamer.streamer import Streamer
from flask import Flask, Response, render_template

app = Flask(__name__)

@app.route("/")
def index():
    # Для визуализации шаблона вы можете использовать метод render_template().
    # Всё, что вам необходимо - это указать имя шаблона, а также переменные в виде именованных аргументов,
    # которые вы хотите передать движку обработки шаблонов:
    return render_template("index.html")

#HOST = '127.0.0.1'
#PORT = 64000

#port1 = 64000
#port2 = 8092
#port3 = 8093
#require_login = False

#streamer1 = Streamer(port1, require_login)
#streamer2 = Streamer(port2, require_login)
#streamer3 = Streamer(port3, require_login)

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#print('Socket created')

#s.bind((HOST, PORT))
#print('Socket bind complete')
#s.listen(10)
#print('Socket now listening')

#conn, addr = s.accept()

def detectPeople(gray):
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(10, 10))
    for (x, y, w, h) in faces:
        cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 255, 0), 2)
        cv2.putText(gray, "Man", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 3, (30, 105, 210), 6)

#def detectCat(gray):
#    face_cascade = cv2.CascadeClassifier('haarcascade_frontalcatface.xml')
#    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(10, 10))
#    for (x, y, w, h) in faces:
#        cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 255, 0), 2)
#        cv2.putText(gray, "Cat", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 3, (30, 105, 210), 6)

data = b""
payload_size = struct.calcsize(">L")
print("payload_size: {}".format(payload_size))
while True:
    while len(data) < payload_size:
        print("Recv: {}".format(len(data)))
        data += conn.recv(4096)

    #print("Done Recv: {}".format(len(data)))
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    #print("msg_size: {}".format(msg_size))
    while len(data) < msg_size:
        data += conn.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    #detectPeople(frame)
    #detectCat(frame)
    streamer1.update_frame(frame)
    #streamer2.update_frame(frame)
    #streamer3.update_frame(frame)

    if not streamer1.is_streaming:
        streamer1.start_streaming()

    #if not streamer2.is_streaming:
    #    streamer2.start_streaming()

    #if not streamer3.is_streaming:
    #    streamer3.start_streaming()
    #cv2.imshow('ImageWindow',frame)
    cv2.waitKey(30)

@app.route("/video_feed")
def video_feed():
    #
    # вернуть сгенерированный ответ вместе с конкретным типом медиа (тип mime)
    return Response(detectPeople(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


#
# проверить, является ли это основным потоком выполнения
if __name__ == '__main__':
    # запустить поток, который будет выполнять обнаружение движения
    t = threading.Thread(target=detect_motion, args=(
        32,))
    t.daemon = True
    t.start()

    # запускаем flask app
    app.run(host="127.0.0.1", port="8080", debug=True,
            threaded=True, use_reloader=False)
