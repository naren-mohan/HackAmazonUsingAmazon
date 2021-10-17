from bs4 import BeautifulSoup
import proxyScrape
import requests
import os
from random import choice
from lxml.html import fromstring
from itertools import cycle
from time import perf_counter
import concurrent.futures


def remove_comma(Cost):							#SMALL FUNCTION TO REMOVE THE COMMAS IN THE PRICE FOR STORAGE PURPOSES
	cost1 = Cost.split(',')
	fCost = ''
	for i in range(len(cost1)):
		fCost = fCost+str(cost1[i])
	return fCost


def get_payload(payload):						#FUNCTION TO GET PARAMETERS(FOR IDENTIFYING THE SIZE)
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


def get_shipping_price(div):						#FUNCTION TO GET THE SHIPPING PRICE
	shipDiv = str(div.find('span', attrs={'id':'ourprice_shippingmessage'}))
	shipPriceTemp = shipDiv.split('Delivery')
	shipPrice = shipPriceTemp[0].split('.')
	shipPrice = shipPrice[0].split('\xa0')
	# print("PRINTING")
	# print(shipPrice)
	
	if len(shipPrice)<=1:
		return 0
	shipPrice = int(remove_comma(shipPrice[1]))
	return shipPrice

def get_cost(url):								#MASTER FUNCTION WHICH SCRAPES THE CURRENT COST OF THE PRODUCT
	
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
						"Accept-Encoding":"gzip, deflate",     
						"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
						"DNT":"1",
						"Connection":"close", 
						"Upgrade-Insecure-Requests":"1"}
	payload = get_payload(url)
	
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

	iPrice = str(price).split('.')
	cents = float(iPrice[1]) * 0.01
	iPrice = iPrice[0].split('$')  	#Removes rupiya symbol


	#now remove commas
	cost = float(remove_comma(iPrice[1])) + cents
	shipPrice = get_shipping_price(div)
	#cost = int(iPrice[1])
	if lDeal:
		print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!DEAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print('Name = '+name+'  Cost =',cost,' Shipping =',shipPrice)
	return cost


def main():

	# Read from the text file 

	
	wishlist = [
	'https://www.amazon.com/Beats-Studio3-Wireless-Over%E2%80%91Ear-Headphones/dp/B08528ZCNY/?_encoding=UTF8&smid=ATVPDKIKX0DER&pf_rd_p=495206da-5292-4db7-aa14-c2b2d8671985&pd_rd_wg=ePvei&pf_rd_r=WJ1HFP0RBA8ND6HX59YC&pd_rd_w=DzsPT&pd_rd_r=ab663589-72ee-4448-84c0-08db1009da9b&ref_=pd_gw_unk&th=1',
	'https://www.amazon.com/Philips-Norelco-Rechargeable-Technology-S7782/dp/B08KT6DFRN/ref=lp_12215725011_1_2?dchild=1&rdc=1'
	]
	
	# with concurrent.futures.ThreadPoolExecutor() as executor:
	# 	executor.map(get_cost,wishlist)

	for url in wishlist:
		get_cost(url)

proxyPool = proxyScrape.getProxy()

if __name__ == '__main__':
	start = perf_counter()
	main()
	end = perf_counter()
	print('Time Taken = ',end-start)