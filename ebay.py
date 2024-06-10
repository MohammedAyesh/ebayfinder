import json
import math
import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Union
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import dateutil
from nested_lookup import nested_lookup
from loguru import logger as log
from scrapfly import ScrapeApiResponse, ScrapeConfig, ScrapflyClient, ScrapflyScrapeError
import pandas as pd

SCRAPFLY_KEY = ""
SCRAPFLY = ScrapflyClient(key=SCRAPFLY_KEY)
BASE_CONFIG = {
    "asp": True,
    "country": "US",
    "lang": ["en-US"],
}

def _find_json_objects(text: str, decoder=json.JSONDecoder()):
    pos = 0
    while True:
        match = text.find("{", pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1

def clean_price(price: Union[str, int, float]) -> float:
    """Remove non-numeric characters from price string and convert to float."""
    if isinstance(price, (int, float)):
        return float(price)
    clean_price = ''.join(c for c in price if c.isdigit() or c == '.')
    return float(clean_price)

def parse_variants(result: ScrapeApiResponse) -> dict:
    script = result.selector.xpath('//script[contains(., "MSKU")]/text()').get()
    if not script:
        return {}
    all_data = list(_find_json_objects(script))
    data = nested_lookup("MSKU", all_data)[0]
    selection_names = {}
    for menu in data["selectMenus"]:
        for id_ in menu["menuItemValueIds"]:
            selection_names[id_] = menu["displayLabel"]
    selections = []
    for v in data["menuItemMap"].values():
        selections.append(
            {
                "name": v["valueName"],
                "variants": v["matchingVariationIds"],
                "label": selection_names[v["valueId"]],
            }
        )
    results = []
    variant_data = nested_lookup("variationsMap", data)[0]
    for id_, variant in variant_data.items():
        result = defaultdict(list)
        result["id"] = id_
        for selection in selections:
            if int(id_) in selection["variants"]:
                result[selection["label"]] = selection["name"]
        result["price_original"] = int(clean_price(variant["binModel"]["price"]["value"]["convertedFromValue"]))
        result["price_original_currency"] = variant["binModel"]["price"]["value"]["convertedFromCurrency"]
        result["price_converted"] = int(clean_price(variant["binModel"]["price"]["value"]["value"]))
        result["price_converted_currency"] = variant["binModel"]["price"]["value"]["currency"]
        result["out_of_stock"] = variant["quantity"]["outOfStock"]
        results.append(dict(result))
    return results

def parse_product(result: ScrapeApiResponse, min_price: int):
    sel = result.selector
    css_join = lambda css: "".join(sel.css(css).getall()).strip()
    css = lambda css: sel.css(css).get("").strip()
    item = {}
    item["url"] = css('link[rel="canonical"]::attr(href)')
    item["id"] = item["url"].split("/itm/")[1].split("?")[0]
    price_original = css(".x-price-primary>span::text")
    if price_original:
        item["price_original"] = int(clean_price(price_original))
    else:
        item["price_original"] = None
    price_converted = css(".x-price-approx__price ::text")
    if price_converted:
        item["price_converted"] = int(clean_price(price_converted))
    else:
        item["price_converted"] = None
    item["name"] = css_join("h1 span::text")
    item["seller_name"] = css_join("[data-testid=str-title] a ::text")
    item["seller_url"] = css("[data-testid=str-title] a::attr(href)").split("?")[0]
    item["photos"] = sel.css('.ux-image-filmstrip-carousel-item.image img::attr("src")').getall()
    item["photos"].extend(sel.css('.ux-image-carousel-item.image img::attr("src")').getall())
    item["description_url"] = css("div.d-item-description iframe::attr(src)")
    if not item["description_url"]:
        item["description_url"] = css("div#desc_div iframe::attr(src)")
    feature_table = sel.css("div.ux-layout-section--features")
    features = {}
    for ft_label in feature_table.css(".ux-labels-values__labels"):
        label = "".join(ft_label.css(".ux-textspans::text").getall()).strip(":\n ")
        ft_value = ft_label.xpath("following-sibling::div[1]")
        value = "".join(ft_value.css(".ux-textspans::text").getall()).strip()
        features[label] = value
    item["features"] = features

    # Ignore listings where the price is less than the min_price
    if item["price_converted"] and item["price_converted"] < int(min_price):
        log.info(f"Product {item['id']} ignored due to price {item['price_converted']} being less than {min_price}")
        return None

    return item

async def fetch_description(description_url: str) -> str:
    """Fetch the product description from the given iframe URL."""
    description_page = await SCRAPFLY.async_scrape(ScrapeConfig(description_url, **BASE_CONFIG))
    sel = description_page.selector
    description = "".join(sel.css("body *::text").getall()).strip()
    return description

async def scrape_product(url: str, min_price: int) -> Dict:
    page = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    product = parse_product(page, min_price)

    if product is None:
        return None

    if product["description_url"]:
        try:
            description = await fetch_description(product["description_url"])
            product["description"] = description
        except Exception as e:
            log.error(f"Failed to fetch description from {product['description_url']}: {e}")
            product["description"] = None
    else:
        product["description"] = None

    product["variants"] = parse_variants(page)
    return product

def parse_search(result: ScrapeApiResponse, start_index: int = 1, min_price: int = 1) -> List[Dict]:
    previews = []
    index = start_index
    for box in result.selector.css(".srp-results li.s-item"):
        css = lambda css: box.css(css).get("").strip() or None
        css_re = lambda css, pattern: box.css(css).re_first(pattern, default="").strip()

        auction = css(".s-item__auction")
        auction_end = css_re(".s-item__time-end::text", r"\((.+?)\)") or None

        # Ignore auction listings
        if auction or auction_end:
            log.info(f"Listing ignored because it's an auction.")
            continue

        price = css(".s-item__price::text")
        if price:
            try:
                price = int(clean_price(price))
            except ValueError:
                price = None
        else:
            price = None

        # Ignore listings where the price is less than the min_price
        if price and int(price) < int(min_price):
            log.info(f"Listing ignored due to price {price} being less than {min_price}")
            continue

        item = {
            "index": index,
            "url": css("a.s-item__link::attr(href)").split("?")[0],
            "title": css(".s-item__title span::text"),
            "price": price,
            "location": css(".s-item__itemLocation::text"),
            "photo": box.css("img::attr(data-src)").get() or box.css("img::attr(src)").get(),
            "condition": css(".SECONDARY_INFO::text"),
        }
        previews.append(item)
        index += 1
    return previews

def _get_url_parameter(url: str, param: str, default=None) -> Optional[str]:
    query_params = dict(parse_qsl(urlparse(url).query))
    return query_params.get(param) or default

def _update_url_param(url: str, **params):
    parsed_url = urlparse(url)
    query_params = dict(parse_qsl(parsed_url.query))
    query_params.update(params)
    updated_url = parsed_url._replace(query=urlencode(query_params))
    return urlunparse(updated_url)

async def scrape_search(url: str, min_price: int, max_pages: Optional[int] = None, start_index: int = 1) -> List[Dict]:
    log.info("Scraping search for {}", url)
    first_page = await SCRAPFLY.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    results = parse_search(first_page, start_index, min_price)
    total_results = first_page.selector.css(".srp-controls__count-heading>span::text").get()
    total_results = int(total_results.replace(",", "").replace(".", ""))
    items_per_page = int(_get_url_parameter(first_page.context["url"], "_ipg", default=60))
    total_pages = math.ceil(total_results / items_per_page)
    if max_pages and total_pages > max_pages:
        total_pages = max_pages
    other_pages = [
        ScrapeConfig(_update_url_param(first_page.context["url"], _pgn=i), **BASE_CONFIG)
        for i in range(2, total_pages + 1)
    ]
    log.info("Scraping search pagination of {} total pages for {}", len(other_pages), url)
    next_index = start_index + len(results)
    async for result in SCRAPFLY.concurrent_scrape(other_pages):
        if not isinstance(result, ScrapflyScrapeError):
            try:
                results.extend(parse_search(result, next_index, min_price))
                next_index += len(results)
            except Exception as e:
                log.error(f"failed to parse search: {result.context['url']}: {e}")
        else:
            log.error(f"failed to scrape {result.api_response.config['url']}, got: {result.message}")
    return results

def display_table(data: List[Dict]):
    df = pd.DataFrame(data)
    print(df)

# Example usage
if __name__ == "__main__":
    import asyncio

    if len(sys.argv) < 2:
        print("Usage: python script.py <min_price>")
        sys.exit(1)

    min_price = int(sys.argv[1])  # Get the minimum price from command-line arguments

    async def run():
        search_url = "https://www.ebay.com/sch/i.html?_nkw=macbook&_ipg=60"
        results = await scrape_search(search_url, min_price=min_price, max_pages=1)
        display_table(results)
        single_product_result = await scrape_product("https://www.ebay.com/itm/332562282948", min_price=min_price)
        print(single_product_result)
        variant_product_result = await scrape_product("https://www.ebay.com/itm/393531906094", min_price=min_price)
        print(variant_product_result)

    asyncio.run(run())
