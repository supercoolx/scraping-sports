# Sports Betting Scraper API

This project scrapes sports betting data from [PMU.ch](https://www.pmu.ch/en/sporttip/sportsbetting/bet/current) using Selenium, stores the data in a MongoDB database, and provides a RESTful API to trigger the scraping process.

## Steps to Set Up and Run the Project

### 1. Install Python

First, make sure Python 3.8+ is installed on your machine. If it isn't, you can download it from the [official Python website](https://www.python.org/downloads/).

### 2. Install chrome and chromedriver
we have to install chrome and chromedriver 112 version
#### Chrome
sudo dpkg -i chrome_112.deb

#### ChromeDriver
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

### 3. Install Required Libraries

Next, you need to install the required Python libraries. Open a terminal or command prompt and run the following commands:

powershell or command

`pip install Flask`
`pip install selenium`
`pip install beautifulsoup4`
`pip install pymongo`

### 4. Start Project

powershell or command

`python index.py`

### 5. Get Data

you should install postman on your PC.

`http://127.0.0.1:5000/scrape`