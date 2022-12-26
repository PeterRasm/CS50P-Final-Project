""" 
    Calculates price of the total gas comsumption for a distance for one or more cars.

    This is the final project of CS50P

    List of arguments (optional)
    mpg:   -- The car's mileage, cty/hwy
    miles: -- Distance in miles
    price: -- Gas price

    List of functions:
    main():      Controlling flow
    read_argv(input): Validates argument to program and populates dict with
                 the individual parameters/values
    get_miles(): If 'miles' is missing as input, user is prompted for the 
                 distance to be used for the calculations
    calculate_cost(miles, mpg_cty, mpg_hwy, price): Calculates the cost
    print_cost_single(arg_dict, car): If mpg is given directly as argument,
                 cost is calculated on that mpg only and displayed in
                 simple form
    print_table(cars, miles, price): If one or more cars are added during
                 the program, the output is displayed in form of a table
                 including some car details.
    print_csv(cars, miles, price): If one or more cars are added during
                 the program, in addition to the output on screen, the 
                 car details and cost calculations are saved in csv file
    connection_error: Central message to output in case of connection error

    Example: 
    python project.py mpg:22/25 miles:237 price:4.5

    If 'mpg' is given as argument, the program is a simpel calculator using the 
    mileage, distance and gas price to calculate the average cost.
    
    If 'mpg' is not given as argument, the user will be prompted to enter car make, 
    model and year and a distance to use for the calculation. The user can enter as 
    many cars as he/she wants, the prompt for a new car will stop when user enters 
    CMD-D/CTRL-D.

    Each car entry will be validated against https://www.fueleconomy.gov/ws/rest/vehicle/
    and the mileage for each car will be retrieved. If the data entered does not match with
    a car make/model/year in the database of www.fueleconomy.gov the user will be notified
    with an option to correct the data input.

    If the argument for miles is missing, the user will be prompted for the distance 
    to use in the calculation.

    If the argument for 'price' is missing, the gas price for 'regular' will be retrieved
    from https://www.fueleconomy.gov/ws/rest/fuelprices.

    The entered cars will be compared and listed on-screen as well as stored in a 
    csv file called 'cars.csv'
"""

from sys import argv, exit
import csv, tabulate
from car_class import CAR
from call_ws import ws_get_price
from datetime import datetime

#print(CAR.__doc__)

CSV_NAME = "cars.csv"

def main():
    # Dictionary of the arguments 
    arg_dict = read_argv(argv[1:])
    
    if "mpg" in arg_dict:
        # Skip the car instance, print cost and exit program
        print_cost_single(arg_dict, arg_dict["mpg"]["cty"], arg_dict["mpg"]["hwy"])
        exit(0)

    # Declare empty list for cars
    cars = []

    print()
    print("Enter cars, end list with CTRL-D ....")
    print()

    while True:
        # Add cars to list
        try:
            car = CAR.get_newcar()
        except ValueError as error:
            # Pass on the error message and prompt input again
            print('\n', error, '\n')
            continue
        except ConnectionError:
            connection_error()
        except EOFError:
            break
        
        print(car)
        cars.append(car)
    
    # User pressed CTRL-D to end input of more cars
    print(".....")
    print()
    if len(cars) == 0:
        exit("No cars selected ....")
    else:
        print_table(cars, arg_dict["miles"], arg_dict["price"])
        print_csv(cars, arg_dict["miles"], arg_dict["price"])


def read_argv(input):
    """ Read, validate and return individual arguments as dictionary """
    if len(input) > 3:
        print("Error: Too many arguments")
        exit(1)

    tmp_dict = {}
    
    for arg in input:
        #print(arg)
        if ':' not in arg:
            print("Error: Invalid format, missing colon")
            exit(1)

        arg_list = arg.split(":") 

        # Check if same parameter is used multiple times
        if arg_list[0] in tmp_dict:
            print("Error: Same argument used two or more times")
            exit(2)

        # Add argument to dictionary and validate numerical values
        # Could have used if..else but match..case gives better readability
        # when having multiple "cases"
        match arg_list[0]:
            case "miles":
                try:
                    tmp_dict["miles"] = int(arg_list[1])
                except ValueError:
                    print("Error: Miles must be an integer")
                    exit(3)
            case "price":
                try:
                    tmp_dict["price"] = float(arg_list[1])
                except ValueError:
                    print("Error: Price must be a decimal number (float)")
                    exit(4)
            case "mpg":
                try:
                    cty, hwy = arg_list[1].split('/')
                    tmp_dict["mpg"] = {"cty":int(cty), "hwy":int(hwy)}
                except (ValueError, IndexError):
                    print("Error: Mpg must be two integers separated with a '/'")
                    exit(5)
            case _:
                print("Error: Argument not recognized")
                exit(6)
                
    # Missing 'miles' / 'price'
    for arg in ("miles", "price"):
        if arg not in tmp_dict:
            match arg:
                case "miles":
                    tmp_dict["miles"] = get_miles()
                case "price":
                    tmp_dict["price"] = ws_get_price()

    return tmp_dict


