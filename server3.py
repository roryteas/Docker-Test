import base64
from pickletools import decimalnl_long
import sys
from socket import *
import _thread
import os
import json
from tabnanny import check
import pycurl
import time
from io import BytesIO
from sqlalchemy import true	


serverSocket = socket(AF_INET, SOCK_STREAM)
#serverPort = 8080

token = 'Tpk_71a0b285c4124025a57ecccd7c43a511'
serverPort = int(os.environ.get('PORT', 17995))

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



#retrieves list of common stock from endpoint and returns list of stock symbols
def getTickerList():
	
	
	response_buffer = BytesIO()
	curl = pycurl.Curl()	#Set the curl options which specify the Google API server, the parameters to be passed to the API,
	# and buffer to hold the response
	curl.setopt(pycurl.CONNECTTIMEOUT, 60)
	curl.setopt(curl.SSL_VERIFYPEER, False)
	curl.setopt(curl.URL, 'https://sandbox.iexapis.com/stable/ref-data/symbols?token='+token)
	
	curl.setopt(curl.WRITEFUNCTION, response_buffer.write)

	curl.perform()
	curl.close()

	body = response_buffer.getvalue()

	json_body = json.loads(body)	
	cs_tlist = []
	for security in json_body:
		if security["type"] == "cs":
			cs_tlist.append(security["symbol"])


	return cs_tlist

#loads portfolio page
def portfolio(message):


	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	f = open("Front-End/portfolio.html","rb")
	body = f.read()


	return header, body

#loads research page
def research(message):


	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	f = open("Front-End/research.html","rb")
	body = f.read()


	return header, body

#takes 
def gainloss(body):

	stockList = []
	for stock in body["portfolio"]:
		stockList.append(stock["Stock"])
	priceList = getStockQuotes(stockList)
	for i, stock in enumerate(body["portfolio"]):
		quote = priceList[i]
		gain_Loss = (float(quote) - float(body["portfolio"][i]["Price"]))
		
		decimal_Gain_Loss = gain_Loss / float(body["portfolio"][i]["Price"])
		
		perent_Gain_Loss = decimal_Gain_Loss * 100

		body["portfolio"][i]["Gain/Loss"] = perent_Gain_Loss
	return body

#sends portfolio data to client
def jason():


	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	f = open("portfolio.json")	
	body = json.load(f)
	body = gainloss(body)
	body = json.dumps(body)
	body = body.encode()
	

	return header, body
#if authorisation fails sends HTML to client
def noAuth():

	header = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic\r\n\r\n".encode()
	
	body = "<html><body>Access Denied</body></html>".encode()

	return header, body

def checkRealTicker(new_stock):

	tickerList = cst_list
	
	isRealTicker = new_stock["Stock"] in tickerList

	return isRealTicker

def emptyValidation(new_stock):
	test = 0
	empty_field = False
	if new_stock["Stock"] == "":
		test +=1
	if new_stock["Quantity"] == "":
		test +=1
	if new_stock["Quantity"] == "":
		test +=1

	if test > 0:
		empty_field = True
	
	return empty_field

def priceValidation(new_stock):

	priceValid = True
	if float(new_stock["Price"]) <= 0:
		priceValid = False
	
	return priceValid
		
def shortValidation(new_stock):

	is_long  = True 
			
	portfolio_list = getPortfolio()
	stock_index = stockInPortfolio(portfolio_list, new_stock)
	
	if stock_index >= 0:
		if float(portfolio_list[stock_index]["Quantity"]) + float(new_stock["Quantity"]) < 0:
			is_long = False
	return is_long


def validation(new_stock):

	validation_error = 0

	if emptyValidation(new_stock):
		validation_error = 1
	elif not checkRealTicker(new_stock):
		validation_error = 2
	elif not priceValidation(new_stock):
		validation_error = 3
	elif not shortValidation(new_stock):
		validation_error = 4

	return validation_error

def errorCode(validation_error):
	error_text = "Error Unknown"
	
	if validation_error == 1:
		error_text = "EMPTYFIELD"

	elif validation_error == 2:
		error_text = "WRONGSTOCK"

	elif validation_error == 3:
		error_text = "BADPRICE"

	elif validation_error == 4:
		error_text = "SHORT"

	return error_text
