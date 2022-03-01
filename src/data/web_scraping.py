import urllib
from requests_html import HTML
from requests_html import HTMLSession


def create_search_url(search, url='https://google.com/search?q='):
    search_encoded = urllib.parse.quote_plus(search)
    full_url = url + search_encoded

    return full_url


def get_source(url):
    """Return the source code for the provided URL. 

    Args: 
        url (string): URL of the page to scrape.

    Returns:
        response (object): HTTP response object from requests_html. 
    """
    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def scrape_page_urls(url):
    response = get_source(url)
    links = list(response.html.absolute_links)

    # clean google urls
    google_domains = ('https://www.google.', 
                      'https://google.', 
                      'https://webcache.googleusercontent.', 
                      'http://webcache.googleusercontent.', 
                      'https://policies.google.',
                      'https://support.google.',
                      'https://maps.google.')

    for url in links[:]:
        if url.startswith(google_domains):
            links.remove(url)

    print(f"Retrieved {len(links)} links\n")

    return links
