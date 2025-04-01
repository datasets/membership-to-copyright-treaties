import os
import requests
import pandas as pd
from datetime import datetime  # Change this import
from bs4 import BeautifulSoup

def get_treaty_links():
    url = 'https://www.wipo.int/treaties/en/#accordion__col1'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    ul_element = soup.find('ul', class_='dividers')
    treaties = []
    links = []
    if ul_element:
        li_elements = ul_element.find_all('li')
        for li in li_elements:
            a_tag = li.find('a', href=True)
            if a_tag:
                link_text = a_tag.get_text(strip=True)
                href_link = a_tag['href']
                treaties.append(link_text)
                links.append(href_link)
                #print(f'Text: {link_text}, Href: {href_link}')
    else:
        print('The specified <ul> element with class "dividers" was not found on the page.')
    if not os.path.exists('cache'):
        os.makedirs('cache')
    with open('cache/treaties.txt', 'w') as f:
        for treaty in treaties:
            f.write(treaty + '\n')
    return links, treaties

def convert_date(date_str):
    """Convert date from 'Month day, Year' to 'YYYY-MM-DD' format if valid."""
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str 

def clean_data(data):
    cleaned_data = []
    
    for row in data:
        if len(row) < 5:
            continue  # Skip invalid rows
        
        country, city, date1, col4_data, date3 = row[0], row[1], row[2], row[3], row[4]
        
        # Split the fourth column
        col4_parts = col4_data.split(": ")
        if len(col4_parts) == 2:
            column4, date2 = col4_parts
        else:
            column4, date2 = col4_data, ""  # Handle unexpected cases
        
        date1 = convert_date(date1)
        date2 = convert_date(date2)
        date3 = convert_date(date3)
        
        cleaned_data.append([country, city, date1, column4, date2, date3])
    
    return cleaned_data
def parse_pdf(links, treaties):
    pdf_links = []
    data = []
    for link in links:
        soup = BeautifulSoup(requests.get('https://www.wipo.int' + link).content, 'html.parser')
        ul_element = soup.find_all('ul', class_='dot__list')
        for i in range(len(ul_element)):
            a_tag = ul_element[i].find('a', href=True)
            if a_tag:
                href_link = a_tag['href']
                if 'ShowResults' in href_link:                 
                    pdf_links.append(href_link)                   

    
    for link, treaty in zip(pdf_links, treaties):
        soup1 = BeautifulSoup(requests.get(link).content, 'html.parser')
        tbody = soup1.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                row_data = []
                for td in tds:
                    div = td.find('div')
                    text = div.text.strip() if div else td.text.strip()
                    # In the beginning after first data append treaty name to each column
                    row_data.append(text)
                if row_data:  # Only append non-empty rows
                    if 'WIPO' not in treaty:
                        treaty = treaty.split()[0]
                    row_data.insert(1, treaty)
                    # Remove last value 
                    row_data.pop(-1)
                    data.append(row_data)
    
    data = clean_data(data)
    df = pd.DataFrame(data, columns=['Contracting Party','Treaty','Signature Date','Instrument Type','Instrument Date','Entry Into Force Date'])
    df.to_csv('data/membership-to-copyright-treaties.csv', index=False)


if __name__ == '__main__':
    links, treaties = get_treaty_links()
    parse_pdf(links, treaties)
