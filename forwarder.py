#!/usr/bin/python
import threading, socket, sys, select

CFG_NAME = "rules.conf"
ROUTES = {}
THREADS = []
HOST = "127.0.0.1"
BUF_SIZE = 1024

class ProxyServer:

	def __init__(self, port):
		self.port = port
		self.destinations = {}

		print "Starting server on %s port %s" % (HOST, self.port)
		self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.srv_socket.bind((HOST, port))
		self.srv_socket.listen(5)

	# def __init__(self, connip, connport, destip, destport):
	# 	self.connip = connip
	# 	self.connport = connport
	# 	self.destip = destip
	# 	self.destport = destport
	# 	self.clients = []

	# 	print "Starting server on %s port %s" % (HOST, self.connport)
	# 	self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 	self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# 	self.srv_socket.bind((HOST, self.connport))
	# 	self.srv_socket.listen(5)
	# 	self.check_destination()

	def handle_accept(self):
		try:
			clients = [self.srv_socket]
			while True:
				readList, writeList, exceptions = select.select(clients, [], [])
				# For each socket ready to be read
				for sockets in readList:
					# Ready to accept another client
					if sockets == self.srv_socket:
						try:
							conn, address = sockets.accept()
							conn.setblocking(0)
							clients.append(conn)
							for path in ROUTES[self.port]:
								if path[0] == address[0]:
									self.destinations[conn] = self.connect_dest(path[1], path[2])
						except socket.error:
							clients.remove(sockets)
					elif sockets in clients:
						data = sockets.recv(1024)
						if data == "":
							clients.remove(sockets)
							print "%s has disconnected" % sockets.getpeername()[1]
							sockets.close()
						else:
							# Determine where to forward to
							for path in ROUTES[self.port]:
								if sockets.getpeername()[0] == path[0]:
									print "%s: %s" % (sockets.getpeername(), data)
									self.destinations[sockets].sendall(data)
		finally:
			# self.terminate_connection()
			pass

	def terminate_connection(self):
		for sockets in self.clients:
			sockets.close()
		self.srv_socket.close()
		self.dest_socket.close()

	def connect_dest(self, dest_ip, dest_port):
		print "Checking if %s:%s is available..." % (dest_ip, dest_port)
		dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			dest_socket.connect((dest_ip, dest_port))
		except socket.error:
			print "\tCould not connect to destination server..."
			return
		print "\tConnected to %s:%s" % (dest_ip, dest_port)

		return dest_socket

	# def check_destination(self):
	# 	print "Checking if %s:%s is available..." % (self.destip, self.destport)
	# 	self.dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 	try:
	# 		self.dest_socket.connect((self.destip, self.destport))
	# 	except socket.error:
	# 		print "\tCould not connect to destination server..."
	# 		return
	# 	print "\tConnected to %s:%s" % (self.destip, self.destport)

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
		route_data = [parts[0], parts[2], int(parts[3])]
		try:
			ROUTES[int(parts[1])].append([parts[0], parts[2], int(parts[3])])
		except KeyError:
			ROUTES[int(parts[1])] = [route_data]
		# ROUTES.append(ProxyServer(int(parts[0], int(parts[1]), parts[2], int(parts[3])))

def main():
	# Create config file if it doesn't exist
	# Parse config file

	parse_config()

	for port, emptyVar in ROUTES.iteritems():
		route = ProxyServer(int(port))
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