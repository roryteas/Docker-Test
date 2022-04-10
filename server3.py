#Author: Sunil Lal

#This is a simple HTTP server which listens on port 8080, accepts connection request, and processes the client request 
#in sepearte threads. It implements basic service functions (methods) which generate HTTP response to service the HTTP requests. 
#Currently there are 3 service functions; default, welcome and getFile. The process function maps the requet URL pattern to the service function.
#When the requested resource in the URL is empty, the default function is called which currently invokes the welcome function.
#The welcome service function responds with a simple HTTP response: "Welcome to my homepage".
#The getFile service function fetches the requested html or img file and generates an HTTP response containing the file contents and appropriate headers.

#To extend this server's functionality, define your service function(s), and map it to suitable URL pattern in the process function.

#This web server runs on python v3
#Usage: execute this program, open your browser (preferably chrome) and type http://servername:8080
#e.g. if server.py and broswer are running on the same machine, then use http://localhost:8080

import base64
from socket import *
import _thread


serverSocket = socket(AF_INET, SOCK_STREAM)

serverPort = 8080
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(("0.0.0.0", serverPort))

serverSocket.listen(5)
print('The server is running')	
# Server should be up and running and listening to the incoming connections

#Extract the given header value from the HTTP request message
def getHeader(message, header):


	if message.find(header) > -1:
		value = message.split(header)[1].split()[0]
	else:
		value = None

	return value

#service function to fetch the requested file, and send the contents back to the client in a HTTP response.
def getFile(filename):

	try:

		# open and read the file contents. This becomes the body of the HTTP response
		f = open(filename, "rb")
		
		print(f)

		body = f.read()
		print(body)

		header = ("HTTP/1.1 200 OK\r\n\r\n").encode()

	except IOError:

		# Send HTTP response message for resource not found
		header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
		body = "<html><head></head><body><h1>404 Not Fround</h1></body></html>\r\n".encode()

	return header, body

#service function to generate HTTP response with a simple welcome message
def welcome(message):


	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	body = ("<html><head></head><body><h1>Welcome to my homepage</h1></body></html>\r\n").encode()


	return header, body
def noAuth(message):

	header = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic\r\n\r\n".encode()
	print(header)
	body = "<html><body>Sorry bucko</body></html>".encode()
	return header, body

#default service function
def default(message):

	header, body = welcome(message)

	return header, body


#We process client request here. The requested resource in the URL is mapped to a service function which generates the HTTP reponse 
#that is eventually returned to the client. 
def process(connectionSocket) :	
	# Receives the request message from the client
	message = connectionSocket.recv(1024).decode()

	user = "gim"
	password = "gim"
	credentials = "b'" +user + ":" + password + "'"
	print(credentials)
	
	temp = [i.strip() for i in message.splitlines()]
	auth_present = False

	for line in temp:

		if line.split() == []:
			pass

		elif line.split()[0].strip() == "Authorization:":
			decoded_string = base64.b64decode(line.split()[2].strip())
						
			
			if str(decoded_string) == str(credentials):
				auth_present = True




	if len(message) > 1:



		# Extract the path of the requested object from the message
		# Because the extracted path of the HTTP request includes
		# a character '/', we read the path from the second character
		resource = message.split()[1][1:]
		print(resource)
		#map requested resource (contained in the URL) to specific function which generates HTTP response
		if not auth_present:
			print("ITS NAHT")
			responseHeader, responseBody = noAuth(message)

		elif resource == "":
			responseHeader, responseBody = default(message)
		elif resource == "welcome":
			responseHeader,responseBody = welcome(message)
		else:
			responseHeader,responseBody = getFile(resource)

	connectionSocket.send(responseHeader)
	connectionSocket.send(responseBody)
	connectionSocket.close()

	# Send the HTTP response header line to the connection socket

	# Send the content of the HTTP body (e.g. requested file) to the connection socket

	# Close the client connection socket



#Main web server loop. It simply accepts TCP connections, and get the request processed in seperate threads.
while True:
	
	# Set up a new connection from the client
	connectionSocket, addr = serverSocket.accept()
	#Clients timeout after 60 seconds of inactivity and must reconnect.
	connectionSocket.settimeout(60)
	# start new thread to handle incoming request
	_thread.start_new_thread(process,(connectionSocket,))





