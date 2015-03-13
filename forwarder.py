#!/usr/bin/python
import threading, socket, sys, select

CFG_NAME = "rules.conf"
ROUTES = {}
THREADS = []
HOST = ""
BUF_SIZE = 2048

class ProxyServer:

	def __init__(self, port):
		self.port = port
		self.clients = []
		self.destinations = {}
		self.connected_paths = []

		print "Starting server on %s port %s" % (HOST, self.port)
		self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.srv_socket.bind((HOST, port))
		self.srv_socket.listen(5)

	def handle_accept(self):
		self.clients = [self.srv_socket]
		while True:
			readList, writeList, exceptions = select.select(self.clients, [], [])
			# For each socket ready to be read
			for sockets in readList:
				# Ready to accept another client
				if sockets == self.srv_socket:
					try:
						conn, address = sockets.accept()
						for path in ROUTES[self.port]:
							if path[0] == address[0]:
								self.destinations[conn] = self.connect_dest(path[1], path[2])
								if self.destinations[conn] is False:
									conn.close()
									break
								conn.setblocking(0)
								self.clients.append(conn)
								self.clients.append(self.destinations[conn])
								self.connected_paths.append(Connected_Route(conn, self.destinations[conn]))
								break
					except socket.error:
						self.clients.remove(sockets)
				else:
					# Determine where to forward to
					for conn_sock in self.connected_paths:
						if sockets == conn_sock.src:
							self.forward_data(sockets, conn_sock.dest)
							break
						elif sockets == conn_sock.dest:
							self.forward_data(sockets, conn_sock.src)
							break

	def connect_dest(self, dest_ip, dest_port):
		print "Checking if %s:%s is available..." % (dest_ip, dest_port)
		dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			dest_socket.connect((dest_ip, dest_port))
		except socket.error:
			print "\tCould not connect to destination server..."
			return False
		print "\tConnected to %s:%s" % (dest_ip, dest_port)
		return dest_socket

	def forward_data(self, src_socket, dest_socket):
		data = src_socket.recv(BUF_SIZE)
		socket_info = src_socket.getpeername()
		# print "Received %s from %s" % (data, socket_info)
		if data == "":
			print "%s:%s has disconnected" % socket_info
			self.terminate_connection(Connected_Route(src_socket, dest_socket))
			return
		try:
			dest_socket.send(data)
		except IOError:
			print "Destination unavailable, disconnecting sockets"
			self.terminate_connection(Connected_Route(src_socket, dest_socket))

	def terminate_connection(self, path_sockets):
		source = path_sockets.src
		destination = path_sockets.src
		try:
			self.clients.remove(source)
			self.clients.remove(destination)
			self.destinations.remove(source)
			self.connected_paths.remove(path_sockets)
		except ValueError:
			pass
		source.close()
		destination.close()

class Connected_Route():
	def __init__(self, src_socket, dest_socket):
		self.src = src_socket
		self.dest = dest_socket

def parse_config():
	for line in file(CFG_NAME):
		parts = line.split()
		route_data = [parts[0], parts[2], int(parts[3])]
		try:
			ROUTES[int(parts[1])].append([parts[0], parts[2], int(parts[3])])
		except KeyError:
			ROUTES[int(parts[1])] = [route_data]

def main():
	# Create config file if it doesn't exist
	# Parse config file
	parse_config()

	for port, emptyVar in ROUTES.iteritems():
		route = ProxyServer(int(port))
		route_thread = threading.Thread(target=route.handle_accept)
		THREADS.append(route_thread)
		# Run threads as daemons
		route_thread.daemon = True
		route_thread.start()
	while True:
		pass

if __name__ == '__main__':
	try:
		main()
	finally:
		print "\nExiting..."