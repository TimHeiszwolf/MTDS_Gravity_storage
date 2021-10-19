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


class Controller:
    def __init__(self, train_track = TrainTrack(), supply = WindSupplyDummy(1000), demand = HouseholdsDummy(1000), delta_time = 5):
        
        self.time = 0
        self.delta_time = delta_time
        
        self.supply = supply
        self.demand = demand
        self.train_track = train_track
        
        self.data = {"Time" : [], "Velocity" : [], "Satisfaction" : [], "Amount carts on track" : [], "Supply" : [], "Demand" : [], "Storage" : [], "Difference" : [], "Losses": [], "Amount carts on top" : [], "Amount carts on bottom" : []}
        
        
        
        self.allow_new_carts = True
        self.max_acceleration = 1
        self.max_speed = 10
    
    
    def check_carts(self):
        """
        A function which checks if the carts are still on/near the track and if not removes them from circulation. If allowed it also tries to add a new cart.
        """
        
        train_track = self.train_track# So that we don't have to put self in front of it each time.
        
        did_thing = False
        
        for i in range(len(train_track.carts_on_track)):# Checks each cart.
            if train_track.carts_on_track[i] > train_track.track_length:# If the cart is at the top of the track then remove (and replace) it
                train_track.remove_cart(self.delta_time, i)
                
                if self.allow_new_carts:
                    train_track.add_cart("Bottom")
                
                did_thing = True
                return True
                break
            elif train_track.carts_on_track[i] < 0:# If the cart is at the bottom of the track then remove (and replace) it
                train_track.remove_cart(self.delta_time, i)
                
                if self.allow_new_carts:
                    train_track.add_cart("Top")
                
                did_thing = True
                return True
                break
            else:# Otherwise continue
                continue
        
        if not did_thing:
            return False
    
    def controller(self):
        """"
        This is the actual part of the controller that controlls how and when carts are added and also determines the force the generator will use. Speciclicly this controller always tried to add a cart and does the controll for power purley based on (steady-state) speed by adjusting the generator force. See the report for more details.
        """
        
        train_track = self.train_track# So that we don't have to put self. in front of it each time.
        
        net_demand = self.supply.output(self.time) - self.demand.consumption(self.time)# Calculate the difference in supply and demand that the storage system should fill.
        
        while self.check_carts():# Check the carts until no more changes are done.
            continue
        
        if len(train_track.carts_on_track) > 0:# If there are other carts on the track let the track itself decide were (and if it is possible) to add a cart.
            train_track.add_cart()
        else:# If there are no other carts on the track the velocity will be zero and thus the controller will have to determine where to add the carts.
            if net_demand > 0:
                train_track.add_cart("Bottom")
            elif net_demand < 0:
                train_track.add_cart("Top")
        
        neutral_force = -(train_track.get_gravity() + train_track.get_friction())# Calculate the force the generator needs to have to maintain the current speed of the carts.
        neutral_power = train_track.get_efficiency_generator() * abs(train_track.get_gravity() + train_track.get_friction()) * train_track.velocity# Calculate the assosiated power out/input.
        
        if neutral_force != 0:# Prevent a devide by zero error. Will only be zero if there are no carts (or if the carts are at terminal velocity which should never happen).
            needed_change_in_speed = -(neutral_power - net_demand) / abs(neutral_force)# Calculate the change in speed needed to get to the desired power output. It ignores a potential increase in friction but that is not a problem since during the next tick it will take into account an increased friction and thus it will exponentially decrease any effect this has.
        else:
            needed_change_in_speed = 0
        
        if train_track.velocity > self.max_speed:# If the speed is maximum then set the change in velocity to be zero.
            needed_change_in_speed = 0#train_track.velocity - self.max_speed
        elif train_track.velocity < -self.max_speed:
            needed_change_in_speed = 0#self.max_speed + train_track.velocity
        
        acceleration = min([max([needed_change_in_speed / self.delta_time, -self.max_acceleration]), self.max_acceleration])# Make sure the maximum acceleration also is not exeded.
        train_track.force_of_generator = neutral_force + acceleration * train_track.mass_per_cart * len(train_track.carts_on_track)# The force is calculated based on the neutral force plus any acceleration needed.
        
        if train_track.force_of_generator <=0:# Make sure the force is not negative.
            train_track.force_of_generator = 0
        
    def get_debug_print(self):
        """
        A function which can be used to print stuff for debugging purposes.
        """
        
        print("")
        print("Time:", self.time)
        print("Demand sasitsfied:", np.round(100 * (self.supply.output(self.time) - self.train_track.get_power())/ self.demand.consumption(self.time), 2), "From storage:", np.round(100 * (-self.train_track.get_power())/ self.demand.consumption(self.time), 2), "Demand:", np.round(self.demand.consumption(self.time), 2), "Supply:", np.round(self.supply.output(self.time), 2), "Storage:", np.round(-self.train_track.get_power(),2))
        
        train_track = self.train_track
        
        print("Velocity:", np.round(train_track.velocity, 2))
        print("Carts: ", len(train_track.carts_on_track), train_track.carts_of_track, "Position:", np.round(train_track.carts_on_track, 1))
        print("Forces (gravity, friction, generator):", [np.round(train_track.get_gravity()), np.round(train_track.get_friction()), np.round(train_track.force_of_generator)])
    
    def do_tick(self):
        """
        This sub-function does a time-step (tick as it is called). During each tick it saves the data to the data dictionairy and then exicutes the controller and lets the train traick also do a tick.
        """
        
        self.data["Time"].append(self.time)
        self.data["Velocity"].append(self.train_track.velocity)
        self.data["Satisfaction"].append((self.supply.output(self.time) - self.train_track.get_power()) / self.demand.consumption(self.time))#data["Satisfaction"] =  ((data["Supply"] - data["Storage"]) / data["Demand"])
        self.data["Amount carts on track"].append(len(self.train_track.carts_on_track))
        self.data["Supply"].append(self.supply.output(self.time))# Inefficient that we call these functions 4 times (here twice and once in controller).
        self.data["Demand"].append(self.demand.consumption(self.time))
        self.data["Storage"].append(self.train_track.get_power())
        self.data["Difference"].append(self.supply.output(self.time) - self.train_track.get_power() - self.demand.consumption(self.time))# Positive is energy left over, negative is energy shortage
        self.data["Losses"].append(sum(self.train_track.losses.values()))
        self.data["Amount carts on top"].append(self.train_track.carts_of_track["Top"])
        self.data["Amount carts on bottom"].append(self.train_track.carts_of_track["Bottom"])
        
        self.controller()# Let the controller do its thing.
        self.train_track.do_tick(self.delta_time)# Do a tick for the train track (the actual physics).
        
        self.time = self.time + self.delta_time
    
    def simulate(self, end_time_seconds = 364 * 24 * 3600, end_time_days = 0):
        """
        This sub-function does the simulation until a certain end time. It also returns some data so it can be used in the make_3Dfunction_plot.
        """
        
        end_time = end_time_seconds + 3600 * 24 * end_time_days
        
        while self.time <= end_time:
            self.do_tick()
            #print(self.get_debug_print())
        #print(self.get_debug_print())
        return self.supply.output(self.time) - self.train_track.get_power() - self.demand.consumption(self.time)# Positive is energy left over, negative is energy shortage
    
    def get_difference_supply_demand(self, time_seconds, time_days = 0):
        """
        This function gets the difference in supply and demand without the influence of the storage system. This sub-function is mainly used to make plots for the report.
        """
        
        time = time_seconds + 3600 * 24 * time_days
        return self.supply.output(time) - self.demand.consumption(time)
    
    def get_sastisfaction_supply_demand(self, time_seconds, time_days = 0):
        """
        This function gets the satisfactionf of the demand by the supply without the influence of the storage system. This sub-function is mainly used to make plots for the report.
        """
        
        time = time_seconds + 3600 * 24 * time_days
        return self.supply.output(time) / self.demand.consumption(time)

"""
households = Households()
wind_supply = WindSupplyDummy()

def get_difference(time_seconds, time_days = 0, output = households, inputt  = wind_supply):
    return output.consumption(time_seconds, time_days) - inputt.output(time_seconds, time_days)

make_3Dfunction_plot(get_difference)
#"""
"""
controller = Controller()

controller.simulate(200)

data = pd.DataFrame(controller.data)

print(data)
#"""
"""
train_track = TrainTrack(carts = 0)
supply = WindSupply()
demand = Households(amount_of_households_per_type = [125000, 0, 0, 0, 0, 0, 0, 0, 0, 0])# Theoretically 125000
controller = Controller(train_track = train_track, supply = supply, demand = demand, delta_time = 120)

make_3Dfunction_plot(controller.get_sastisfaction_supply_demand, zLabel = "Satisfaction")
#"""