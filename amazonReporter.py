import concurrent.futures
import os
from itertools import cycle
from random import choice
from time import perf_counter

import numpy as np
import requests
from bs4 import BeautifulSoup
from lxml.html import fromstring

import proxyScrape


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

def get_proxy():
	global proxyPool
	proxyPool = proxyScrape.getProxy()

def get_cost(arg_url):						#MASTER FUNCTION WHICH SCRAPES THE CURRENT COST OF THE PRODUCT
	if type(arg_url) == str:
		url = arg_url
	else:
		url = arg_url["url"]
	#print(url)
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
						"Accept-Encoding":"gzip, deflate",     
						"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
						"DNT":"1",
						"Connection":"close", 
						"Upgrade-Insecure-Requests":"1"}
	payload = get_payload(url)
	
	get_proxy()
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
		ret_load = {"id": arg_url["id"],
					"url": arg_url["url"],
					"lowprice": arg_url["lowprice"],
					"cost": -1}
		return ret_load

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

	if type(arg_url) == str:
		return cost
	else:
		ret_load = {"id": arg_url["id"],
					"url": arg_url["url"],
					"lowprice": arg_url["lowprice"],
					"cost": cost}
	return ret_load


def get_prices_df(df_items):
	with concurrent.futures.ThreadPoolExecutor() as executor:
		ret_load = list(executor.map(get_cost, df_items.to_dict('records')))
	print(ret_load)
	return ret_load
	# get_proxy()
	# return get_cost(url)


#print(proxyPool)

if __name__ == '__main__':
	start = perf_counter()
	get_prices_df()
	end = perf_counter()
	#print('Time Taken = ',end-start)
