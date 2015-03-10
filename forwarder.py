#!/usr/bin/python
import threading, socket

CFG_NAME = "forward.conf"
ROUTES = []
THREADS = []
HOST = "127.0.0.1"

class Route:
	def __init__(self, connport, destip, destport):
		self.connport = connport
		self.destip = destip
		self.destport = destport

def print_route_info(route):
	print "Forwarding connection from %s to %s:%s" % (route.connport, route.destip, route.destport)

def init_routes():
	for line in file(CFG_NAME):
		parts = line.split()
		ROUTES.append(Route(int(parts[0]), parts[1], int(parts[2])))

def create_host(route):
	print "Starting server on %s port %s" % (HOST, route.connport)
	route_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	route_socket.bind((HOST, route.connport))
	route_socket.listen(5)

	while True:
		client_sock = route_socket.accept()[0]
		temp = client_sock.recv(1024)
		print temp
		# dest_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# dest_sock.connect(route.destip, route.destport)

def main():
	# Create config file if it doesn't exist
	# Parse config file
	init_routes()
	for route in ROUTES:
		print_route_info(route)
		route_thread = threading.Timer(0.0, create_host, args=(route,))
		THREADS.append(route_thread)
		route_thread.start()

	while True:
		pass
	# for threads in THREADS:
		# create_host(route)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		print "\nExiting..."
		# for threads in THREADS:
			# threads.cancel()