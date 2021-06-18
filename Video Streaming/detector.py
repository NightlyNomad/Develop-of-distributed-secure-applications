import cv2
import io
import socket
import struct
import time
import pickle
import zlib


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('', 64000))
connection = client_socket.makefile('wb')



cam = cv2.VideoCapture(0)

cam.set(3, 360);
cam.set(4, 360);

img_counter = 0

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
while True:
    ret, im = cam.read()
    result, im = cv2.imencode('.jpg', im, encode_param)
    data = pickle.dumps(im, 0)
    size = len(data)
    #print("{}: {}".format(img_counter, size))
    client_socket.sendall(struct.pack(">L", size) + data)
    img_counter += 1

cam.release()