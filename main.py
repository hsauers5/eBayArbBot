import sys
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class Robot:
    def __init__(self):
        # https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options=options, executable_path="geckodriver")


def get_walmart_items_in_category(category="bikes"):
    robot = Robot()
    base_url = "https://www.walmart.com/search/?cat_id=0&search_redirect=false&grid=true&facet=customer_rating%3A4+-+5+Stars||" \
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


# gets average asking price on ebay - skews too high
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


def find_market_data(item_name):
    robot = Robot()
    robot.browser.get("http://www.checkaflip.com/")
    time.sleep(2)
    robot.browser.find_element_by_id("query").click()
    time.sleep(1)
    robot.browser.find_element_by_id("query").clear()
    robot.browser.find_element_by_id("query").send_keys(item_name)

    time.sleep(1)

    robot.browser.find_element_by_class_name("btn-default").__setattr__("value", "New")
    robot.browser.execute_script('document.getElementsByClassName("btn btn-default dropdown-toggle")[0]'
                                 '.innerHTML="New";')

    time.sleep(1)

    robot.browser.find_element_by_id("submit").click()
    robot.browser.find_element_by_id("submit").click()

    time.sleep(2)

    price = ""
    percent_sold = ""

    count = 0
    while True and (price == "" or price == None or price == 'calculating...'):
        if count >= 15:
            price = -1
            break
        price = robot.browser.find_element_by_id("complavgprice").text
        count += 1

    count = 0
    while True and (percent_sold == "" or percent_sold == None or percent_sold == 'calculating...'):
        if count >= 15:
            percent_sold = -1
            break
        percent_sold = robot.browser.find_element_by_id("percentsold").text
        count += 1

    if price == "" or price == None:
        price = -1

    num_sold = len(robot.browser.find_element_by_id('completed-listings').find_elements_by_class_name('listing'))

    robot.browser.quit()
    return [float(price), float(percent_sold), float(num_sold)]


def find_arbs(category="bikes"):
    # get wmt data
    items = get_walmart_items_in_category(category=category)
    print('Got items!')

    arbs = []

    # get ebay pricing
    for item in items:
        print(item['name'])
        '''
        item_data = []
        try:
            item_data = find_market_data(item['name'])
        except:
            try:
                item_data = find_market_data(item['name'])
            except:
                item_data = [-1, -1, -1]
        '''
        item_data = find_market_data(item['name'])

        item['ebay_price'] = item_data[0]
        item['percent_sold'] = item_data[1]
        item['num_sold'] = item_data[2]

        print("Prices | Walmart: " + str(item['walmart_price']) + " / eBay: " + str(item['ebay_price']) + " | "
              + "Percent Sold: " + str(item['percent_sold']) + " Num Sold: " + str(item['num_sold']))

        # determine if arb opportunity exists
        margin = 0.15
        if item['ebay_price'] > item['walmart_price'] * (1+margin):
            arbs.append(item)

    print("\n Arbs found: ")
    print(arbs)
    return arbs


if __name__ == "__main__":

    category = "tv"
    if len(sys.argv) >= 1:
        category = sys.argv[1]
    my_arbs = find_arbs(category=category)

    with open("items.json", "w") as json_file:
        json_file.write(json.dumps(my_arbs))

    import create_spreadsheet
    create_spreadsheet.create_spreadsheet()