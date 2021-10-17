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

	iPrice = price.split('.')
	iPrice = iPrice[0].split('\xa0')  	#Removes rupiya symbol

	#now remove commas
	cost = int(removeComma(iPrice[1]))
	# print(name)
	# print(cost)
	# #print(div)
	shipPrice = getShippingPrice(div)
	#cost = int(iPrice[1])
	if lDeal:
		print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!DEAL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	print('Name = '+name+'  Cost =',cost,' Shipping =',shipPrice)
	return cost


def main():
	wishlist = [
	'https://www.amazon.in/Nike-Mens-Precision-Basketball-Shoes/dp/B0851CYJQ3/ref=pd_sbs_309_6/257-5924260-3005507?_encoding=UTF8&pd_rd_i=B0851CYJQ3&pd_rd_r=7b29a717-b7eb-4469-bcfe-c55246f6a55a&pd_rd_w=Ij1pe&pd_rd_wg=JeJSw&pf_rd_p=758bfbc8-a8f2-4456-bf65-ae5d502eac06&pf_rd_r=TT7RMSMEHN7K51QG36HV&psc=1&refRID=TT7RMSMEHN7K51QG36HV',
	'https://www.amazon.in/dp/B07NDFTM65/?coliid=I195MCJL3VVFAG&colid=1PU3VQ3I9PNPC&psc=1&ref_=lv_ov_lig_dp_it',
	'https://www.amazon.in/dp/B01N07NBLA/?coliid=I352IRSMR16O3R&colid=1PU3VQ3I9PNPC&psc=1&ref_=lv_ov_lig_dp_it',
	'https://www.amazon.in/Rugged-Extra-Tough-Unbreakable-Braided/dp/B0789LZTCJ/ref=gbps_tit_s-5_9f8e_c45f72c9?smid=A14CZOWI0VEHLG&pf_rd_p=b4500f5f-e496-4b18-ab75-623b14149f8e&pf_rd_s=slot-5&pf_rd_t=701&pf_rd_i=gb_main&pf_rd_m=A1VBAL9TL5WCBF&pf_rd_r=8TGBFKPQM89YC82MJEVF',
	'https://www.amazon.in/Nike-Basketball-University-White-Black-Numeric_10/dp/B07TLNDB7M/ref=sr_1_1?dchild=1&keywords=nike%2Bbasketball%2Bshoes%2Bred&qid=1606409004&sr=8-1&th=1&psc=1',
	'https://www.amazon.in/NOC-Playing-Limited-Air-Cushion-Finish/dp/B0846LS4YH/ref=sr_1_1?keywords=nocs+green+deck&qid=1584618955&s=apparel&sr=8-1',
	'https://www.amazon.in/Nike-Basketball-University-White-Black-Numeric_10/dp/B07TNS9VCW/ref=sr_1_1?dchild=1&keywords=nike%2Bbasketball%2Bshoes%2Bred&qid=1606409004&sr=8-1&th=1&psc=1',
	'https://www.amazon.in/A400-Type-C-Cable-Meter-Black/dp/B077Z65HSD/ref=sr_1_3?crid=32FB6BVZO4LDA&keywords=boat+rugged+cable+type+c&qid=1584552066&s=electronics&smid=A14CZOWI0VEHLG&sprefix=boat+rugged+%2Celectronics%2C343&sr=1-3'
	]
	'''wishlist = ['https://www.amazon.in/dp/B01N07NBLA/?coliid=I352IRSMR16O3R&colid=1PU3VQ3I9PNPC&psc=1&ref_=lv_ov_lig_dp_it']
	for url in wishlist:
		getCost(url)'''
	with concurrent.futures.ThreadPoolExecutor() as executor:
		executor.map(getCost,wishlist)



proxyPool = proxyScrape.getProxy()

if __name__ == '__main__':
	start = perf_counter()
	main()
	end = perf_counter()
	print('Time Taken = ',end-start)