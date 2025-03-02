import math
import sqlite3
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import logging
import requests
from bs4 import BeautifulSoup
import csv
import json

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b

def log_to_db(operation, num1, num2, result):
    conn = sqlite3.connect("calculator_history.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS history (operation TEXT, num1 REAL, num2 REAL, result TEXT)")
    cursor.execute("INSERT INTO history (operation, num1, num2, result) VALUES (?, ?, ?, ?)", 
                   (operation, num1, num2, str(result)))
    conn.commit()
    conn.close()

def save_history_to_csv():
    conn = sqlite3.connect("calculator_history.db")
    df = pd.read_sql_query("SELECT * FROM history", conn)
    df.to_csv("calculator_history.csv", index=False)
    conn.close()

def log_to_file(operation, num1, num2, result):
    logging.basicConfig(filename="calculator.log", level=logging.INFO, format="%(asctime)s - %(message)s")
    logging.info(f"{operation}: {num1} {operation} {num2} = {result}")

def scrape_website(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Unable to fetch data from {url}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    for item in soup.find_all('h2'):
        headline = item.text.strip()
        link = item.find('a')['href'] if item.find('a') else 'No link available'
        data.append({'headline': headline, 'link': link})
    
    return data

def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['headline', 'link'])
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filename}")

def save_to_json(data, filename):
    if not data:
        print("No data to save.")
        return
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {filename}")

def calculator():
    while True:
        print("\nSimple Calculator")
        print("Select operation:")
        print("1. Add")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. View History")
        print("6. Save History to CSV")
        print("7. Exit")
        
        choice = input("Enter choice (1-7): ")
        
        if choice == '7':
            print("Exiting calculator. Goodbye!")
            break
        
        if choice == '5':
            conn = sqlite3.connect("calculator_history.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM history")
            records = cursor.fetchall()
            conn.close()
            print("\nCalculation History:")
            for record in records:
                print(record)
            continue
        
        if choice == '6':
            save_history_to_csv()
            print("History saved to calculator_history.csv")
            continue
        
        if choice in ('1', '2', '3', '4'):
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue
            
            if choice == '1':
                result = add(num1, num2)
                operation = "Addition"
            elif choice == '2':
                result = subtract(num1, num2)
                operation = "Subtraction"
            elif choice == '3':
                result = multiply(num1, num2)
                operation = "Multiplication"
            elif choice == '4':
                result = divide(num1, num2)
                operation = "Division"
            
            print(f"Result: {result}")
            log_to_db(operation, num1, num2, result)
            log_to_file(operation, num1, num2, result)
        else:
            print("Invalid choice. Please select a valid operation.")

def web_scraper():
    url = input("Enter the website URL to scrape: ")
    scraped_data = scrape_website(url)
    
    if scraped_data:
        print("Select format to save data:")
        print("1. CSV")
        print("2. JSON")
        choice = input("Enter choice (1/2): ")
        
        if choice == '1':
            save_to_csv(scraped_data, "scraped_data.csv")
        elif choice == '2':
            save_to_json(scraped_data, "scraped_data.json")
        else:
            print("Invalid choice. Data not saved.")

if __name__ == "__main__":
    while True:
        print("Select mode:")
        print("1. Calculator")
        print("2. Web Scraper")
        print("3. Exit")
        mode = input("Enter choice (1-3): ")
        if mode == '1':
            calculator()
        elif mode == '2':
            web_scraper()
        elif mode == '3':
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")
