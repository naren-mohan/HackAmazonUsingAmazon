from bs4 import BeautifulSoup
import requests

def getProxy():
	url = 'https://www.sslproxies.org/'

	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', 
				"Upgrade-Insecure-Requests": "1",
				"DNT": "1",	
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
				"Accept-Language": "en-US,en;q=0.5", 
				"Accept-Encoding": "gzip, deflate"}
		
	r = requests.get(url, headers=headers, allow_redirects=False)

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






