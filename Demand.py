import pandas as pd
import numpy as np
import datetime
import math

class Households:
    """
    The households class is an object to store the data from the imported CSV file, then ready it for the modeling and finally giving values (with interpolation) to the simulation.
    """
    def __init__(self, amount_of_households_per_type = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0], power_consumption_per_type = [3500, 1000, 5000, 6900, 4200, 1, 0, 20000, 13000, 4000], profiel = "profielen Elektriciteit 2019 versie 1.00.csv"):
        """
        The initialize fuction for the households class imports the data from a CSV file and then readies it by cleaning up the data and coverting it into actual power use.
        
        amount_of_households_per_type is the amount of households in each type of the data imported. Needs to match the amount of data columns in the profile in length.
        power_consumption_per_type is the amount of power each of those types consumes in a year. Unit is KWh per year. Also needs to match the amount of data columns in length.
        profiel is the name of the CSV file from which this NEDU data is imported.
        """
        
        data = pd.read_csv(profiel)# Import the data from a csv file as obtained from the NEBU website.
        data = data.drop([0,1,2,3], axis = 0)# Drop the first rows of useless meta data.
        data = data.reset_index(drop = True)# Fix the index now that some rows have been removed.
        data = data.rename(columns = {"Unnamed: 1":"Start time", "Versienr":"End time"})# Rename the relevant columns.
        data = data.drop(data.columns[0], 1)# Drop the first column since it contains duplicate data.
        data["Start time"] = pd.to_datetime(data["Start time"], format="%d-%m-%Y %H:%M")
        start_time = data["Start time"][0]
        data["End time"] = pd.to_datetime(data["End time"], format="%d-%m-%Y %H:%M")
        
        for i in range(2, len(data.columns)):# Loop trough all the data columns (so not the time columns)
            data = data.rename(columns={data.columns[i]:data.columns[i][5:]})# Remove the first 5 letters from each columns name since that only contains the version number.
            data[data.columns[i]] = data[data.columns[i]].astype("float")# Convert all the numbbers as strings to floats
            
            if data[data.columns[i]].sum() > 1 + 10**-4 or data[data.columns[i]].sum() < 1 - 10**-4:# Check if the sum of each column is (nearly) one.
                print("Panic: column", data.columns[i],"of profile", profiel, "doesn't add up to 1 when summed. It is", data[data.columns[i]].sum(), "instead.")
        
        for i in range(len(amount_of_households_per_type)):
            data[data.columns[i + 2]] = data[data.columns[i + 2]] * power_consumption_per_type[i] * 3.6*10**6 / (15 * 60) * amount_of_households_per_type[i]# This calculation assumes 15 minutes between the datapoints.
        
        time_since_start = data["Start time"] - start_time
        data["Seconds"] = [time.total_seconds() for time in time_since_start]#[i * 15 * 60 for i in range(0,len(data["Start time"]))]
        data["Days"] = data["Seconds"] / (3600 * 24)
        
        self.amount_of_households_per_type = amount_of_households_per_type
        self.power_consumption_per_type = power_consumption_per_type
        self.data = data
        self.start_time = start_time
    
    def consumption(self, time_seconds, time_days = 0, only_total = True):
        """
        Based on the data in the households object it returns the amount power used. It uses linear interpolation between points to preserve continuity.
        
        time_seconds is a number in seconds, which can be more than a day, is the time of which you want to know the power usage.
        time_days is a number in days which gets converted to second and then added to time in seconds.
        only_total is a boolean which decided if you want to have results split into categories or if you want just the total power usage.
        """
        
        estimated_row_bot = math.floor(time_seconds / (15 * 60) + time_days * 24 * 4)# Makes a estimate for which row the data is in we are searching for.
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
        
        results = {}
        
        for i in range(2, len(self.data.columns) - 2):# Do the procces for every column except the first two and the last two (both are time data).
            column = self.data.columns[i]
            results[column] = self.data[column][estimated_row_bot] + interpolation_factor * (self.data[column][estimated_row_bot + 1] - self.data[column][estimated_row_bot])# The amount of power is interpolated using linear interpolation.
        
        if only_total:# Depending on the options either return the total power or the power per type.
            return sum(results.values())
        else:
            return results

from mpl_toolkits.mplot3d import axes3d
from matplotlib import pyplot
from matplotlib import cm
from Helpers import make_3Dfunction_plot


#"""
households = Households()
#print(households.data.head(100))
print(households.data)
#print(households.consumption(1400, 300))
make_3Dfunction_plot(households.consumption)
#"""
