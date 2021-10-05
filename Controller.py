import pandas as pd
import numpy as np
import datetime
import math

from mpl_toolkits.mplot3d import axes3d
from matplotlib import pyplot
from matplotlib import cm

from Helpers import make_3Dfunction_plot
from Supply import WindSupply
from Supply import WindSupplyDummy
from Demand import Households
from Storage import TrainTrack


class Controller:
    def __init__(self, train_track = TrainTrack(), supply = WindSupplyDummy(), demand = Households(), delta_time = 5):
        
        self.time = 0
        self.delta_time = delta_time
        
        self.supply = supply
        self.demand = demand
        self.train_track = train_track
        
        self.data = {"Time": [], "Supply" : [], "Demand" : [], "Storage" : [], "Difference" : [], "Losses": []}
        
        
        
        self.allow_new_carts = True
        self.max_acceleration = 1
        self.max_speed = 10
    
    
    def check_carts(self):
        """
        A function which checks if the carts are still on/near the track and if not removes them from circulation. If allowed it also tries to add a new cart.
        """
        for i in range(len(train_track.carts_on_track)):# Checks each cart.
            if train_track.carts_on_track[i] > train_track.track_length:# If the cart is at the top of the track then remove (and replace) it
                train_track.remove_cart(self.delta_time, i)
                
                if self.allow_new_carts:
                    train_track.add_cart("Top")
            elif train_track.carts_on_track[i] < 0:# If the cart is at the bottom of the track then remove (and replace) it
                train_track.remove_cart(self.delta_time, i)
                
                if self.allow_new_carts:
                    train_track.add_cart("Bottom")
            else:# Otherwise continue
                continue
                
    
    def controller(self):
        
        train_track = self.train_track# So that we don't have to put self in front of it each time.
        
        neutral_force = train_track.get_gravity() + train_track.get_friction()
        
        neutral_power = abs(neutral_force) * self.train_track.velocity# Power is defined as negative when flowing out and postive when flowing in.
        net_demand = self.supply.output(self.time) - self.demand.consumption(self.time)
        
        
        if neutral_force != 0:
            needed_change_in_speed = (neutral_power - net_demand) / abs(neutral_force)# Calculates the change in speed needed to match the needed demand. Thus ignores inital loss of power due to acceleration. Ignores any change in friction.
        else:
            needed_change_in_speed = 2 * self.max_acceleration * self.delta_time * np.sign(neutral_power - net_demand)
        
        if abs(needed_change_in_speed + train_track.velocity) >= self.max_speed:# If the speed becomes larger than the allowed speed then (try to) add carts. Also set the needed_change_in_speed to the change needed to reach the maximum.
            if train_track.velocity > 0:
                train_track.add_cart("Bottom")
                needed_change_in_speed = self.max_speed - train_track.velocity
            elif train_track.velocity <=0:
                train_track.add_cart("Top")
                needed_change_in_speed = -self.max_speed - train_track.velocity
        
        needed_acceleration = needed_change_in_speed / self.delta_time
        acceleration = max([-self.max_acceleration, min([self.max_acceleration, needed_acceleration])])# Makes sure the acceleration is within limits.
        train_track.force_of_generator = max([-neutral_force + acceleration * train_track.mass_per_cart * len(train_track.carts_on_track), 0])
        
        #print(train_track.force_of_generator)
        
        
    
    def do_tick(self):
        """
        TO WRITE
        """
        
        self.data["Time"].append(self.time)
        self.data["Supply"].append(self.supply.output(self.time))# Inefficient that we call these functions 3 times (here twice and once in controller).
        self.data["Demand"].append(self.demand.consumption(self.time))
        self.data["Storage"].append(self.train_track.get_power())# power)
        self.data["Difference"].append(self.demand.consumption(self.time) - self.supply.output(self.time) + self.train_track.power)
        self.data["Losses"].append(sum(self.train_track.losses.values()))
        
        self.controller()
        self.train_track.do_tick(self.delta_time)
        
        self.time = self.time + self.delta_time
        
    def simulate(self, end_time = 364 * 24 * 3600):
        
        while self.time <= end_time:
            self.do_tick()
            #print(self.time / (3600 * 24))

"""
households = Households()
wind_supply = WindSupplyDummy()

def get_difference(time_seconds, time_days = 0, output = households, inputt  = wind_supply):
    return output.consumption(time_seconds, time_days) - inputt.output(time_seconds, time_days)

make_3Dfunction_plot(get_difference)
#"""
#"""
controller = Controller()

controller.simulate(1 * 24 * 3600)

data = pd.DataFrame(controller.data)

print(data)
#"""
