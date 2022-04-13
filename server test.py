import base64
from socket import *
import _thread
import os
import json


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
		body = f.read()
		

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

def portfolio(message):


	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	f = open("Front-End/zippy.html","rb")
	body = f.read()


	return header, body

def jason(message):


	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	f = open("portfolio.json","rb")
	body = f.read()


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

def getPortfolio():

	with open('portfolio.json') as f:
		jase = json.load(f)
	portfolio = jase['portfolio']
	return portfolio

def stockInPortfolio(portfolio_list, new_stock):
	stock_in_portfolio = -1
	for i, current_stock in enumerate(portfolio_list):
		if current_stock["Stock"] == new_stock["Stock"]:
			stock_in_portfolio = i	
	return stock_in_portfolio

def getAveragePrice(current_stock, new_stock):
	
	current_stock_paid = int(current_stock["Price"]) * int(current_stock["Quantity"])
	print(current_stock_paid)
	new_stock_paid = int(new_stock["Price"]) * int(new_stock["Quantity"])
	print(new_stock_paid)
	total_stock_quantity = int(current_stock["Quantity"]) + int(new_stock["Quantity"])
	total_stock_paid = current_stock_paid + new_stock_paid
	average_stock_price = total_stock_paid/total_stock_quantity
	return average_stock_price


#We process client request here. The requested resource in the URL is mapped to a service function which generates the HTTP reponse 
#that is eventually returned to the client. 
def process(connectionSocket) :	
	# Receives the request message from the client
	message = connectionSocket.recv(1024).decode()	
	user = "22011882"
	password = "22011882"
	credentials = "b'" +user + ":" + password + "'"
	
	
	temp = [i.strip() for i in message.splitlines()]
	auth_present = False

	for line in temp:

		if line.split() == []:
			pass

		elif line.split()[0].strip() == "Authorization:":
			decoded_string = base64.b64decode(line.split()[2].strip())
						
			
			if str(decoded_string) == str(credentials):
				auth_present = True


	http_method = message.split()[0]
	
	if http_method == "GET":


		if len(message) > 1:


			# Extract the path of the requested object from the message
			# Because the extracted path of the HTTP request includes
			# a character '/', we read the path from the second character
			resource = message.split()[1][1:]
			
			#map requested resource (contained in the URL) to specific function which generates HTTP response
			if not auth_present:
				print("ITS NAHT")
				responseHeader, responseBody = noAuth(message)

			elif resource == "":
				responseHeader, responseBody = default(message)
			elif resource == "welcome":
				responseHeader,responseBody = welcome(message)
			elif resource == "portfolio":
				responseHeader,responseBody = portfolio(message)
			elif resource == "portfolio.json":
				responseHeader,responseBody = jason(message)
			else:
				responseHeader,responseBody = getFile(resource)
	
	if 	http_method == "POST":

		new_stock = json.loads(message.split()[-1])		
		portfolio_list = getPortfolio()

		stock_index = stockInPortfolio(portfolio_list, new_stock)

		if stock_index > -1:
			portfolio_list[stock_index]["Price"] = getAveragePrice(portfolio_list[stock_index], new_stock)
			portfolio_list[stock_index]["Quantity"] = int(portfolio_list[stock_index]["Quantity"]) + int(new_stock["Quantity"])			
			
		else:
			portfolio_list.append(new_stock)

		with open('portfolio.json') as f:
			jase = json.load(f)	
		
		
		jase['portfolio'] = portfolio_list

		with open('portfolio.json', 'w') as outfile:
			outfile.write(json.dumps(jase))


		responseHeader,responseBody = portfolio(message)
		
	
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




