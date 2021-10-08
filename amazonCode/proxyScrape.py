from bs4 import BeautifulSoup
import requests

def getProxy():
	url = 'https://www.sslproxies.org/'

	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
							"Accept-Encoding":"gzip, deflate",     
							"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
							"DNT":"1",
							"Connection":"close", 
							"Upgrade-Insecure-Requests":"1"}
		
	r = requests.get(url,headers=headers)

	soup = BeautifulSoup(r.text,'html.parser')
	div = soup.find('div',attrs={'class':'table-responsive'})
	tbody = div.find('tbody')
	getContent = tbody.find_all('td')
	proxy_list = []

	for i in range(0,len(getContent)):			#Extract only 0th, 1st element
		if i % 8 == 0:
			proxy = getContent[i].text
			port = getContent[i+1].text
			proxy_list.append(str(proxy)+':'+str(port))

	#print('Returning now')
	return proxy_list[:10]






