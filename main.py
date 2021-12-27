# Author: Hung Vu
# This script repeatedly makes a call to IPM store
# to check for product availability.

import requests
import json
import sched
import time
import validators
from html.parser import HTMLParser
from datetime import datetime

# Sched order (?)
# 1. If 2 events have the same delay time, then an order is based on priority
# 2. If 2 events have the same delay time and priority, then an order is FCFS
# 3. If 2 events have different delay time, then it works based on provided time order


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
                        print("Current price: " +
                              str(variant["price"] / 100) + " VND")
                        print("Available quantity: " +
                              str(variant["inventory_quantity"]))
                    print("")

            # Add new response to schedule
            original_url = "https://ipm.vn/products/" + \
                product_status["handle"]
            response_dict[original_url] = requests.get(original_url)
            s.enter(interval, 1, self.feed, kwargs={
                    "data": response_dict[original_url].content.decode()})


# Main script
try:
    # TODO: Add license and copyright
    print("Created by Hung Vu")
    print("This script will monitor availability of your chosen IPM products automatically.")

    print("Press Ctrl + C to kill the script.")
    print("")

    url_list = []
    url_list_confirm = False
    interval = None
    response_dict = {}
    s = sched.scheduler(time.time, time.sleep)
    parser = MyHTMLParser()

    while(not url_list_confirm):
        choice = input("Enter URL of new IPM product or (Y) to confirm your list: ")
        print("")
        if(choice == "Y"):
            break
        elif(validators.url(choice) == True):
            url_list.append(choice)
            print("Your list of products:")
            for url in url_list:
                print(url)
        elif(isinstance(validators.url(choice), validators.utils.ValidationFailure)):
            print("Invalid URL. Please try again.")
        print("")

    while (interval == None):
        choice = input("Enter request interval (an integer, in seconds, min is 1): ")
        if(choice.isdigit() and int(choice) > 1):
            interval = int(choice)
            break
        else:
            print("Invalid choice. Please try again.")
        print("")

    for url in url_list:
        response_dict[url] = requests.get(url)
        s.enter(interval, 1, parser.feed, kwargs={
                "data": response_dict[url].content.decode()})

    s.run()

except KeyboardInterrupt:
    print("Process is terminated.")

except:
    print("Unknown error. Press Ctrl + C to exit and restart the script.")
