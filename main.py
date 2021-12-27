# Author: Hung Vu
# This script repeatedly make a call to IPM store
# to check for product availability.
import requests
import json
import sched
import time
from html.parser import HTMLParser
from datetime import datetime

response = requests.get("https://ipm.vn/products/horimiya-tap-8")
s = sched.scheduler(time.time, time.sleep)


class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        if ("Haravan.OptionSelectors" in data):
            # There is a space before "available", but it got lost after the parsing process
            start_index = data.index("{\"available\":")
            end_index = data.index("onVariantSelected") - 2
            product_status = json.loads(data[start_index: end_index])
            print("")
            print("#################" + str(datetime.now()))
            print("Product name: " + product_status["handle"])
            if (not product_status["available"]):
                print("Status: Out of stock")
            else:
                print("Status: Some specific variants are in stock")
                print("Variants:")
                print("")
                counter = 1
                for variant in product_status["variants"]:
                    print(counter)
                    counter += 1
                    print("Title: " + variant["title"])
                    print(
                        "Status: In stock" if variant["available"] else "Status: Out of stock")
                    if(variant["available"]):
                        # print("Regular price: " +
                        #       str(variant["compare_at_price"] / 100) + " VND")
                        print("Current price: " +
                              str(variant["price"] / 100) + " VND")
                        print("Available quantity: " +
                              str(variant["inventory_quantity"]))
                        # print("Original quantity: " +
                        #       str(variant["old_inventory_quantity"]))
                    print("")
                # s.enter(1, 1, self.feed, kwargs={"data": response.content.decode()})


parser = MyHTMLParser()

s.enter(1, 1, parser.feed, kwargs={"data": response.content.decode()})

s.run()
