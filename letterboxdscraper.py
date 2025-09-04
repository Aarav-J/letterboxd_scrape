import sys
import time 
import requests
from bs4 import BeautifulSoup as bs
import json 
import os

# Use fakeredis if in Lambda environment, otherwise use regular redis
if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    import fakeredis
    redis_client = fakeredis.FakeStrictRedis()
else:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

from datetime import datetime, timedelta
MAIN_URL = "https://letterboxd.com/aarav_j/films"
TITLE_URl = 'https://letterboxd.com/film/'
CACHE_EXPIRY = 120  # Cache for 2 minutes

def get_cached_data(key):
    """Get data from Redis cache"""
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cached_data(key, data, expiry=CACHE_EXPIRY):
    """Set data in Redis cache"""
    redis_client.setex(key, expiry, json.dumps(data))

def url_scrape(url): 
    print("fetching url: ", url)
    response = requests.get(url)
    # response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print("Failed to retrieve the page. Status code:", response.status_code)
        return None
    soup = bs(response.text, 'html.parser')
    return soup 

# def get_movies(soup): 
#     # movies = []
#     movie_elements = soup.find_all('li', class_='poster-container')
#     for movie in movie_elements:
#         # print();
#         get_title(movie.contents[1]['data-film-slug'])
#     # print(movie_elements[0].contents[1]['data-film-slug'])
#     # print(movie_elements[1]['data-poster-url'])
#     print(f"Found {len(movie_elements)} movies.")


# def get_title(slug): 
#     soup = url_scrape(TITLE_URl + slug)
#     if soup is None:
#         return None
#     title_element = soup.find('span', class_="name")
#     if title_element:
#         return title_element.text.strip()
#     return None
# soup = url_scrape(MAIN_URL)
# get_movies(soup)

def get_recent_movie(): 
    # Try to get cached data
    cached_data = get_cached_data('recent_movie')
    if cached_data:
        return cached_data

    # If no cached data, scrape the website
    soup = url_scrape(MAIN_URL + "/diary/")
    films = soup.find_all('tr', class_="diary-entry-row")
    # print(films)
    film = films[0]
    try: 
        date = film.find('a', class_="daydate").attrs['href'].split('/')[5:8]
        year = date[0]
        month = date[1]
        day = date[2]
    except: 
        month = None
        year = None
        day = None
    
    titleDiv = film.find('h2', class_='name')
    title = titleDiv.contents[0].text.strip()
    slug = titleDiv.contents[0].attrs['href'].split('/')[3]
    # anchor = film.find('a', class_=)
    # print(title)
    # print(slug)
    rating = film.find_all('input', class_='rateit-field')[0].attrs['value']
    # print(rating)
    # slug = 
    review_link = film.find('a', class_='has-icon').attrs['href'] if film.find('a', class_="has-icon") else False
    if review_link: 
        written_review = get_review(review_link)
        # print(written_review)
        print("getting review")
    else: 
        print("no review")
    
    print("review link: ", review_link)
    print(written_review)
    # print(written_review)
    # written_review = ""
    # time.sleep(2)
    # image = film.find('img', class_='image').attrs['src']
    # https://a.ltrbxd.com/resized/film-poster/5/1/9/3/9/51939-scarface-0-35-0-52-crop.jpg?v=e64e66a6b8
    # https://a.ltrbxd.com/resized/film-poster/5/1/9/3/9/51939-scarface-1983-0-70-0-105-crop.jpg
    # https://a.ltrbxd.com/resized/film-poster/4/5/2/2/8/452289-the-gentlemen-0-70-0-105-crop.jpg
    # https://a.ltrbxd.com/resized/film-poster/4/5/2/2/8/9/452289-the-gentlemen-0-70-0-105-crop.jpg?v=fe10998b1d 2x"
    id = film.find_all('div', class_="productiondetails")[0]
    new = id.find('div', class_="react-component").attrs['data-film-id']
    id_string = "/".join(f"{number}" for number in new)
    # print(id_string)
    image_link = f"https://a.ltrbxd.com/resized/film-poster/{id_string}/{new}-{title.lower().replace(' ', '-')}-0-70-0-105-crop.jpg"
    # print(image_link)
    # print(new)
    movie_data = { 
        "title": title, 
        "month": month,
        "year": year,
        "day": day,
        "slug": slug,
        "rating": rating,
        "written_review": written_review, 
        'image-link': image_link,
        'cached_at': datetime.now().isoformat()
    }
    
    # Cache the data
    set_cached_data('recent_movie', movie_data)
    
    return movie_data



def get_review(review_link): 
    soup = url_scrape("https://letterboxd.com/" + review_link)
    review = soup.find_all('p')
    return review[8].text
    
    # print(review)
# For local testing
if __name__ == "__main__":
    print(get_recent_movie())
# print(get_recent_movie())

def handler(event, context): 
    try:
        movie_data = get_recent_movie()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(movie_data)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