def getStockQuote(stock):

	response_buffer = BytesIO()
	curl = pycurl.Curl()
	curl.setopt(curl.SSL_VERIFYPEER, False)
	
	curl.setopt(curl.URL, 'https://sandbox.iexapis.com/stable/stock/'+ stock +'/quote?token='+token)
	curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
	curl.perform()
	curl.close()

	
	body = json.loads(response_buffer.getvalue())
	quote = body["latestPrice"]
	
	return quote

def getStockQuotes(stockList):

	response_buffer = BytesIO()
	curl = pycurl.Curl()
	curl.setopt(curl.SSL_VERIFYPEER, False)
	stockstr = ''
	for stock in stockList:
		stockstr+=stock
		stockstr+=","
	stockstr = stockstr[:-1]
	
	curl.setopt(curl.URL, 'https://sandbox.iexapis.com/stable/stock/market/batch?types=price&symbols='+ stockstr +'&token='+token)
	
	curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
	curl.perform()
	curl.close()
	
	
	priceList = []

	body = json.loads(response_buffer.getvalue())
	for stock in stockList:
		priceList.append(body[stock]["price"])
	
	
	return priceList


def postStockQuote(message):
	
	response = message.split()
	stock = response[-1].strip('"')
	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	body = str(getStockQuote(stock)).encode()
	
	return header, body

#retrieves stock stats and 5y chart values from end point and returns JSON with this data
def getStockStats(stock):

	
	response_buffer = BytesIO()
	curl = pycurl.Curl()
	curl.setopt(curl.SSL_VERIFYPEER, False)	
	curl.setopt(curl.URL, 'https://sandbox.iexapis.com/stable/stock/'+ stock +'/chart/5y?&chartCloseOnly=true&token='+token)	
	curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
	curl.perform()
	curl.close()
	
	stockChart = json.loads(response_buffer.getvalue())


	response_buffer = BytesIO()
	curl = pycurl.Curl()
	curl.setopt(curl.SSL_VERIFYPEER, False)
	curl.setopt(curl.URL, 'https://sandbox.iexapis.com/stable/stock/'+ stock +'/stats?token='+token)
	curl.setopt(curl.WRITEFUNCTION, response_buffer.write)
	curl.perform()
	curl.close()	
	stockStats = json.loads(response_buffer.getvalue())

	stockData = {}
	stockData["stockChart"] =stockChart
	stockData["stockStats"] = stockStats

	return stockData

#receives stock symbol from client and sends 5y chart and stock data back to client
def postGetStats(message):

	response = message.split()
	stock = response[-1].strip('"')

	header = "HTTP/1.1 200 OK\r\n\r\n".encode()
	body = json.dumps(getStockStats(stock)).encode()
	return header, body

#receives transaction info from client and returns updated portfolio to client
def postPortfolio(message):
	
	response = message.split()	

	new_stock = json.loads(response[-1])	
	new_stock["Stock"] = new_stock["Stock"].upper()	
	valid = validation(new_stock)


	if valid == 0:
				
		portfolio_list = getPortfolio()
		stock_index = stockInPortfolio(portfolio_list, new_stock)

		if stock_index > -1:
			
			if (float(portfolio_list[stock_index]["Quantity"]) + float(new_stock["Quantity"]) > 0):
				portfolio_list[stock_index]["Price"] = getAveragePrice(portfolio_list[stock_index], new_stock)
				portfolio_list[stock_index]["Quantity"] = float(portfolio_list[stock_index]["Quantity"]) + float(new_stock["Quantity"])			
				header = "HTTP/1.1 200 OK\r\n\r\n".encode()
				body = "".encode()
			elif (float(portfolio_list[stock_index]["Quantity"]) + float(new_stock["Quantity"]) == 0):
				del portfolio_list[stock_index]
				header = "HTTP/1.1 200 OK\r\n\r\n".encode()
				body = "".encode()

		else:
			
			if float(new_stock["Quantity"]) > 0:
				portfolio_list.append(new_stock)
				header = "HTTP/1.1 200 OK\r\n\r\n".encode()
				body = "".encode()


		with open('portfolio.json') as f:
			jase = json.load(f)	
			
			
		jase['portfolio'] = portfolio_list

		with open('portfolio.json', 'w') as outfile:
			outfile.write(json.dumps(jase))
	

	else:

			error_code = errorCode(valid)
		
			error_body =( "Error - "+error_code)
			body = error_body.encode()
			header = "HTTP/1.1 449 RETRY WITH\r\n\r\n".encode()

	return header, body

