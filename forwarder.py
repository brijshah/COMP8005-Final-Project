#!/usr/bin/python
import threading, socket, sys, select

CFG_NAME = "rules.conf"
ROUTES = []
THREADS = []
HOST = "127.0.0.1"
BUF_SIZE = 1024

class ProxyServer:
	def __init__(self, connport, destip, destport):
		self.connport = connport
		self.destip = destip
		self.destport = destport
		self.clients = []

		print "Starting server on %s port %s" % (HOST, self.connport)
		self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.srv_socket.bind((HOST, self.connport))
		self.srv_socket.listen(5)

	def handle_accept(self):
		try:
			self.clients = [self.srv_socket]
			while True:
				readList, writeList, exceptions = select.select(self.clients, [], [])
				# For each socket ready to be read
				for socket in readList:
					# Ready to accept another client
					if socket == self.srv_socket:
						try:
							conn, address = socket.accept()
							conn.setblocking(0)
							self.clients.append(conn)
						except socket.error:
							self.clients.remove(socket)
					elif socket in self.clients:
						data = socket.recv(1024)
						if data == "":
							self.clients.remove(socket)
							print "%s has disconnected" % socket.getpeername()[1]
							socket.close()
						else:
							print "%s: %s" % (socket.getpeername(), data)
							self.dest_socket.sendall(data)
		finally:
			self.terminate_connection()

	def terminate_connection(self):
		for sockets in self.clients:
			sockets.close()
		self.srv_socket.close()
		self.dest_socket.close()

	def check_destination(self):
		print "Checking if %s:%s is available..." % (self.destip, self.destport)
		self.dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.dest_socket.connect((self.destip, self.destport))
		except socket.error:
			print "\tCould not connect to destination server..."
			return
		print "\tConnected to %s:%s" % (self.destip, self.destport)

	# def handle_forward(self, from_sock, to_sock):
	# 	data = from_sock.recv(BUF_SIZE)
	# 	if data == "":
	# 		print "Source connection disconnected"
	# 		raise socket.error
	# 	else:
	# 		print data
	# 		to_sock.sendall(data)

def parse_config():
	for line in file(CFG_NAME):
		parts = line.split()
		ROUTES.append(ProxyServer(int(parts[1]), parts[2], int(parts[3])))

def main():
	# Create config file if it doesn't exist
	# Parse config file

	parse_config()

	for route in ROUTES:
		route_thread = threading.Thread(target=route.handle_accept)
		THREADS.append(route_thread)
		route_thread.daemon = True
		route_thread.start()
	while True:
		pass

if __name__ == '__main__':
	try:
		main()
	finally:
		print "\nExiting..."