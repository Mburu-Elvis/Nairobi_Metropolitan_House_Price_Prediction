from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np


page_base_url = 'https://mansiondeal.com/public/aasearchsale.php?pn='
house_base_url = 'https://mansiondeal.com/public/'

def scrape_house_page(house_url):
    response = requests.get(house_url)
    if response.status_code != 200:
        print('Error: page fetch  failed with {} error code'.format(response.status_code))
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        location = soup.find('div', class_='property-info').find('p', class_='area').text.strip()
    except:
        location = np.nan
    try:
        description = soup.find('div', class_='col-lg-9 col-sm-8').find('div', class_='row').find('div', class_='col-lg-8').find('div', class_='spacer').find('p').text.strip()
    except:
        description = np.nan
    
    details = details = soup.find('div', class_='col-lg-9 col-sm-8').find('div', class_='row').find('div', class_='col-lg-4').find('div', class_='col-lg-12 col-sm-6')
    house_details = details.find('div', class_='listing-detail')
    try:
        bedrooms = house_details.find('span', attrs={'data-original-title': 'Bed Room'}).text.strip()
    except:
        bedrooms = np.nan
    try:
        livingrooms = house_details.find('span', attrs={'data-original-title': 'Living Room'}).text.strip()
    except:
        livingrooms = np.nan
    try:
        bathrooms = house_details.find('span', attrs={'data-original-title': 'Bathrooms'}).text.strip()
    except:
        bathrooms = np.nan
    try:
        kitchen = house_details.find('span', attrs={'data-original-title': 'Kitchen'}).text.strip()
    except:
        kitchen = np.nan
    try:
        price = details.find('div', class_='property-info').find('p', class_='price').text.strip()
    except:
        price = np.nan

    amenities = soup.find('div', class_='col-lg-3 col-sm-4 hidden-xs').find('div', class_='hot-properties hidden-xs').find_all('div', class_='row')
    house_amenities = {}
    for amenity in amenities:
        name = amenity.find('div', class_='col-lg-8 col-sm-7').find('p', class_='price').text.strip('')
        if 'Water' in name or 'Electricity' in name:
            house_amenities[name[2:]] = name[0]
        elif 'Garden' in name:
            house_amenities['Garden'] = name
        else:
            house_amenities['Pool'] = name
    house_attributes = {
        'Location': location,
        'Description': description,
        'Bedrooms': bedrooms,
        'Bathrooms': bathrooms,
        'Living Rooms': livingrooms,
        'Kitchen': kitchen,
        'Price': price        
    }
    
    house_attributes.update(house_amenities)
    
    for key, value in house_attributes.items():
        if value == 'n/a' or value == '':
            house_attributes[key] = np.nan
    return house_attributes


def scrape_pages(url):
    page_empty = False
    page_no = 1
    data = pd.DataFrame(columns=['Location', 'Description', 'Bedrooms', 'Bathrooms', 'Living Rooms', 'Kitchen', 'Price'])
    while page_empty == False:
        if page_no == 1:
            response = requests.get('https://mansiondeal.com/public/aredirectsale.php?s=Kenya')
        else:
            response = requests.get(f'{url}{page_no}')
        if response.status_code != 200:
            print(f'Request failed to fetch page {page_no} with Error code {response.status_code}')
        soup = BeautifulSoup(response.text, 'html.parser')
        houses = soup.find_all('div', class_="result")
        house_details = []
        for house in houses:
            relative_url = house.find('a')['href']
            house_url = house_base_url + relative_url
            house_details.append(scrape_house_page(house_url=house_url))
        if page_no == 28:
            page_empty = True
        page_no += 1
        page_dataframe = pd.DataFrame(house_details)
        data = pd.concat([data, page_dataframe])
    return data

data = scrape_pages(page_base_url)

data.to_csv('../data/mansiondeal_sale_price.csv', index=False)