import pandas as pd
import numpy as np
import datetime
import math

class TrainTrack:
    """
    This is the class that actually simulates the tracks/storage solution. See the report for details. In short it simulates the carts on the tracks as one giant cart and thus applies friction/gravity/braking only to that giant monolithic block. It adds carts by pretending the mass of the giant block increases and doing a conservation of energy calculation. It does keep track of the location of each cart and based on that it can remove carts. If that happens the power output is increased such that the kinetic energy is outputed trough that.
    """
    def __init__(self, carts = 150, track_dimensions = [20000, 2000], mass_per_cart = 12.192 * 2.438 * 2.591 * 2170, minimal_distance = 100, efficiency_generator = [0.9, 1/0.7]):
        """
        The init fucntion.
        
        carts is the amount of carts available. This amount is put both at the top and bottom.
        track_dimensions is a list with the first element being the distance (in the x axis) while the second element is the height.
        mass_per_cart is a number representing the amount of mass per cart.
        minimal_distance is a number which specifies the minimal amount of distance needed between carts.
        efficiency_generator is a list with the first element being the efficiency of generating power and the second element being the efficiency of storing power. Default values are based on sources (which can be found in the report).
        """
        
        self.carts_on_track = []# Each cart on the track will be represented by a number which indicates its position on the track.
        self.velocity = 0# The velocity of the consolidated cart.
        self.carts_of_track = {"Bottom" : carts, "Top" : carts}# Both at the bottom and the top the same amount of carts is started with.
        self.losses = {"Friction" : 0, "Efficiency" : 0}
        
        self.angle = np.arctan(track_dimensions[1] / track_dimensions[0])# Calculate the angle of the track.
        self.track_length = np.sqrt(track_dimensions[0]**2 + track_dimensions[1]**2)# Calculate the length of the tracks by using Pythagoras.
        self.track_height = track_dimensions[1]
        
        self.mass_per_cart = mass_per_cart
        self.minimal_distance = minimal_distance
        
        self.force_of_generator = 0# This is one of the variables that can be used by the controller to control the carts.
        self.efficiency_generator = efficiency_generator
        self.other_power = 0
    
    def get_friction(self, velocity = "NaN"):
        """
        This function gets the friction of all the carts in total.
        
        velocity can be specified and then the friction of that velocity will be obtained. Otherwise the velocity of the traintrack object will be used.
        """
        
        g = 9.81
        density_air = 1.275
        
        drag_coefficient = 1.05 * (2.591 * 2.438) / 2
        friction_coefficient = 0.0015# https://www.school-for-champions.com/science/friction_rolling_coefficient.htm
        
        if velocity == "NaN":
            velocity = self.velocity
        
        return -np.sign(velocity) *  len(self.carts_of_track) * (density_air * velocity**2 * drag_coefficient + np.cos(self.angle) * g * self.mass_per_cart * friction_coefficient)#TODO Make into rolling resistance
    
    def get_gravity(self):
        """
        Gets the gravity of the entire system.
        """
        
        g = 9.81
        return -np.sin(self.angle) * g * len(self.carts_on_track) * self.mass_per_cart
    
    def get_kinetic_energy_per_cart(self, velocity = "NaN"):
        """
        Gets the kinetic energy per cart. The velocity can be specified if not then the velocity of the object will be used.
        """
        
        if velocity == "NaN":
            return (1/2) * self.mass_per_cart * self.velocity**2
        else:
            return (1/2) * self.mass_per_cart * velocity**2
    
    def add_cart(self, location = ""):
        """
        This function adds a cart to the system. If the location is not specified it tries to figure it out itself. When a cart is added it is pretended it becomes part of the total system and thus instantly gets pulled up to speed. Then conservation of energy is used to get the new total velocity.
        """
        
        if np.sign(self.velocity) > 0 and location == "":# If the location is not specified try to figure out where to put the cart.
            location = "Bottom"
        elif np.sign(self.velocity) <= 0 and location == "":
            location = "Top"
        
        
        if len(self.carts_on_track) == 0:# The max function doesn't like empty arrays so in that case define it yourself.
            max_cart = 0
            min_cart = self.track_length
        else:
            max_cart = max(self.carts_on_track)# The position of the highest cart on the track.
            min_cart = min(self.carts_on_track)# The position of the lowest cart on the track.
        
        if (location == "Top" and (self.track_length - max_cart) > self.minimal_distance) or (location == "Bottom" and min_cart > self.minimal_distance):# Checks if the minimal distance can be kept when adding a cart.
            
            self.velocity = np.sign(self.velocity) * np.sqrt(len(self.carts_on_track) * self.velocity**2 / (len(self.carts_on_track) + 1))# The new velocity based on the conservation of energy.
            
            if location == "Top":
                if self.carts_of_track["Top"] > 0:# Checks if there is a cart available on top.
                    self.carts_on_track.append(self.track_length)# Adds a cart to the top.
                    self.carts_of_track["Top"] = self.carts_of_track["Top"] - 1# Remove a cart.
                    return True
                else:
                    return False
            elif location == "Bottom":
                if self.carts_of_track["Bottom"] > 0:# Checks if there is a cart available on the bottom
                    self.carts_on_track.append(0)# Adds a cart to the bottom.
                    self.carts_of_track["Bottom"] = self.carts_of_track["Bottom"] - 1# Remove a cart.
                    return True
                else:
                    return False
        
        else:# If no distance can be kept then return false and don't add a cart.
            return False
    
    def remove_cart(self, delta_time, index):
        """
        This function removes a cart and then adds the amount of kinetic energy to the output power.
        
        delta_time is the time step size.
        index is the index of the cart you want to remove.
        """
        
        if self.carts_on_track[index] > self.track_length / 2:# Determines the location of the cart, generally should be very obvious (either completely at the top or completley at the bottom) but this function also allows for half way removal (altrough that doesn't make physics sense).
            location = "Top"
        elif self.carts_on_track[index] <= self.track_length / 2:
            location = "Bottom"
        
        energy_left_over = self.get_kinetic_energy_per_cart()# Gets how much energy is left.
        self.other_power = self.other_power -  energy_left_over / delta_time# Adds the energy to other power.
        
        self.carts_on_track.pop(index)# Removes that cart.
        self.carts_of_track[location] = self.carts_of_track[location] + 1# Adds the cart to the stockpile.
    
    def get_power(self):
        """
        Gets the amount of power that the track generates. Both based on the generator and the other sources of power
        """
        efficiency = self.get_efficiency_generator()
        
        return self.efficiency_generator[0] * self.other_power + efficiency * self.force_of_generator * self.velocity
    
    def do_tick(self, delta_time):
        """
        This function does a tick (time-step). It also properly stores the losses and does the kinematic physics for the carts.
        
        delta_time is the size of the tick/time-step.
        """
        
        efficiency = self.get_efficiency_generator()
        
        self.losses["Friction"] = abs(self.get_friction() * self.velocity) * delta_time
        self.losses["Efficiency"] = (1 - self.efficiency_generator[0]) * self.other_power + abs((1 - efficiency) * self.force_of_generator * self.velocity) * delta_time# The inverse of the power, so the power that is wasted due to efficiency.
        
        self.other_power = 0#Reset the other power to zero. It could be considered to make a exponential decay of this such that the size of delta_time thus doesn't influence the behavior of other power.
        
        if len(self.carts_on_track) == 0:# Prevent devide by zero error
            acceleration = 0
            self.velocity = 0
        else:
            acceleration = (self.get_gravity() + self.get_friction() + self.force_of_generator) / (len(self.carts_on_track) * self.mass_per_cart)# Calculate the acceleration.
        
        change_in_position = self.velocity * delta_time + 0.5 * acceleration * delta_time**2# Do the kinematics of the position.
        self.carts_on_track = [current_position_of_cart + change_in_position for current_position_of_cart in self.carts_on_track]# Change the position of each of the carts.
        self.velocity = self.velocity + acceleration * delta_time
    
    def get_efficiency_generator(self):
        """
        Gets the efficiency of the generator since that varries based on wheter is it pulling the carts up or letting them decent.
        """
        
        if self.velocity > 0:
            efficiency = self.efficiency_generator[1]
        elif self.velocity <= 0:
            efficiency = self.efficiency_generator[0]
        
        return efficiency
    
    def return_data(self):
        """
        A quick function that can be used for quick data reading. Generally should be used as an input for other functions/data analytics but can be nice for printing/debugging purposes.
        """
        
        return {"Positions": np.round(self.carts_on_track, 2), "Velocity" : np.round(self.velocity, 2), "Forces (gravity, friction, generator)" : [np.round(self.get_gravity()), np.round(self.get_friction()), np.round(self.force_of_generator)], "Power" : np.round(self.get_power()), "Other carts" : self.carts_of_track, "Losses (friction, efficiency)" : np.round([self.losses["Friction"], self.losses["Efficiency"]],1)}
        

