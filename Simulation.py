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


train_track = TrainTrack(carts = 200)
supply = WindSupply(amount_of_windmills = 60)#WindSupplyDummy(100000)
demand = Households(amount_of_households_per_type = [100000, 0, 0, 0, 0, 0, 0, 0, 0, 0])

controller = Controller(train_track = train_track, supply = supply, demand = demand, delta_time = 30)

make_3Dfunction_plot(controller.simulate, amount_of_days = 365)#controller.simulate(2*24*3600)

data = pd.DataFrame(controller.data)

data["Satisfaction"] =  ((data["Supply"] - data["Storage"]) / data["Demand"])
print(data)
 

plt.plot(data["Time"] / (3600 * 24), data["Supply"], label="Supply")
plt.plot(data["Time"] / (3600 * 24), data["Demand"], label="Demand")
#plt.title("Delhi Temperature")
plt.xlabel("Time (days)")
plt.ylabel("Supply (Watts)")
plt.legend(loc="upper left")
plt.show()

plt.plot(data["Time"] / (3600 * 24), data["Satisfaction"])
#plt.title("Delhi Temperature")
plt.xlabel("Time (days)")
plt.ylabel("Satisfaction")
plt.show()

plt.plot(data["Time"] / (3600 * 24), data["Velocity"])
#plt.title("Delhi Temperature")
plt.xlabel("Time (days)")
plt.ylabel("Velocity on track")
plt.show()

plt.plot(data["Time"] / (3600 * 24), data["Amount carts on top"], label = "Amount of carts at top")
plt.plot(data["Time"] / (3600 * 24), data["Amount carts on bottom"], label = "Amount of carts at bottom")
#plt.title("Delhi Temperature")
plt.xlabel("Time (days)")
plt.ylabel("Amount of carts")
plt.legend(loc="upper left")
plt.show()


data.to_excel("Test.xlsx")
