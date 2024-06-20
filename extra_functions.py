import random

from gpiozero import RGBLED
import requests
import feedparser


def set_light_color(red, green, blue):
    '''
    Set the color of a full color light device. Returns True on success.
    The color is represented as the lightness red, green, and blue components.
    Setting the color to (0, 0, 0) effectively turns the light off.

    :param int red: Lightness of the red component (0 to 100).
    :param int green: Lightness of the green component (0 to 100).
    :param int blue: Lightness of the blue component (0 to 100).
    '''

    global _led_controller

    if '_led_controller' not in globals():
        _led_controller = RGBLED('GPIO21', 'GPIO20', 'GPIO26')

    _led_controller.color = (red / 100, green / 100, blue / 100)

    return True


def get_news():
    '''
    Get news headlines.
    '''
    feed = feedparser.parse('https://rss.nytimes.com/services/xml/rss/nyt/US.xml')

    news_list = []

    if feed.status != 200:
        return { 'error': 'Error when fetching news headlines from NYTimes' }

    for entry in feed.entries:
        news_list.append({
            "title": entry['title'],
            "summary": entry['summary'],
            "time_published": entry['published'],
            "tags": [i['term'] for i in entry['tags']],
        })

    return news_list


def mystore_query_product(product_name):
    '''
    Search for products on MyStore.
    The function will return the matched product ID and price.

    :param str product_name: The keyword to search for, e.g., "PC keyboard".
    '''
    product_id = random.randint(0, 9999)
    price = random.randint(1, 99)

    return {
        'product_id': product_id,
        'price': price,
    }


def mystore_submit_order(product_id, count):
    '''
    Submit an order on MyStore.

    :param int product_id: Product ID of the item to buy.
    :param int count: The count of the item to buy.
    '''
    order_id = random.randint(1000000, 9999999)

    return {
        'shopping_list': [product_id] * count,
        'order_id': order_id,
        'status': 'success',
    }


def search_locations(query):
    '''
    Search for places and location.
    Returns a list of matched locations.

    :param str query: Search query, can be any place name or even postal code.
    '''

    global _arcgis_magic_keys

    if '_arcgis_magic_keys' not in globals():
        _arcgis_magic_keys = {}

    req = requests.get(
        "https://geocode.arcgis.com"
        "/arcgis/rest/services/World/GeocodeServer/suggest",
        params={
            'f': 'json',
            'countryCode': 'USA,PRI,VIR,GUM,ASM',
            'maxSuggestions': '10',
            'text': query,
        }
    )

    candidates = []

    for place in req.json()['suggestions']:
        if not place['isCollection']:
            _arcgis_magic_keys[place['text']] = place['magicKey']
            candidates.append(place['text'])

    return req.json()['suggestions']


def get_weather_forecast(location):
    '''
    Get weather forecast.
    Returns the XML weather forecast from the National Weather Service.

    :param str location:
        Location. Should be a place name returned by `search_locations`.
    '''

    global _arcgis_magic_keys

    if '_arcgis_magic_keys' not in globals():
        _arcgis_magic_keys = {}

    req = requests.get(
        "https://geocode.arcgis.com"
        "/arcgis/rest/services/World/GeocodeServer/findAddressCandidates",
        params = {
            'f': 'json',
            'singleLine': location,
            'magicKey': _arcgis_magic_keys.get(location, ''),
        }
    )

    json_data = req.json()
    coord = json_data['candidates'][0]['location']

    req = requests.get(
        'https://forecast.weather.gov/MapClick.php',
        params = {
            'lat': str(coord['y']),
            'lon': str(coord['x']),
            'FcstType': 'dwml',
        }
    )

    return req.text
