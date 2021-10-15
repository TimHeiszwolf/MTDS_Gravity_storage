import pandas as pd
import numpy as np
import datetime
import math

from mpl_toolkits.mplot3d import axes3d
from matplotlib import pyplot
import matplotlib.pyplot as plt
from matplotlib import cm

def make_3Dfunction_plot(function, amount_of_days = 364, increments_in_day = 200, zlabel = "", title = ""):
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
    
    wf.set_xlabel("Time (hours)")
    wf.set_ylabel("Time (days)")
    wf.set_zlabel(zlabel)
    wf.set_title(title)
    wf.set_xlim(0, 24)
    wf.set_ylim(0, amount_of_days)
    
    pyplot.show()