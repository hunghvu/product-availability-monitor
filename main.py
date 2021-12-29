# Author: Hung Vu
# This script will monitor product availability
# of some specfic publishers and retailers.

# Copyright 2021 Hung Huu Vu.
# Licensed under the MIT License.

import enum
import json
import re
import requests
import sched
import time
import validators
# import traceback
from datetime import datetime


class Publisher(enum.Enum):
    kim_dong = 1
    ipm_full_info = 2
    ipm_partial_info = 3
    tiki = 4


def ipm_response_handler(html_response):
    original_url = re.search(
        "rel=\"canonical\" href=\"(.+?)\"", html_response).group(1)
    product_status = None
    if ("Haravan.OptionSelectors" in html_response):
        # There is a space before "available", but it got lost after the parsing process
        start_index = html_response.index("{ product: {\"available\":") + 11
        end_index = html_response.index("onVariantSelected") - 2
        product_status = json.loads(html_response[start_index: end_index])
        display_result(product_status, original_url, Publisher.ipm_full_info)
    else:
        start_index = html_response.index("{\"page\"")
        end_index = html_response.index("for (var attr in meta) {") - 2
        product_status = json.loads(
            html_response[start_index: end_index])["product"]
        display_result(product_status, original_url,
                       Publisher.ipm_partial_info)

    response_dict[original_url] = requests.get(original_url)
    s.enter(interval, 1, ipm_response_handler, kwargs={
            "html_response": response_dict[original_url].content.decode()})


def kim_dong_response_handler(product_status):
    """
        Handle JSON response from Kim Dong
    """
    original_url = "https://nxbkimdong.com.vn/products/" + \
        product_status["handle"]
    request_url = original_url + ".js"
    display_result(product_status, original_url, Publisher.kim_dong)
    response_dict[original_url] = requests.get(request_url)
    s.enter(interval, 1, kim_dong_response_handler, kwargs={
        "product_status": json.loads(response_dict[original_url].content.decode())})


def tiki_response_handler(product_status):
    """
        Handle JSON response from Tiki
    """
    original_url = "https://tiki.vn/" + product_status["url_path"]
    p_key = product_status["url_key"].split("-")[-1].replace("p", "")
    pid_key = product_status["url_path"].split("=")[1]
    request_url = "https://tiki.vn/api/v2/products/" + \
        p_key + "?platform=web&pid=" + pid_key
    display_result(product_status, original_url, Publisher.tiki)
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"}
    response_dict[original_url] = requests.get(request_url, headers=headers)
    s.enter(interval, 1, tiki_response_handler, kwargs={
        "product_status": json.loads(response_dict[original_url].content.decode())})


def display_result(product_status, original_url, publisher: Publisher):
    """
        Show results to user
    """
    print()
    print("#################" + str(datetime.now()))
    if (publisher in [Publisher.kim_dong, Publisher.ipm_full_info]):
        print("Product name: " + product_status["handle"])
        print("URL:", original_url)
        if (not product_status["available"]):
            print("Status: Out of stock")
        else:
            print("Status: Some specific variants are in stock")
            print("Variants:")
            print()
            counter = 1
            for variant in product_status["variants"]:
                print(
                    counter, "-", variant["title"] if publisher in [
                        Publisher.ipm_full_info] else product_status["title"],
                    "- In stock" if variant["available"] else "- Out of stock")
                counter += 1

                if(variant["available"]):
                    print("Current price:",
                          str(variant["price"] / 100), "VND")
                    print("Available quantity:",
                          str(variant["inventory_quantity"]))
                print()
    elif (publisher in [Publisher.ipm_partial_info]):
        print("Product name: " + product_status["title"])
        print("URL:", original_url)
        print(
            "Status: In stock" if product_status["available"] else "Status: Out of stock")
        print("Current price:",
              str(product_status["price"] / 100), "VND")
        print("Available quantity: Unknown")
    elif(publisher in [Publisher.tiki]):
        print("Product name: " + product_status["name"])
        print("URL:", original_url)
        inventory_type = product_status["inventory_type"]
        if(inventory_type == "cross-border"):
            print("Status: From global seller - products is transported from abroad")
        elif (inventory_type == "instock"):
            print("Status: In stock - products in TIKI storage, TIKI pack, TIKI deliver")
        elif (inventory_type == "backorder"):
            print(
                "Status: Backorder - products in seller storage, TIKI pack, TIKI deliver")
        elif(inventory_type == "seller_backorder"):
            print(
                "Status: Seller backorder - products in seller storage, seller pack, seller deliver")
        elif(inventory_type == "drop_ship"):
            print(
                "Status: Drop ship - products in seller storage, seller pack, TIKI deliver")
        elif(inventory_type == "preorder"):
            print("Status: Preorder")

        print("Current price:", product_status["price"], "VND")
        print("Available quantity: Unknown")


# Main script
try:
    print("\u00a9", datetime.now().year, "Hung Huu Vu.")
    print("Licensed under the MIT License.")
    print("Source code: https://github.com/hunghvu/product-availability-monitor")
    print()

    print("This script will monitor availability of your chosen products.")
    print("Currently, only Kim Dong, IPM, and Tiki are supported.")

    print("Press Ctrl + C to exit the program.")
    print()

    url_list = []
    url_list_confirm = False
    interval = None
    response_dict = {}
    s = sched.scheduler(time.time, time.sleep)

    while(not url_list_confirm):
        choice = input(
            "Enter URL of a new product or (Y) to confirm your list: ")
        print()
        if(choice == "Y"):
            if (len(url_list) > 0):
                break
            print("Your list of product cannot be empty. Please try again.")
        elif(validators.url(choice) == True and (
            "https://ipm.vn/" in choice
            or "https://nxbkimdong.com.vn/" in choice
            or "https://tiki.vn/" in choice
        )):
            url_list.append(choice)
            print("Your list of products:")
            for url in url_list:
                print(url)
        else:
            print("Invalid URL. Please try again.")
        print()

    while (interval == None):
        choice = input(
            "Enter request interval (an integer, in seconds, min is 1): ")
        if(choice.isdigit() and int(choice) >= 1):
            interval = int(choice)
            break
        else:
            print("Invalid choice. Please try again.")
        print()

    for url in url_list:
        if ("https://ipm.vn/" in url):
            response_dict[url] = requests.get(url)
            s.enter(interval, 1, ipm_response_handler, kwargs={
                "html_response": response_dict[url].content.decode()})

        elif("https://nxbkimdong.com.vn/" in url):
            response_dict[url] = requests.get(url + ".js")
            s.enter(interval, 1, kim_dong_response_handler, kwargs={
                    "product_status": json.loads(response_dict[url].content.decode())})

        elif("https://tiki.vn/" in url):
            p_key = re.search("-p([0-9]+?).html", url).group(1)
            pid_key = url[url.index("pid=") + 4:]
            request_url = "https://tiki.vn/api/v2/products/" + \
                p_key + "?platform=web&pid=" + pid_key
            headers = {  # Bypass 403 response
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"}
            response_dict[url] = requests.get(request_url, headers=headers)
            s.enter(interval, 1, tiki_response_handler, kwargs={
                    "product_status": json.loads(response_dict[url].content.decode())})

    s.run()

except KeyboardInterrupt:
    print("Process is terminated.")

except Exception as error:
    # traceback.print_exc()
    print("Unknown error, require restart. If the script does not automatically exit, press Ctrl + C.")
