import socket,cv2, pickle,struct ,numpy as np

# create socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
bind_ip = '' 
port = 9999
client_socket.bind(('',port))
#client_socket.setblocking(0)
while True:
	print("entered loop")
	data, addr = client_socket.recvfrom(50000)
	print("got data")
	np_array = np.fromstring(data, dtype=np.uint8)
	image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
	cv2.imshow('Robot vision', image)
	try:
		pass
	except KeyboardInterrupt:
		break

client_socket.close()