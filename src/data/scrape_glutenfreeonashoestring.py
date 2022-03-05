"""Scrapes Glutenfree on a Shoestring blog."""
import json
import requests
from time import sleep
from random import randint
from bs4 import BeautifulSoup

from src.data.web_scraping import scrape_page_urls
from src.data.pickling import save_pickle


def clean_urls(urls):
    cleaned_urls = []

    for url in urls[:]:
        if url.startswith("https://glutenfreeonashoestring.com"):
            cleaned_urls.append(url)

    print(f"\nRetrieved {len(cleaned_urls)} links\n")

    return cleaned_urls


def get_recipe_info(url):
    recipe_dict = {}

    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')

    try:
        scripts = [item for item in soup.find("script", {"class": "yoast-schema-graph"})]
        scripts_json = json.loads(scripts[0])

        for nbr in range(0, len(scripts_json["@graph"])):
            if "recipeIngredient" in list(scripts_json["@graph"][nbr].keys()):
                recipe_info = scripts_json["@graph"][nbr]
                # TODO: use title instead of url
                recipe_dict[recipe_info["name"]] = recipe_info

                return recipe_dict
    except:
        recipe_dict[url] = ""


def scrape_shoestring_page(url):
    recipe_info = {}

    shoestring_urls = scrape_page_urls(url)
    shoestring_urls_clean = clean_urls(shoestring_urls)

    for url in shoestring_urls_clean:
        recipe_info[url] = get_recipe_info(url)
        # pause to prevent spamming their server
        sleep(randint(2, 10))

    return recipe_info


def scrape_all_shoestring_pages():
    all_recipes = {}

    # Each page's url is formatted the same way
    all_urls = [
        "https://glutenfreeonashoestring.com/gluten-free-recipes/?_paged=" + str(number)
        for number in range(1, 55)
    ]
    all_urls.append("https://glutenfreeonashoestring.com/gluten-free-recipes/")

    # this will take a while
    for url in all_urls:
        recipes = scrape_shoestring_page(url)
        all_recipes.update(recipes)

    save_pickle(all_recipes, "data/raw/shoestring_recipes.pickle")

    return all_recipes


if __name__ == "__main__":
    recipe_info = scrape_all_shoestring_pages()
