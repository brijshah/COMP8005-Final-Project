#!/usr/bin/python
#-------------------------------------------------------------------------------
#--	SOURCE FILE:	forwarder.py -   Python Proxy Server(Port Forwarder)
#--
#--	CLASSES:		ProxyServer
#--					Connected_Route
#--
#--	FUNCTIONS:		ProxyServer:
#--						handle_accept()
#--						connect_dest(destp_ip, dest_port)
#--						forward_data(src_socket, dest_socket)
#--						terminate_connection(path_sockets)
#--					parse_config()
#--					main()
#--
#--	DATE:			March 14, 2015
#--
#--	PROGRAMMERS:	David Wang
#--					Brij Shah
#--
#--	NOTES:			A simple port forwarder created in Python 2.7. This program
#--					reads from a configuration file and forwards data from one
#--					IP:PORT pair to another IP:PORT. The program supports
#--					multiple inbound connection requests as well as simutaneous
#--					two-way traffic.
#--
#-------------------------------------------------------------------------------

import threading, socket, sys, select

#Global Variables
ROUTES = {}
THREADS = []
HOST = ""
BUF_SIZE = 2048

#Configuration File
CFG_NAME = "rules.conf"

#-------------------------------------------------------------------------------
#-- CLASS:       	ProxyServer
#--
#-- FUNCTIONS:		handle_accept(self)
#--					connect_dest(self, destp_ip, dest_port)
#--					forward_data(self, src_socket, dest_socket)
#--					terminate_connection(self, path_sockets)
#--
#-- NOTES:			A representation of a port forwarding that sends and
#--					receives data on a specific port.
#-------------------------------------------------------------------------------
class ProxyServer:

	# Initialize a ProxyServer class and create a server on the port
	def __init__(self, port):
		self.port = port # The port the server is running
		self.clients = [] # List of clients
		self.connected_paths = [] # List of connected paths

		print "Starting server on port %s" % self.port
		self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.srv_socket.bind((HOST, port))
		self.srv_socket.listen(5)

	#---------------------------------------------------------------------------
	#-- FUNCTION:       handle_accept()
	#--
	#-- NOTES:			The main connecting/forwarding portion of the program.
	#--					It uses Select to handle I/O events on various sockets
	#--					including server and multiple client sockets.
	#--
	#--					When accepting a new connection, the program checks to
	#--					see if it the IP to this port is part of any forwarding
	#--					rule. If not, the connection is terminated. If it is,
	#--					the program then checks if the destination host is
	#--					active. If not, the connection is terminated. If it is,
	#--					the connection and its destination are both added to
	#--					select's client list for processing.
	#--
	#--					When forwarding data, the program determines whether the
	#--					socket is a destionation or a source, and forwards the
	#--					data accordingly.
	#---------------------------------------------------------------------------
	def handle_accept(self):
		self.clients = [self.srv_socket]
		while True:
			readList, writeList, exceptions = select.select(self.clients,[],[])
			# For each socket ready to be read
			for sockets in readList:
				# Ready to accept another client
				if sockets == self.srv_socket:
					# Accept the connection
					conn, address = sockets.accept()
					# Determine if it needs to be forwarded
					for path in ROUTES[self.port]:
						# If it's part of a forwarding rule
						if path[0] == address[0] or path[0] == "*":
							# Check if destination is alive
							destination_sock = self.connect_dest(path[1], path[2])
							if destination_sock is False:
								# Close connection if destination is dead
								conn.close()
								break
							conn.setblocking(0)
							self.clients.append(conn) # append connection
							self.clients.append(destination_sock) # append destination of conn
							# Create a connected_route object for the connection and destination
							self.connected_paths.append(Connected_Route(conn, destination_sock))
							break
					# If it doesn't match any forwarding rule
					conn.close()
				else:
					# Determine where to forward data
					for conn_sock in self.connected_paths:
						# If it's the source socket
						if sockets == conn_sock.src:
							# Send to destinatin
							self.forward_data(sockets, conn_sock.dest)
							break
						# If it's the destination socket
						elif sockets == conn_sock.dest:
							# send to source
							self.forward_data(sockets, conn_sock.src)
							break

	#---------------------------------------------------------------------------
	#-- FUNCTION:       connect_dest(self, dest_ip, dest_port)
	#--
	#-- VARIABLES(S):   dest_ip - IP of the destionation
	#--					dest_port - Port of the destionation
	#--
	#-- NOTES:			Attempts to connect to the specified IP and PORT, if
	#--					it succeeds, return the socket of the connection. If it
	#--					fails (socket error), return False
	#---------------------------------------------------------------------------
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

	#---------------------------------------------------------------------------
	#-- FUNCTION:       forward_data(self, src_socket, dest_socket)
	#--
	#-- VARIABLES(S):   src_socket - socket to receive data from
	#--					dest_socket - socket to send data to
	#--
	#-- NOTES:			The actual forwarding of data. This function receives
	#--					data from the source socket and forwards it to the
	#--					destionation socket. The connections are terminated when
	#--					a null character is received or when an IOError occurs
	#--					during send (destionation unavailable)
	#---------------------------------------------------------------------------
	def forward_data(self, src_socket, dest_socket):
		data = src_socket.recv(BUF_SIZE)
		socket_info = src_socket.getpeername()
		# print "Received %s from %s" % (data, socket_info)
		if data == "":
			self.terminate_connection(Connected_Route(src_socket, dest_socket))
			return
		try:
			dest_socket.send(data)
		except IOError:
			print "Destination unavailable, disconnecting"
			self.terminate_connection(Connected_Route(src_socket, dest_socket))

	#---------------------------------------------------------------------------
	#-- FUNCTION:       terminate_connection(self, path_sockets)
	#--
	#-- VARIABLES(S):   path_sockets - a Connected_Route class object
	#--
	#-- NOTES:			Attempts to terminate the connection on a connected route
	#--					if any clients cannot be removed, the exception is
	#--					simply ignored. The source and destionation sockets are
	#--					then closed afterwards.
	#---------------------------------------------------------------------------
	def terminate_connection(self, path_sockets):
		source = path_sockets.src
		destination = path_sockets.dest
		try:
			self.clients.remove(source)
			self.clients.remove(destination)
			self.destinations.remove(source)
			self.connected_paths.remove(path_sockets)
		except ValueError:
			pass
		source.close()
		destination.close()

