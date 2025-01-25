import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from datetime import datetime

# Function to fetch and extract the winning numbers for a specific year
def fetch_winning_numbers(year):
    url = f"https://za.national-lottery.com/powerball/results/{year}-archive"
    print(f"Fetching data for year {year}...")
    
    # Send GET request to the website
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page for {year}")
        return []
    
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the table rows containing the draw results
    rows = soup.find_all("tr")
    
    # Initialize list to store winning numbers
    winning_numbers = []
    
    # Loop through each row and extract the date and winning numbers
    for row in rows:
        date_cell = row.find("td", class_="noBefore colour")
        numbers_cell = row.find("td", class_="noBefore nowrap")
        
        if date_cell and numbers_cell:
            # Extract the date and the numbers
            date = date_cell.get_text(strip=True)
            numbers = [ball.get_text(strip=True) for ball in numbers_cell.find_all("li", class_="result")]
            
            # Skip if no numbers are found
            if numbers:
                winning_numbers.append({
                    "year": year,
                    "date": date,
                    "numbers": numbers
                })
    
    return winning_numbers

def save_to_csv(results, filename='powerball_results.csv', mode='w'):
    headers = ['Date', 'Number 1', 'Number 2', 'Number 3', 'Number 4', 'Number 5', 'Bonus Ball']
    write_headers = mode == 'w'
    
    with open(filename, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if write_headers:
            writer.writerow(headers)
        
        for result in results:
            # Fix date parsing for format: 'Saturday18 January 2025'
            date_str = result['date']
            # Extract components from date string
            day_name = date_str[:-2].rstrip('0123456789')  # Get day name
            day_num = ''.join(filter(str.isdigit, date_str[:date_str.find(' ')]))  # Get day number
            rest = date_str[date_str.find(' ')+1:]  # Get month and year
            
            # Reconstruct date string in a format strptime can handle
            parsed_date_str = f"{day_num} {rest}"
            date_obj = datetime.strptime(parsed_date_str, '%d %B %Y')
            formatted_date = date_obj.strftime('%a, %b %d, %Y')
            
            # Split numbers into main numbers and bonus
            numbers = result['numbers']
            main_numbers = numbers[:5]
            bonus_ball = numbers[5]
            
            row = [formatted_date] + main_numbers + [bonus_ball]
            writer.writerow(row)

# Main function to fetch data for all years
def fetch_all_years(start_year, end_year):
    all_results = []
    first_year = True
    
    for year in range(start_year, end_year - 1, -1):
        winning_numbers = fetch_winning_numbers(year)
        
        if winning_numbers:
            print(f"Found {len(winning_numbers)} results for {year}")
            # Use write mode for first year, append for rest
            mode = 'w' if first_year else 'a'
            save_to_csv(winning_numbers, mode=mode)
            first_year = False
            all_results.extend(winning_numbers)
        else:
            print(f"No results found for {year}")
        
        wait_time = random.uniform(10, 20)
        print(f"Waiting {wait_time:.2f} seconds before fetching {year - 1}...")
        time.sleep(wait_time)
    
    return all_results

# Fetch data for all years from 2025 down to 2000
fetch_all_years(2025, 2000)

print("All winning numbers have been saved to all_winning_numbers.csv and powerball_results.csv")
