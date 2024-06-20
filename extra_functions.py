import feedparser
import random

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
