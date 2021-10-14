import numpy as np 
import pandas as pd
import datetime
import math

class WindSupply:
    """
    This class will calculate the poweroutput form windmills with the windspeeds in the database
    """
    def __init__(self, amount_of_windmills = 60, windspeeds_profile = "wind_speed_ijmuiden.txt"):
        
        data = pd.read_csv(windspeeds_profile)
        data["Start time"] = pd.to_datetime(data["date"], format="%Y%m%d")
        data["Start time"] = [data["Start time"][i] + datetime.timedelta(hours = float(data["hour"][i])) for i in range(len(data["Start time"]))]
        data["wind speed"] = data["wind speed"] * 0.1
        #data["max wind speed"] = data["max wind speed"] * 0.1        
        start_time = data["Start time"][0]
        
        self.amount_of_windmills = amount_of_windmills
        
        time_since_start = data["Start time"] - start_time
        data["Seconds"] = [time.total_seconds() for time in time_since_start]
        data["Days"] = data["Seconds"] / (3600 * 24)
             
        ρ = 1.225# Air density in kg/m^3 
        Cp = 0.3# Power efficiency factor
        A = 5027# Sweep area in m^2
        K = 0# Efficiency difference land sea
        T = 60# Amount of windmills in the park
        year_amount = 435 * 10**9# wh per year in the park
        
        hour_amount = year_amount/(365 * 24 * T) #wh per hour
        
        data["output"] = 1/2 * ρ * Cp * A * (data["wind speed"])**3 #calculating the power output in watt for each given windspeed.
        
        data.loc[(data.output > 2000000),'output'] = 2000000
        
        K = hour_amount / data["output"].mean()
        data["output_adjusted"] = K * 1.33 * 1/2 * ρ * Cp * A * (data["wind speed"])**3 #calculating the power output in watt for each given windspeed.
        data.loc[(data.output_adjusted > 2000000),'output_adjusted'] = 2000000
        
        self.data = data
    
    def output(self, time_seconds, time_days = 0):
        """
        Based on the data in the households object it returns the amount power used. It uses linear interpolation between points to preserve continuity.
        
        time_seconds is a number in seconds, which can be more than a day, is the time of which you want to know the power usage.
        time_days is a number in days which gets converted to second and then added to time in seconds.
        only_total is a boolean which decided if you want to have results split into categories or if you want just the total power usage.
        """
        
        estimated_row_bot = math.floor(time_seconds / (3600) + time_days * 24)# Makes a estimate for which row the data is in we are searching for.
        wanted_time = time_seconds + time_days * 3600 * 24
        
        # print("Getting consumption at estimated index", estimated_row_bot)
        if not (self.data["Seconds"][estimated_row_bot] <= wanted_time and self.data["Seconds"][estimated_row_bot + 1] >= wanted_time):# Checks if the estimate row is correct.
            #print("Attention for time", wanted_time / (3600 * 24), "(d) the rows are not predicatable anymore.")
            
            if self.data["Seconds"][estimated_row_bot] > wanted_time:# If estimate is incorrect determine if to high or to low.
                direction = -1
            else:
                direction = 1
            
            while not (self.data["Seconds"][estimated_row_bot] <= wanted_time and self.data["Seconds"][estimated_row_bot + 1] >= wanted_time):# Until the correct row is found go lower or higher.
                estimated_row_bot = estimated_row_bot + direction
        
        interpolation_factor = (wanted_time - self.data["Seconds"][estimated_row_bot]) / (self.data["Seconds"][estimated_row_bot + 1] - self.data["Seconds"][estimated_row_bot]) # time_difference_for_bot_point / time_difference_between_points
        
        return self.amount_of_windmills * (self.data["output"][estimated_row_bot] + interpolation_factor * (self.data["output"][estimated_row_bot + 1] - self.data["output"][estimated_row_bot]))


class WindSupplyDummy:

    def __init__(self, multiplication = 1):
        
        self.data = ["lol there is no data"]
        self.multiplication = multiplication
    
    def output(self, time_seconds, time_days = 0, average_power = 3500 * 3.6*10**6 / (365 * 24 * 3600)):
        
        day_factor = np.cos(2 * np.pi * time_days / 360)
        
        return self.multiplication * average_power * (1 - 0.5 * np.sin(2 * np.pi * time_seconds / (24 * 3600)) + 0.25 * day_factor)

from mpl_toolkits.mplot3d import axes3d
from matplotlib import pyplot
from matplotlib import cm
from Helpers import make_3Dfunction_plot


"""
wind_supply = WindSupply()
make_3Dfunction_plot(wind_supply.output)

wind_supply = WindSupplyDummy()
make_3Dfunction_plot(wind_supply.output)
#"""

