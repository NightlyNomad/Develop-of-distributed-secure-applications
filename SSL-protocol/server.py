import socket
import ssl
from PIL import Image
import numpy as np
import io

mask = np.array([[1, 1, 0, 1, 1],
                 [1, 2, 1, 2, 1],
                 [0, 1, 3, 1, 0],
                 [1, 2, 1, 2, 1],
                 [1, 1, 0, 1, 1]])


def get_indexes(mask: np.ndarray):
    ravel = mask.ravel()
    index = np.array([])
    for i, val in enumerate(ravel):
        index = np.append(index, np.array([i] * val))
    return index.astype(np.int32)


def rank_filter(pixels: np.ndarray, mask: np.ndarray, rank: int):
    h, w = pixels.shape
    hm = mask.shape[0] // 2
    wm = mask.shape[1] // 2
    res = np.zeros_like(pixels)
    index = get_indexes(mask)
    for i in range(hm, h - hm):
        for j in range(wm, w - hm):
            frame = pixels[i - hm: i + hm + 1, j - wm: j + wm + 1]
            ravel = frame.ravel()
            sorted_array = np.sort(ravel[index])
            res[i, j] = sorted_array[rank]
    return res


def rank_by_channel(image: np.ndarray, mask: np.ndarray, rank: int):
    res = np.zeros_like(image)
    for i in range(3):
        res[:, :, i] = rank_filter(image[:, :, i], mask, rank)
    return res


def bytesToRGB(img_bytes):
    image = Image.open(io.BytesIO(img_bytes))
    return np.array(image)


def recvall(sock, count):
    data = bytearray()
    while len(data) < count:
        pack = sock.recv(count - len(data))
        print('recieved {0} bytes'.format(len(pack)))
        if not pack:
            return None
        data.extend(pack)
    return data


listen_addr = 'localhost'
listen_port = 9092
server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

bindsocket = socket.socket()
bindsocket.bind((listen_addr, listen_port))
bindsocket.listen(5)

print("Waiting for client")
newsocket, fromaddr = bindsocket.accept()
print("Accepted")
conn = context.wrap_socket(newsocket, server_side=True)
# img_file_len = conn.recv(100)

img_file_len = recvall(conn, 8)
a = int.from_bytes(img_file_len, byteorder='big', signed=False)

img_data = recvall(conn, a)
conn.settimeout(1)

img_np = bytesToRGB(img_data)
res_med = rank_by_channel(img_np, mask, 15)

im = Image.fromarray(res_med)
buf = io.BytesIO()
im.save(buf, format='JPEG')
byte_im = buf.getvalue()

img_file = open('recieved_image_with_filter_ssl.jpg', 'wb')
img_file.write(byte_im)
img_file.close()

img_file = open('recieved_image_ssl.jpg', 'wb')
img_file.write(img_data)
img_file.close()

conn.shutdown(socket.SHUT_RDWR)
conn.close()

img = Image.open('recieved_image_with_filter_ssl.jpg')
img.show()
