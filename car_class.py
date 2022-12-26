from datetime import datetime
from call_ws import ws_validate_car, ws_get_car_details, ws_get_car_models

class CAR():
    """
    Class to handle a cars make, model, year and mileage

    Attributes:
        make (str): The make of the car (example Honda)
        model (str): The model of the car (example Pilot)
        year (str): The release year of this model
        mileage_cty (int): Average mileage for driving in city
        mileage_hwy (int): Average mileage for driving on highway

    Methods:
        __init__      : Initialize attributes
        __str__       : Appearance when car is used with print()
        get_newcar    : Create new instance of class
                        Validates car make, model and year.
                        Retrieves car details like mpg
        
    Web Service used to get car data: https://www.fueleconomy.gov/feg/ws/index.shtml#vehicle 

    """

    def __init__(self, car_id, make, model, year, mpg_cty, mpg_hwy):
        """ Initialize attributes """
        self.car_id = car_id
        self.make = make
        self.model = model
        self.year = year
        self.mpg_cty = mpg_cty
        self.mpg_hwy = mpg_hwy


    def __str__(self):
        """ Appearance when car is used with print() """
        return f"\n{27 * '-'} \n"                             \
               f"{self.make} {self.model}, {self.year}   \n"  \
               f"    Mileage City:    {self.mpg_cty} mpg \n"  \
               f"    Mileage Highway: {self.mpg_hwy} mpg \n"  \
               f"{27 * '-'} \n"


    @classmethod
    def get_newcar(cls, make="", model="", year=0 ):
        """ 
        Create new instance 
        """
        # Get user input if not passed as arguments
        if not (make and model and year):
            make, model, year = cls.get_user_input()

        car_id = ws_validate_car(make, model, year)
        
        if car_id == 0:
            raise ValueError("Car details were not found in car database.")
        elif car_id == 999:
            raise ConnectionError
            
        # Besides retrieving mpg, also get the correct upper/lower case for make and model
        try:
            mpg_cty, mpg_hwy, make, model = ws_get_car_details(car_id)
        except ConnectionError:
            raise ConnectionError

        return cls(car_id, make, model, year, mpg_cty, mpg_hwy)
        

    @classmethod
    def get_models(cls, make, year):
        """
        Get all models for make and year
        """

        model_list = ws_get_car_models(make, year)

        if len(model_list) == 0:
            raise ValueError("Car details were not found in car database.")
        else:
            return model_list

    @classmethod
    def get_user_input(cls):
        """
        Prompt user to enter details for make, model and year
        """
    
        make = input("Make: ").strip()

        while True:
            try:
                year = int(input("Year: ").strip())
            except ValueError:
                continue
            else:
                if 1950 <= year <= datetime.now().year:
                    break
                print("Please enter valid year between 1950 and", datetime.now().year)
        
                # Check if models exist for this make and year
        
        models = CAR.get_models(make, year)

        while True:
            model = input("Model: ").strip()
            
            # Comparing model with models from list, compared as lower case
            if model.lower() in [item.lower() for item in models]:
                break
            else:
                print("\nModel not found, please enter model from this list:\n")
                for col1, col2, col3 in zip(models[0::3], models[1::3], models[2::3]):
                    print(f"{col1:<35}{col2:<35}{col3:<35}")    #.format(col1, col2, col3))
                print()

        return make, model, year

        