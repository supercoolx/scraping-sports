from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson import ObjectId
import time

app = Flask(__name__)

client = MongoClient('mongodb://admin:123qwe%21%40%23QWE@localhost:27017/sportbet?authSource=admin')  # Use your MongoDB URI
db = client['scrapping']  # Use the database name
collection = db['data']

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless (without opening a browser window)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Function to convert ObjectId to string
def convert_objectid(data):
    if isinstance(data, list):
        for item in data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
    elif isinstance(data, dict):
        if '_id' in data:
            data['_id'] = str(data['_id'])
    return data

# Function to perform the scraping
def scrape_data():
    driver = webdriver.Chrome(options=chrome_options)
    url = 'https://www.pmu.ch/en/sporttip/sportsbetting/bet/current'
    driver.get(url)

    # Clear the collection before inserting new data
    collection.delete_many({})

    # Wait for the page to fully load
    time.sleep(2)

    # Function to scroll gradually
    def gradual_scroll_to(driver, start_height, end_height, step=0.05):
        """Scroll gradually from the start_height to the end_height."""
        current_height = start_height
        while current_height < end_height:
            # Scroll to the current height
            driver.execute_script(f"window.scrollTo(0, {current_height});")
            # Small step down
            current_height += driver.execute_script("return document.body.scrollHeight") * step
            # Wait briefly after each step
            time.sleep(1)

    # Get the initial page height
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Variable to store all scraped data
    scraped_data = []

    # Function to perform the actual scraping
    def extract_data(soup):
        bet_containers = soup.find_all('div', class_="o_bet-list")
        scraped_bets = []
        team_names = []
        odds = []

        for bet in bet_containers:
            starttime = bet.find_all('div', class_="t_prematch-current-bet-container__block-time-info")
            name = bet.find_all('span', class_="t_prematch-current-bet-container__competition-text")
            currenttime = bet.find_all('span', class_="t_prematch-current-bet-container__time")
            team_name = bet.find_all('span', class_="m_bet-button__name")
            odds = bet.find_all('span', class_="m_bet-button__odds-text")
            starttime = [starttime[0].get_text(strip=True)]  # Use the same starttime for all bets
            name = [n.get_text(strip=True) for n in name]  # Extract text from the name elements
            currenttime = [ct.get_text(strip=True) for ct in currenttime]  # Extract text from the currenttime elements
            team_names = [tn.get_text(strip=True) for tn in team_name]  # Extract text from the team name elements
            odds = [od.get_text(strip=True) for od in odds]  # Extract text from the odds elements

            # Initialize the index to track team and odds
            team_idx = 0

            for i in range(len(name)):
                current_starttime = starttime[0]  
                current_name = name[i]
                current_time = currenttime[i]

                # Get team 1 and odds 1
                team1_name = team_names[team_idx]
                odds1 = odds[team_idx]

                # Check if there's an "X" (draw)
                if team_names[team_idx + 1] == "X":
                    x_value = odds[team_idx + 1]  # Draw odds
                    team2_name = team_names[team_idx + 2]  # Team 2
                    odds2 = odds[team_idx + 2]  # Team 2 odds
                    team_idx += 3  # Move to the next set (team1, X, team2)
                else:
                    x_value = 0  # No draw, set X to 0
                    team2_name = team_names[team_idx + 1]  # Team 2
                    odds2 = odds[team_idx + 1]  # Team 2 odds
                    team_idx += 2  # Move to the next set (team1, team2)

                # Save the data into MongoDB
                bet_data = {
                    'current_starttime': current_starttime,
                    'current_name': current_name,
                    'current_time': current_time,
                    'team1_name': team1_name,
                    'odds1': odds1,
                    'x_value': x_value,
                    'team2_name': team2_name,
                    'odds2': odds2,
                }
                inserted_id = collection.insert_one(bet_data).inserted_id
                bet_data['_id'] = str(inserted_id)  # Convert ObjectId to string
                scraped_bets.append(bet_data)
        return scraped_bets

    # Infinite scroll and scrape loop
    while True:
        # Get the page source and create a BeautifulSoup object
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Scrape data from the page
        scraped_data.extend(extract_data(soup))

        # Gradually scroll down
        gradual_scroll_to(driver, last_height * 0.5, last_height * 0.9)

        # Wait for new content to load
        time.sleep(2)

        # Get the new scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        # If the height hasn't increased, break the loop
        if new_height == last_height:
            break

        last_height = new_height  # Update last_height

    driver.quit()
    return scraped_data

# Define the Flask route for scraping
@app.route('/scrape', methods=['GET'])
def scrape_route():
    scraped_data = scrape_data()
    return jsonify(scraped_data), 200

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    # context = ('/etc/ssl/certs/pocketbotdev9_com.crt', '/etc/ssl/private/pocketbotdev9_com.key')#certificate and key files
    # app.run(host="0.0.0.0", port=6001, debug=True, use_reloader=False, ssl_context=context)
    app.run(debug=True, use_reloader=False)
