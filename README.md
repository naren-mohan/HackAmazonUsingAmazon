# Hack Amazon Using Amazon
#### Started as a hobby project to track the prices of products listed on amazon.com

Amazon is one of the top, if not, the top e-commerce platform on the internet. Millions of products are bought and sold everyday in this e-commerce platform. This project web scrapes the amazon.com efficiently using BeautifulSoup library to analyze the prices data. The name of the project is because it web scrapes amazon.com (hack amazon) and was hosted on free-tier aws ec2 instance (using amazon), excuse the click-baity title! :P 

### Objectives
* Track the prices of products
* Notify through email in case of price drop of a product
* Identify the pricing trends with the dataset collected through this project

### Implementation
* Webscrape amazon.com product URLs to get the price and shipping price
* Collect the pricing data every hour and store in the sqlite database
* Basic functional front end developed using Flask and Jinja templates to add/remove/edit products interested and also view pricing information

### Requirements
```
pip3 install -r requirements.txt
```

### Further Implementations
* Visualize the pricing trend in the frontend for each product
* Scrape more features such as listing price, reviews from the amazon.com
* Improve the front end.
