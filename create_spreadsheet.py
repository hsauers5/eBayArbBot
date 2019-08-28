import csv
import json


def create_spreadsheet(items_list="items.json"):
    items = []
    with open('flips.csv', 'w') as csv_file:
        csv_file.write('Name, Walmart_Price, Ebay_Price, Difference, Margin, Percent_Sold, Num_Sold\n')
        with open(items_list, 'r') as json_file:
            for row in json.load(json_file):
                item = row
                items.append(item)
                csv_file.write(item['name'].replace(',', '') + ',' + str(item['walmart_price'])
                               + ',' + str(item['ebay_price']) + ',' + str(item['ebay_price'] - item['walmart_price'])
                               + ',' + str((item['ebay_price'] - item['walmart_price'])/item['walmart_price'])
                               + ',' + str(item['percent_sold']) + ',' + str(item['num_sold']) + '\n')

        print(items)


if __name__ == "__main__":
    create_spreadsheet()