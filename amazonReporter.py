from bs4 import BeautifulSoup
import proxyScrape
import requests
import os
from random import choice
from lxml.html import fromstring
from itertools import cycle
from time import perf_counter
import concurrent.futures


def removeComma(Cost):							#SMALL FUNCTION TO REMOVE THE COMMAS IN THE PRICE FOR STORAGE PURPOSES
	cost1 = Cost.split(',')
	fCost = ''
	for i in range(len(cost1)):
		fCost = fCost+str(cost1[i])
	return fCost


def getPayload(payload):						#FUNCTION TO GET PARAMETERS(FOR IDENTIFYING THE SIZE)
	list = payload.split('?')
	#print(list)
	if(len(list)<=1):
		return None

	list = list[1].split('&')
	payerDict = {}
	#print(list[0])
	for item in range(len(list)):
		#print(list[item].split('='))
		payerDict[item] = list[item].split('=')
	#print(payerDict)
	return payerDict


def getShippingPrice(div):						#FUNCTION TO GET THE SHIPPING PRICE
	shipDiv = str(div.find('span', attrs={'id':'ourprice_shippingmessage'}))
	shipPriceTemp = shipDiv.split('Delivery')
	shipPrice = shipPriceTemp[0].split('.')
	shipPrice = shipPrice[0].split('\xa0')
	# print("PRINTING")
	# print(shipPrice)
	
	if len(shipPrice)<=1:
		return 0
	shipPrice = int(removeComma(shipPrice[1]))
	return shipPrice

def getCost(url):								#MASTER FUNCTION WHICH SCRAPES THE CURRENT COST OF THE PRODUCT
	
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
						"Accept-Encoding":"gzip, deflate",     
						"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
						"DNT":"1",
						"Connection":"close", 
						"Upgrade-Insecure-Requests":"1"}
	payload = getPayload(url)
	
	proxy = choice(proxyPool)
	print(f'Using Proxy {proxy}')
	try:
		r = requests.get(url,
		params= payload,
		headers=headers,
		proxies={'http':proxy}
		)
	except requests.exceptions.ConnectionError as e:
		print('Status Code - ', r.status_code)
		print(e)
	except Exception as e:
		print(e)
	
	#print(r.url)
	lDeal = False	#Lightning Deal Indicator
	soup = BeautifulSoup(r.text, 'html.parser')
	name = soup.title.string
	#print(name)
	div = soup.find('div',attrs={'id':'price'})
	
	try:
		div.find('span',attrs={'class':'a-size-medium a-color-price priceBlockDealPriceString'})
	except AttributeError as e:
		print('Name = '+name+' Cost = CURRENTLY UNAVAILABLE')
		return None

	if (div.find('span',attrs={'class':'a-size-medium a-color-price priceBlockDealPriceString'}) != None):
		price = (div.find('span',attrs={'class':'a-size-medium a-color-price priceBlockDealPriceString'}).string)
		lDeal = True
	elif(div.find('span',attrs={'class':'a-size-medium a-color-price priceBlockBuyingPriceString'}) != None):
		price = (div.find('span',attrs={'class':'a-size-medium a-color-price priceBlockBuyingPriceString'}).string)
	else:
		price = (div.find('span',attrs={'class':'a-size-medium a-color-price priceBlockSalePriceString'}).string)

	print(price)
	iPrice = str(price).split('.')
	print(iPrice)
	iPrice = iPrice[0].split('₹')  	#Removes rupiya symbol


	#now remove commas
	cost = int(removeComma(iPrice[1]))
	shipPrice = getShippingPrice(div)
	#cost = int(iPrice[1])
	if lDeal:
		print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!DEAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print('Name = '+name+'  Cost =',cost,' Shipping =',shipPrice)
	return cost


def main():
	wishlist = [
	'https://www.amazon.in/Nike-Court-Legacy-Sneaker-9-CU4150-103/dp/B096QZC2Q2/ref=sr_1_2?dchild=1&keywords=nike%2Bsneakers&qid=1633373782&qsid=260-4279648-5963656&sr=8-2&sres=B08R4VGX5T%2CB096QZC2Q2%2CB00XWPWWYM%2CB07PL2QQGV%2CB00XQBRC74%2CB07BQXW4TG%2CB0946G5NT2%2CB00WQNO4U6%2CB08PKCS1Y9%2CB09CLBGQ2T%2CB08FGWCH7F%2CB07L6B6NHL%2CB011AC154Q%2CB0187Q593Q%2CB082R6S1PW%2CB0838JSL9B%2CB0178Q7CNG%2CB07C9J8MWY%2CB08R5LDBS1%2CB01IYK9Y86&srpt=SHOES&th=1&psc=1'
	]
	
	with concurrent.futures.ThreadPoolExecutor() as executor:
		executor.map(getCost,wishlist)

	# for url in wishlist:
	# 	getCost(url)

proxyPool = proxyScrape.getProxy()

if __name__ == '__main__':
	start = perf_counter()
	main()
	end = perf_counter()
	print('Time Taken = ',end-start)