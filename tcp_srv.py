#!/usr/bin/python

#-----------------------------------------------------------------------------
#--	SOURCE FILE:	tcp_srv.py -   Simple TCP echo server
#--
#--	FUNCTIONS:		accept_echo(client)
#--					main					
#--
#--	DATE:			March 14, 2015
#--
#--	DESIGNERS:		David Wang
#--
#--	PROGRAMMERS:	David Wang
#--
#--	NOTES:
#--	
#-----------------------------------------------------------------------------

import socket, sys, threading

#Global Variables
SERVER_IP = ""
SERVER_PORT = 0
BUF_SIZE = 1024

#-----------------------------------------------------------------------------
#-- FUNCTION:       accept_echo(client)
#--
#-- VARIABLES(S):   client - 
#--
#-- NOTES:
#-- 
#-----------------------------------------------------------------------------
def accept_echo(client):
	while True:
		data = client.recv(BUF_SIZE)
		if data == "":
			print "Client disconnected"
			break
		else:
			client.sendall(data)
	client.close()

#-----------------------------------------------------------------------------
#-- FUNCTION:       main 
#--
#-- NOTES:
#-- 
#-----------------------------------------------------------------------------
def main():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((SERVER_IP, SERVER_PORT))
	server.listen(5)

	while True:
		client, client_addr = server.accept()
		threading.Thread(target=accept_echo, args=[client,]).start()

if __name__ == '__main__':
	if(len(sys.argv) is not 3):
		print "Please use the following format:"
		print "\tpython tcp_srv.py [SERVER IP] [SERVER PORT]"
		sys.exit()
	else:
		SERVER_IP = sys.argv[1]
		SERVER_PORT = int(sys.argv[2])

	main()
