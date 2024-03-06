from bs4 import BeautifulSoup
import requests
import pandas as pd

page_1 = 'https://www.buyrentkenya.com/property-for-rent/nairobi'
base_url = 'https://www.buyrentkenya.com'
page_base_url = "https://www.buyrentkenya.com/property-for-rent/nairobi?page="

Location = []
Price = []
Bedrooms = []
Bathrooms = []
Amenities = []

for page in range(1, 428):
    if page == 1:
        page_url = page_1
    else:
        page_url = f'{page_base_url}{page}'

    page_response = requests.get(page_url)
    if page_response.status_code != 200:
        print(f"Page: {page} request failed")
        continue
    page_soup = BeautifulSoup(page_response.text, "lxml")
    houses = page_soup.find_all('div', class_='flex flex-col gap-y-3 w-full md:w-4/5')

    for house in houses:
        url = house.find('h2', class_='font-semibold md:hidden').find('a', class_='no-underline')['href']
        house_url = base_url + url
        house_response = requests.get(house_url)
        if house_response.status_code != 200:
            print(f"House: {house} request failed")
        house_soup = BeautifulSoup(house_response.text, 'lxml')

        try:
            location = house_soup.find('p', class_='hidden items-center text-sm text-gray-500 md:flex').text.strip()
        except AttributeError:
            location = None
        try:
            price = house_soup.find('span', class_='block text-right text-xl font-semibold leading-7 md:text-xxl md:font-extrabold').text.strip().strip('KSh')
        except AttributeError:
            price = None
        try:
            bedrooms = house_soup.find('span', class_='flex h-6 max-w-24 items-center rounded-2xl bg-highlight px-3 py-2 mr-5 font-bold').text.strip()
        except AttributeError:
            bedrooms = None
        try:
            bathrooms = house_soup.find('span', class_='flex h-6 max-w-24 items-center rounded-2xl bg-highlight px-3 py-2 font-bold').text.strip()
        except AttributeError:
            bathrooms = None
        try:
            description = house_soup.find('div', class_='my-3 overflow-hidden bg-white rounded-2xl md:rounded-0 p-3 md:px-0').text.strip()
        except AttributeError:
            description = None
        try:
            features = house_soup.find_all('ul', class_='flex flex-row flex-wrap items-center')
            amenities = []
            feat_no = 0
            for feature in features:
                if feat_no == 2:
                    break
                amenity = feature.find_all('li', 'flex')
                for item in amenity:
                    amenities.append(item.text.strip('\n\n|'))
                feat_no += 1
            amenities = sorted(amenities)
        except AttributeError:
            amenities = []
        Location.append(location)
        Price.append(price)
        Bedrooms.append(bedrooms)
        Bathrooms.append(bathrooms)
        Amenities.append(amenities)
    print(f'Page: {page} Done')


data = {
    "Location": Location, 
    "Bedrooms": Bedrooms, 
    "Bathrooms": Bathrooms,
    "Amenities": Amenities,
    "Price": Price,
}
df = pd.DataFrame(data)
df.to_csv('../data/buyrentke.csv', index=False)
print('===================\nDone Extracting\n===================')
