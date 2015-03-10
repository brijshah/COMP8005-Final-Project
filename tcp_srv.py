import socket, sys
SERVER_IP = ""
SERVER_PORT = 0
BUF_SIZE = 1024

def main():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((SERVER_IP, SERVER_PORT))
	server.listen(5)

	while True:
		client, client_addr = server.accept()
		data = client.recv(1024)
		print data

if __name__ == '__main__':
	if(len(sys.argv) is not 3):
		print "Please use the following format:"
		print "\tpython tcp_srv.py [SERVER IP] [SERVER PORT]"
		sys.exit()
	else:
		SERVER_IP = sys.argv[1]
		SERVER_PORT = sys.argv[2]

	main()