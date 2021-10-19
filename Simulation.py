import pandas as pd
import numpy as np
import datetime
import math

from mpl_toolkits.mplot3d import axes3d
from matplotlib import pyplot
import matplotlib.pyplot as plt
from matplotlib import cm

from Helpers import make_3Dfunction_plot
from Supply import WindSupply
from Supply import WindSupplyDummy
from Demand import Households
from Demand import HouseholdsDummy
from Storage import TrainTrack
from Controller import Controller


### SETTINGS
days_to_simulate = 364
amount_of_carts = 30000
amount_households = 67000
amount_windmils = 60

train_track = TrainTrack(carts = amount_of_carts/2)
supply = WindSupply(amount_of_windmills = amount_windmils)#WindSupplyDummy(100000)
demand = Households(amount_of_households_per_type = [amount_households, 0, 0, 0, 0, 0, 0, 0, 0, 0])# Theoretically 125000
controller = Controller(train_track = train_track, supply = supply, demand = demand, delta_time = 10)


### SIMULATION AND PLOTTING
#make_3Dfunction_plot(controller.get_difference_supply_demand, amount_of_days = days_to_simulate, zlabel = "Difference in power (Watts)")
#make_3Dfunction_plot(controller.get_sastisfaction_supply_demand, amount_of_days = days_to_simulate, zlabel = "Satisfaction")
controller.simulate(3600)# First simulate a hour to stabalize the stystem. This will cause the end result to have a constant first hour.
make_3Dfunction_plot(controller.simulate, amount_of_days = days_to_simulate, zlabel = "Difference in power (Watts)", title = "Difference plot " +str(days_to_simulate) + " days, "+ str(amount_households) + " households and " + str(amount_of_carts) + " carts.")

data = pd.DataFrame(controller.data)
data.to_csv(str(days_to_simulate) + "days" + str(amount_households) + "households" + str(amount_of_carts) + "carts.csv")
#data = pd.read_csv("364days62500households10000000carts.csv")
print(data)

plt.plot(data["Time"] / (3600 * 24), data["Supply"], label="Supply")
plt.plot(data["Time"] / (3600 * 24), data["Demand"], label="Demand")
plt.xlabel("Time (days)")
plt.ylabel("Supply (Watts)")
plt.legend(loc="upper left")
plt.show()

plt.plot(data["Time"] / (3600 * 24), data["Satisfaction"])
plt.xlabel("Time (days)")
plt.ylabel("Satisfaction")
plt.show()

plt.plot(data["Time"] / (3600 * 24), data["Velocity"])
plt.xlabel("Time (days)")
plt.ylabel("Velocity on track (meter per second)")
plt.show()

plt.plot(data["Time"] / (3600 * 24), data["Amount carts on top"], label = "Amount of carts at top")
plt.plot(data["Time"] / (3600 * 24), data["Amount carts on bottom"], label = "Amount of carts at bottom")
plt.xlabel("Time (days)")
plt.ylabel("Amount of carts")
plt.legend(loc="upper left")
plt.show()

print("Supply minus demand sum", np.sum(data["Supply"]) - np.sum(data["Demand"]))