"""
train_track = TrainTrack()
time = 0
train_track.carts_on_track.append(train_track.track_length-1000)

for i in range(10):
    print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1

print("\n Adding a generator force. \n")
train_track.force_of_generator = -(train_track.get_gravity() + train_track.get_friction())#142978

for i in range(20):
    print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1

print("\n Adding another cart. \n")
train_track.add_cart("Top")
#train_track.force_of_generator = -(train_track.get_gravity() + train_track.get_friction())

for i in range(20):
    print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1

print("\n Now trying to decelerate. \n")
train_track.force_of_generator = -1.4 * (train_track.get_gravity() + train_track.get_friction())#142978

for i in range(20):
    print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1

print("\n Running until at the bottom. \n")
train_track.force_of_generator = - (train_track.get_gravity() + train_track.get_friction())

print(time, train_track.return_data())
for i in range(2050):
    #print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1
print(time, train_track.return_data())

print("\n Removing a cart. \n")
train_track.remove_cart(1, 0)
train_track.force_of_generator = - (train_track.get_gravity() + train_track.get_friction())

for i in range(20):
    print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1

print("\n Adding another cart. \n")
train_track.add_cart("Top")
train_track.force_of_generator = -(train_track.get_gravity() + train_track.get_friction())

for i in range(20):
    print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1

print("\n Removing and adding a cart. \n")
train_track.remove_cart(1, 0)
train_track.add_cart("Top")

for i in range(20):
    print(time, train_track.return_data())
    train_track.do_tick(1)
    time = time + 1

#"""

