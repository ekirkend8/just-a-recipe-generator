import json
import requests
from bs4 import BeautifulSoup
from web_scraping import scrape_page_urls


def clean_urls(urls):
    clean_urls = []

    for url in urls[:]:
        if url.startswith("https://glutenfreeonashoestring.com"):
            clean_urls.append(url)

    print(f"\nRetrieved {len(clean_urls)} links\n")

    return clean_urls


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


def main():
    recipe_info = {}

    shoestring_urls = scrape_page_urls('https://glutenfreeonashoestring.com/gluten-free-recipes/')
    shoestring_urls_clean = clean_urls(shoestring_urls)

    for url in shoestring_urls_clean:
        recipe_info[url] = get_recipe_info(url)

    return recipe_info


if __name__ == "__main__":
    recipe_info = main()
