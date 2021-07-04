import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import connect

parser = argparse.ArgumentParser()
parser.add_argument("--page_num_max", help="Enter the no of pages to parse", type=int)
parser.add_argument("--dbname", help="Enter the name of database", type=str)

args = parser.parse_args()

oyo_url = "https://www.oyorooms.com/hotels-in-bangalore/?page="
page_num_MAX = args.page_num_max
scraped_info_list = []
connect.connect(args.dbname)

for page_num in range(1, page_num_MAX):
    url = oyo_url + str(page_num)
    print("GET Request for: " + url)
    req = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64"})
    content = req.content

    soup = BeautifulSoup(content, "html.parser")

    all_hotels = soup.find_all("div", {"class": "hotelCardListing"})
    for hotel in all_hotels:
        hotel_dict = {}
        hotel_dict["name"] = hotel.find("h3", {"class": "listingHotelDescription__hotelName"}).text
        hotel_dict["address"] = hotel.find("span", {"itemprop": "streetAddress"}).text
        hotel_dict["price"] = hotel.find("span", {"class": "listingPrice__finalPrice"}).text
        try:
            hotel_dict["rating"] = hotel.find("span", {"class": "hotelRating__ratingSummary"}).text
        except AttributeError:
            hotel_dict["rating"] = None

        parent_amenities_element = hotel.find("div", {"class": "amenityWrapper"})

        amenities_list = []
        try:
            for amenity in parent_amenities_element.find_all("div", {"class": "amenityWrapper__amenity"}):
                amenities_list.append(amenity.find("span", {"class": "d-body-sm"}).text.strip())
        except AttributeError:
            pass

        hotel_dict["amenities"] = ", ".join(amenities_list[:-1])
        scraped_info_list.append(hotel_dict)
        connect.insert_into_table(args.dbname, tuple(hotel_dict.values()))

df = pd.DataFrame(scraped_info_list)
print(f"{'-'*5}Creating csv file{'-'*5}")
df.to_csv("Oyo.csv")
connect.get_hotel_info(args.dbname)