#sends ticker list to client
def tickers():

	header = "HTTP/1.1 200 OK\r\n\r\n".encode()

	tickers = cst_list
	body = json.dumps(tickers).encode()
	
	
	return header, body

#default service function
def default(message):

	header, body = welcome(message)

	return header, body

#opens portfolio JSON file
def getPortfolio():

	with open('portfolio.json') as f:
		jase = json.load(f)
	portfolio = jase['portfolio']
	return portfolio

#checks if a stock is in the portfolio returns stocks index or -1 if stock isn't present
def stockInPortfolio(portfolio_list, new_stock):
	stock_in_portfolio = -1
	for i, current_stock in enumerate(portfolio_list):
		if current_stock["Stock"] == new_stock["Stock"]:
			stock_in_portfolio = i	
	return stock_in_portfolio

#gets weighted average of stocks purchased that are of the same type
def getAveragePrice(current_stock, new_stock):
	
	current_stock_paid = float(current_stock["Price"]) * float(current_stock["Quantity"])
	
	new_stock_paid = float(new_stock["Price"]) * float(new_stock["Quantity"])
	
	total_stock_quantity = float(current_stock["Quantity"]) + float(new_stock["Quantity"])
	total_stock_paid = current_stock_paid + new_stock_paid
	average_stock_price = total_stock_paid/total_stock_quantity
	return average_stock_price


#We process client request here. The requested resource in the URL is mapped to a service function which generates the HTTP reponse 
#that is eventually returned to the client. 
def process(connectionSocket) :	
	# Receives the request message from the client
	message = connectionSocket.recv(4096).decode()

	http_method = message.split()[0]

	#my student ID which acts as the login credentials
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


	#get options
	
	if http_method == "GET":


		if len(message) > 1:


			# Extract the path of the requested object from the message
			# Because the extracted path of the HTTP request includes
			# a character '/', we read the path from the second character
			resource = message.split()[1][1:]
			
			#map requested resource (contained in the URL) to specific function which generates HTTP response
			if not auth_present:
				
				responseHeader, responseBody = noAuth()

			elif resource == "":
				responseHeader, responseBody = portfolio(message)
			elif resource == "portfolio":
				responseHeader,responseBody = portfolio(message)
			elif resource == "research":
				responseHeader,responseBody = research(message)	
			elif resource == "portfolio.json":
				responseHeader,responseBody = jason()
			elif resource == "Tickers":
				responseHeader,responseBody = tickers()
			else:
				responseHeader,responseBody = getFile(resource)
	#post options 
	if 	http_method == "POST":
		if len(message) > 1:

			resource = message.split()[1][1:]
			

			if not auth_present:				
				responseHeader, responseBody = noAuth(message)
			elif resource == "Portfolio":
				responseHeader,responseBody = postPortfolio(message)
			elif resource == "StockQuote":
				responseHeader,responseBody = postStockQuote(message)
			elif resource == "GetStats":
				responseHeader,responseBody = postGetStats(message)


		
	
	connectionSocket.send(responseHeader)
	connectionSocket.send(responseBody)
	connectionSocket.close()

	# Send the HTTP response header line to the connection socket

	# Send the content of the HTTP body (e.g. requested file) to the connection socket

	# Close the client connection socket



#Main web server loop. It simply accepts TCP connections, and get the request processed in seperate threads.
#have initia

start = time.time()
cst_list = getTickerList()
while True:
	
	
	# Set up a new connection from the client
	connectionSocket, addr = serverSocket.accept()

	current_time = time.time()
	if ((current_time - start) > 900):
		start = time.time()
		cst_list = getTickerList()
		

	

	# start new thread to handle incoming request
	_thread.start_new_thread(process,(connectionSocket,))
	
	