def get_miles():
    """ Get miles as user input, if not given as argument to program """
    print()
    while True:
        try:
            tmp_miles = int(input("Distance in miles: "))
        except ValueError:
            continue
        if tmp_miles > 0:
            break
    print()
    return tmp_miles


def calculate_cost(miles, mpg_cty, mpg_hwy, price):
    """ 
    Calculate average cost based on miles, mpg and price 
    If only one mpg is given, use that value 
    If both mpg types are given, use average mpg 
    """
    if mpg_cty == 0 or  mpg_hwy == 0:
        cost = miles / (mpg_cty + mpg_hwy) * price
    else:
        cost = miles / (mpg_cty + mpg_hwy) * 2 * price

    return cost


def print_cost_single(arg_dict, mpg_cty, mpg_hwy):
    """ Show cost of gasolin for distance and mileage provided by user """

    print()
    print(f"Gas price: ${arg_dict['price']:.2f} per gallon")
    print()
    print(f"The cost in gas for driving {arg_dict['miles']} miles will in average be: ")
    print(f"    - driving in city    ({mpg_cty} mpg): ", end='')
    cost = calculate_cost(arg_dict['miles'], mpg_cty, 0, arg_dict['price'])
    print(f"${cost:.2f}")
    print(f"    - driving on highway ({mpg_hwy} mpg): ", end='')
    cost = calculate_cost(arg_dict['miles'], 0, mpg_hwy, arg_dict['price'])
    print(f"${cost:.2f}")
    print(f"    - mixed driving              : ", end='')
    cost = calculate_cost(arg_dict['miles'], mpg_cty, mpg_hwy, arg_dict['price'])
    print(f"${cost:.2f}")
    print()


def print_table(cars, miles, price):
    """ Print the car data as a table using 'tabulate' """
    # Using a Tuple for the headers to keep the order of "columns"
    headers = ("Make", "Model", "Year", "Mpg Cty", "Mpg Hwy",
               "Cost Cty", "Cost Hwy", "Cost Avg"
              )

    rows = []
    for car in cars:
        # Each row is a Tuple in order to keep order of "columns"
        row = (car.make, car.model, car.year, car.mpg_cty, car.mpg_hwy,
               f"${calculate_cost(miles, car.mpg_cty, 0, price):.2f}",
               f"${calculate_cost(miles, car.mpg_hwy, 0, price):.2f}",
               f"${calculate_cost(miles, car.mpg_cty, car.mpg_hwy, price):.2f}"
              )
        rows.append(row)
    print()
    print(f"Estimated cost of gasolin for driving {miles} ", end="")
    print(f"miles based on ${price:.2f} per gallon.")
    print(tabulate.tabulate(rows, headers, tablefmt="grid"))
    print()
    
    return


def print_csv(cars, miles, price):
    """ Save car mpg data to csv file """
    # Using a Tuple for the headers to keep the order of "columns"
    headers = ("Car#", "Make", "Model", "Year", 
               "Mpg Cty", "Mpg Hwy", 
               "Miles", "Price per Gallon",
               "Cost Cty", "Cost Hwy", "Cost Avg"
              )

    rows = []
    for car in cars:
        # Each row is a Tuple in order to keep order of "columns"
        row = (car.car_id, car.make, car.model, car.year, 
               car.mpg_cty, car.mpg_hwy, miles, price, 
               f"${calculate_cost(miles, car.mpg_cty, 0, price):.2f}",
               f"${calculate_cost(miles, car.mpg_hwy, 0, price):.2f}",
               f"${calculate_cost(miles, car.mpg_cty, car.mpg_hwy, price):.2f}"
              )
        rows.append(row)

    with open(CSV_NAME, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

    return


def connection_error():
    print()
    print("Internet connection failed ....")
    print("Run program with price and mileage as input.")
    print()
    exit()


if __name__ == "__main__":
    main()