#-------------------------------------------------------------------------------
#-- CLASS:       	Connected_Route
#--
#-- NOTES:			A Class that represents a connected forwarding path
#--					Each class contains two sockets representing the source
#--					and destination socket
#--
#--					For future considerations, this class is unncessary, and
#--					should be replaced with a dictionary or an array of tuples
#-------------------------------------------------------------------------------
class Connected_Route():
	def __init__(self, src_socket, dest_socket):
		self.src = src_socket
		self.dest = dest_socket

#-------------------------------------------------------------------------------
#-- FUNCTION:       parse_config()
#--
#-- NOTES:			Parses the configuration file for forwarding rules
#--					It is assumed that the forwarding rules are formatted
#--					correctly in the following order:
#--
#--					SOURCE_IP SOURCE_PORT DESTIONATION_IP DESTIONATION_PORT
#--
#--					Each forwarding rule should be on a seperate line.
#--					The rules are then added to a global "ROUTES" dictionary.
#-------------------------------------------------------------------------------
def parse_config():
	for line in file(CFG_NAME):
		parts = line.split()
		route_data = [parts[0], parts[2], int(parts[3])]
		try:
			ROUTES[int(parts[1])].append(route_data)
		except KeyError:
			ROUTES[int(parts[1])] = [route_data]

#-------------------------------------------------------------------------------
#-- FUNCTION:       main()
#--
#-- NOTES:			Main function of the program
#--					Parses the configuration file and creates a new server on
#--					a new thread. Then loops forever.
#-------------------------------------------------------------------------------
def main():
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
