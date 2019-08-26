import sys
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import requests
import json
import urllib


class Robot:
    def __init__(self):
        # https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options=options, executable_path="geckodriver")


def get_walmart_items_in_category(category="bikes"):
    robot = Robot()
    base_url = "https://www.walmart.com/search/?cat_id=0&facet=customer_rating%3A4+-+5+Stars||" \
               "pickup_and_delivery%3A2-Day+Shipping&query="
    query = category

    page_param = "&page="
    page_number = "1"

    full_url = base_url + query + page_param + page_number

    ELEMENT_CLASS1 = 'Grid-col'
    ELEMENT_CLASS2 = 'u-size-6-12'
    ELEMENT_CLASS3 = 'u-size-1-4-m'

    robot.browser.get(full_url)

    items = robot.browser.find_elements(By.XPATH, "//li[contains(@class,  '" +
                                  ELEMENT_CLASS1 + "') and contains(@class, '" +
                                  ELEMENT_CLASS2 + "') and contains(@class, '" +
                                  ELEMENT_CLASS3 + "')]")

    item_list = []
    for item in items:
        try:
            item_name = item.find_element_by_class_name('product-title-link').get_attribute('title')
            item_price = item.find_element_by_class_name('price-group').text
            item_list.append({"name": item_name, "walmart_price": float(item_price[1:])})
        except:
            pass

    robot.browser.quit()
    return item_list


def find_ebay_price(item_name):
    robot = Robot()
    ebay_base_url = "https://www.ebay.com/sch/i.html?&LH_BIN=1&_nkw="
    ebay_full_url = ebay_base_url + item_name
    robot.browser.get(ebay_full_url)
    prices = robot.browser.find_elements_by_class_name("s-item__price")

    price_count = 0
    avg_price = 0

    for price in prices:
        if price_count >= 9:
            break
        try:
            avg_price += float(price.text[1:price.text.find(" ")])
            price_count += 1
        except:
            pass

    robot.browser.quit()

    try:
        avg_price /= price_count
    except:
        return -1
    return avg_price


def find_market_price(item_name):
    '''
    checkaflip_url = "http://www.checkaflip.com/api"
    headers = { "Host": "www.checkaflip.com",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Length": "195",
                "Connection": "keep-alive",
                "Cookie": "SESSION=DZ9t7XI/cpTUre0qwjvxJWmZodcYgov3GzvNjDyezZnHJC9phaV5HJHmkDysEjqbv8Mi+dXqYnSkLAsJQOPxMD3Z4qv3w4abPgg/8XKjDRvL5fW3fX3z2GbepkMD1oSqUxre2Y0JCi8=; __utma=212496454.1086769493.1566794906.1566794906.1566794906.1; __utmb=212496454.5.10.1566794906; __utmc=212496454; __utmz=212496454.1566794906.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1",
                "Referer": "http://www.checkaflip.com/",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
                }

    params = 'json=' + urllib.parse.quote_plus('{"instance":"SearchCompleted","slot1":'
                                               '"Sceptre 50 Class FHD (1080P) LED TV (X505BV-FSR)",'
                                               '"slot2":false,"slot3":{"instance":"Returns"}}')

    # need parentheses ???
    params = params.replace("%28", "(")
    params = params.replace("%29", ")")
    print(params)

    resp = requests.post(checkaflip_url, params=params, headers=headers)
    print(resp)
    return float(json.loads(resp.text)['slot1'])
    '''

    robot = Robot()
    robot.browser.get("http://www.checkaflip.com/")
    time.sleep(2)
    robot.browser.find_element_by_id("query").click()
    time.sleep(1)
    robot.browser.find_element_by_id("query").clear()
    robot.browser.find_element_by_id("query").send_keys(item_name)

    time.sleep(1)
    '''
    while robot.browser.find_element_by_class_name("btn-default dropdown-toggle").get_attribute("value") != "new":
        robot.browser.find_element_by_class_name("btn-default dropdown-toggle").__setattr__("value", "new")
        print(robot.browser.find_element_by_class_name("btn-default dropdown-toggle").get_attribute("value"))
    '''

    robot.browser.find_element_by_class_name("btn-default").__setattr__("value", "New")
    robot.browser.execute_script('document.getElementsByClassName("btn btn-default dropdown-toggle")[0]'
                                 '.innerHTML="New";')

    time.sleep(1)

    robot.browser.find_element_by_id("submit").click()
    robot.browser.find_element_by_id("submit").click()

    time.sleep(2)

    price = ""

    count = 0
    while True and (price == "" or price == None or price == 'calculating...'):
        price = robot.browser.find_element_by_id("complavgprice").text

    if price == "" or price == None:
        price = -1

    robot.browser.quit()
    return float(price)


def find_arbs(category="bikes"):
    # get wmt data
    items = get_walmart_items_in_category(category=category)
    print('Got items!')

    arbs = []

    # get ebay pricing
    for item in items:
        print(item['name'])
        item['ebay_price'] = find_market_price(item['name'])
        print("Prices | Walmart: " + str(item['walmart_price']) + " / eBay: " + str(item['ebay_price']))

        # determine if arb opportunity exists
        margin = 0.15
        if item['ebay_price'] > item['walmart_price'] * (1+margin):
            arbs.append(item)

    print("\n Arbs found: ")
    print(arbs)


if __name__ == "__main__":
    category = "tv"
    if len(sys.argv) >= 1:
        category = sys.argv[1]
    find_arbs(category=category)
    # print(find_market_price('Sceptre 50" Class FHD (1080P) LED TV (X505BV-FSR)'))