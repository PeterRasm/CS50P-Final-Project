"""
    Collection of the webservice calls used by project.

    ws_get_price:       Prepare to call webservice to retrieve price of gasolin
    ws_get_car_models:  Prepare to call webservice to retrieve valid car models for make and year
    ws_validate_car:    Prepare to call webservice to validate car and retrieve car id
    ws_get_car_details: Call webservice to retrieve mpg figures for car
    ws_call_url:        Call the web service
    ws_no_connection:   Switch what-to-do if connection fails. Used to switch on default
                        value for testing without internet connection.

"""

import requests
import re
from sys import exit

BASE_URL = "https://www.fueleconomy.gov/ws/rest/"

def ws_get_price():
    """ Get price from web service """
    # Using 'r' to create 'raw' string literal
    # In this case no need for r string though, f string can also be used here
    # r string preserves special characters like \n etc
    url = f'{BASE_URL}fuelprices'

    status_code, ws_text = call_url(url)

    #print(status_code)
    #print(ws_text)

    # In case no internet connection
    # Use for testing
    if status_code == 999:
        print("* Internet connection failed ....")
        print("* Using default $5.00 as price per gallon *")
        print()
        return 5.0

    if match := re.search(".+<regular>([0-9]+\.[0-9]+).*", ws_text):
        price = float(match.group(1))
        return price
    else:
        print("No price found")
        exit(21)

def ws_get_car_models(_make, _year):
    # Retrieve valid car models from car database
    url = f'{BASE_URL}vehicle/menu/model?year={_year}&make={_make}'

    status_code, ws_text = call_url(url)

    #print(status_code)
    #print(ws_text)

    if status_code == 200:
        models = []
        #print(ws_text.split("<menuItem>"))
        for item in ws_text.split("<menuItem>"):
            #print(item)
            if  match := re.search("<text>(.+)</text>.+", item):
                models.append(match.group(1))
        return models

    # No internet connection or models not found
    if status_code in (0, 999):
        return []
  

def ws_validate_car(_make, _model, _year):
    # Find car id from car database
    #url = r'https://www.fueleconomy.gov/ws/rest/vehicle/menu/options?year=2019&make=Honda&model=Pilot AWD'
    url = f'{BASE_URL}vehicle/menu/options?year={_year}&make={_make}&model={_model}'
    
    status_code, ws_text = call_url(url)

    #print(status_code)
    #print(ws_text)

    if status_code == 200:
        if  match := re.search(".+<value>([0-9]+)</value>.+", ws_text) :
            return int(match.group(1))

    # Test mode, no internet connection
    if status_code == 999:
        return 999

    # return value 0 when valid car was not found
    return 0        


def ws_get_car_details(car_id):
    """ Get the car details (correct name presentation and mpg) using car_id """
    url = f'{BASE_URL}vehicle/{car_id}'
    
    status_code, ws_text = call_url(url)

    #print(status_code)
    #print(ws_text)

    if status_code == 200:
        # Note to self: regex search pattern can span multiple lines like this
        # Note to self: The string elements will be concatenated 
        # Find also make and model to show correct upper/lower case in output
        if  match := re.search(".+<city08>([0-9]+)</city08>"             # mpg_cty
                               ".+<highway08>([0-9]+)</highway08>"       # mpg_hwy
                               ".+<make>(.+)</make>"                     # make for presentation
                               ".+<model>(.+)</model>",                  # model for presentation
                               ws_text) :
            return int(match.group(1)),int(match.group(2)), match.group(3), match.group(4)
    else:
        raise ConnectionError
    

def call_url(url):

    try:
        r = requests.get(url, timeout=2)
    except requests.ConnectionError:
        # If no connection, action is setup in no_connection()
        return no_connection("Connection Error")
    except requests.ReadTimeout:
        return no_connection("Timeout Error")
    
    #print(r.status_code, r.text)
    return r.status_code, r.text


def no_connection(message):
    """ 
    Define here what happens if connection fails
    Makes testing easier by switching behavior in one place
    """
    # Switch on/off the 'return' for testing/no-testing

    #test_mode = True
    test_mode = False

    if test_mode:
        return 999, "No connection, test mode"
    else:
        print("Connection failed:", message)
        exit(20)


