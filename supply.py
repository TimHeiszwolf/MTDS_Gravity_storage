
# coding: utf-8

# In[2]:

#importing libraries

import numpy as np 
import pandas as pd
import datetime
import math


# In[77]:

class WindSupply:
    """
    This class will calculate the poweroutput form windmills with the windspeeds in the database
    """
    def __init__(self, amount_of_windmills = 36, windspeeds_profile = "wind_speed_ijmuiden.txt"):
        
        data = pd.read_csv(windspeeds_profile)
        data["Start time"] = pd.to_datetime(data["date"], format="%Y%m%d")
        data["Start time"] = [data["Start time"][i] + datetime.timedelta(hours = float(data["hour"][i])) for i in range(len(data["Start time"]))]
        data["wind speed"] = data["wind speed"] * 0.1
        #data["max wind speed"] = data["max wind speed"] * 0.1        
        start_time = data["Start time"][0]
        
        time_since_start = data["Start time"] - start_time
        data["Seconds"] = [time.total_seconds() for time in time_since_start]
        data["Days"] = data["Seconds"] / (3600 * 24)
             
        ρ = 1.225 #kg/m^3 air density
        Cp = 0.3 #power efficiency factor
        A = 5027 #sweep area in m^2
        K = 0 #efficiency difference land sea
        T = 60 #amount of windmills in the park
        year_amount = 435*10**9 #wh per year
        
        hour_amount = year_amount/(365*24*T) #wh per hour
        
        data["output"] = 1/2 * ρ * Cp * A * (data["wind speed"])**3 #calculating the power output in watt for each given windspeed.
        
        data.loc[(data.output > 2000000),'output']=2000000
        
        K = hour_amount/wind_supply.data["output"].mean()
        data["output_adjusted"] = K * 1.33 * 1/2 * ρ * Cp * A * (data["wind speed"])**3 #calculating the power output in watt for each given windspeed.
        
        self.data = data
        
    
        data.loc[(data.output_adjusted > 2000000),'output_adjusted']=2000000
       
        
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
        
        return self.data["output"][estimated_row_bot] + interpolation_factor * (self.data["output"][estimated_row_bot + 1] - self.data["output"][estimated_row_bot])
        
       
        

wind_supply = WindSupply()

#wind_supply.data
#wind_supply.data["output_adjusted"].mean()
#print(wind_supply.data.columns)

        


# In[78]:

from mpl_toolkits.mplot3d import axes3d
from matplotlib import pyplot
from matplotlib import cm

def make_3Dfunction_plot(function, amount_of_days = 364, increments_in_day = 200):
    """
    Makes a 3D plot like in the paper of Elke Klaasen (on the X axis the hours of the day, Y axis the days (of the year) and on the Z axis the actual value). Sadly makes a surface plot instead of a wireframe plot this is because the heatmap didn't work properly with the wireframe.
    
    function is the function of which it is going to make the wire plot
    amount_of_days is the amount of days you want the plot to coverting
    increments_in_day is the amount of steps during each day. Making this number large increases the x-axis accuracy of the plot but also increases computational time greatly.
    """
    
    x = []
    y = []
    z = []
    
    x_new = []
    y_new = []
    z_new = []
    
    for day in range(0, amount_of_days):# For each individual day on the y-axis you make a new array containing the values for each hour (including the x and y-axis values themselfs) this you then append to the total array.
        for hour in np.linspace(0, 24, increments_in_day, endpoint = True):
            x_new.append(hour)
            y_new.append(day)
            z_new.append(function(hour * 3600, day))
        
        x.append(x_new)
        y.append(y_new)
        z.append(z_new)
        
        x_new = []
        y_new = []
        z_new = []
    
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    
   
    
    #print(x, np.shape(x))
    #print(y, np.shape(y))
    #print(z, np.shape(y))
    
    fig = pyplot.figure(figsize=(8,8))
    wf = fig.add_subplot(111, projection='3d')
    #wf.plot_wireframe(x,y,z, cmap = cm.coolwarm, linewidth = 1)# Wireframe doesn't work properly
    wf.plot_surface(x,y,z, cmap = cm.coolwarm, linewidth = 1)# Make the surface plot instead with a colour map and still some wireframe
    wf.view_init(60, -120)# Its reversed from matplotlib
   
    pyplot.show()
    


#"""
wind_supply = WindSupply()
make_3Dfunction_plot(wind_supply.output)
#"""

