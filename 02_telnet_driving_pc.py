import socket
import struct
import numpy as np
import cv2
import pickle
import time

HOST_RPI = '192.168.137.246'
PORT = 8089

client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_mot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_cam.connect((HOST_RPI, PORT))
client_mot.connect((HOST_RPI, PORT))

t_now = time.time()
t_prev = time.time()
cnt_frame = 0

while True:

	# 센서 읽어, 영상 보내
	cmd = 12
	cmd_byte = struct.pack('!B', cmd)
	client_cam.sendall(cmd_byte)

	# 센서값 받기
	rl_byte = client_cam.recv(1)
	rl = struct.unpack('!B', rl_byte)

	right, left = (rl[0] & 2)>>1, rl[0] & 1
	# print(right, left)

	# 영상 받기
	data_len_bytes = client_cam.recv(4)
	data_len = struct.unpack('!L', data_len_bytes)

	frame_data = client_cam.recv(data_len[0], socket.MSG_WAITALL)

	# Extract frame
	frame = pickle.loads(frame_data)

	# 영상 출력
	np_data = np.frombuffer(frame, dtype='uint8')
	frame = cv2.imdecode(np_data,1)
	frame = cv2.rotate(frame, cv2.ROTATE_180)
	frame2 = cv2.resize(frame, (320, 240))
	cv2.imshow('frame', frame2)

	# 자동차 주행
	cmd = int(rl[0]) #34
	cmd = struct.pack('!B', cmd)
	client_mot.sendall(cmd)

	key = cv2.waitKey(1)
	if key == 27:
		break

	cnt_frame += 1
	t_now = time.time()
	if t_now - t_prev >= 1.0 :
		t_prev = t_now
		print("frame count : %f" %cnt_frame)
		cnt_frame = 0

client_cam.close()
client_mot.close()