# This code is for the server 
import socket, cv2, pickle,struct,imutils
from quick_capture_module import StreamCamera
# Socket Create
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_name  = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
#print('HOST IP:',host_ip)
port = 9999
socket_address = (host_ip,port)

# Socket Bind
server_socket.bind(socket_address)

# Socket Listen
server_socket.listen(2)
print("LISTENING AT:",socket_address)

# Socket Accept
client_socket, addr = server_socket.accept()
while True:
	
	print('GOT CONNECTION FROM:',addr)
	if client_socket:
		#vid = StreamCamera()
		
		while(stream.isOpened()):
			try:
				frame = vid.capture()
				#frame = imutils.resize(frame,width=320)
				a = pickle.dumps(frame)
				message = struct.pack("Q",len(a))+a
				client_socket.sendall(message)
				
				#cv2.imshow('TRANSMITTING VIDEO',frame)
				#if cv2.waitKey(1) == '13':
			except KeyboardInterrupt:
				break
		
		print("Shutting down...")
		client_socket.close()