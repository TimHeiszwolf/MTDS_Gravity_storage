import pandas as pd
import numpy as np
import datetime
import math

class TrainCart:
    def __init__(self, start_position = [0, 1], start_velocity = 0.1, mass = 67.5 * 2170, max_acceleration = 3):
        
        self.position = start_position# first index is position on the track, second index is either upwards or downwards (or a string if on hold).
        self.velocity = start_velocity
        self.mass = mass
        self.power = 0
        self.acceleration = 0
        self.max_acceleration = max_acceleration
        
        self.friction_coefficient = 0.001
        self.drag_coefficient = 1.05 * (2.591 * 2.438)
        
    def do_tick(self, delta_time, angle, g = 9.81):
        if type(self.position[1])==int:
            
            self.acceleration = self.get_acceleration(angle, g)
            self.velocity = self.velocity + self.acceleration * delta_time
            self.position[0] = self.position[0] + self.velocity * delta_time + 0.5 * self.acceleration * delta_time**2
    
    def get_friction_acceleration(self, angle, g = 9.81, density_air = 1.275):
        # Todo add proper friction https://www.sciencedirect.com/science/article/pii/S0043164814003718
        
        return 0.5 * density_air * self.velocity**2 * self.drag_coefficient / self.mass + abs(self.velocity) * np.cos(angle) * g
    
    def get_acceleration(self, angle, g = 9.81):
        acceleration = self.power / (abs(self.velocity) * self.mass) - np.sin(angle) * g - np.sign(self.velocity) * self.get_friction_acceleration(angle, g)
        
        if acceleration == math.nan or acceleration > self.max_acceleration:
            if self.power != 0:
                return self.max_acceleration
            else:
                return 0
        else:
            return acceleration
    
    def set_power_from_velocity(self, angle, desired_velocity, desired_final_acceleration, g = 9.81):
        current_velocity = self.velocity
        self.velocity = desired_velocity
        
        required_power = (np.sin(angle) * g + np.sign(self.velocity) * self.get_friction_acceleration(angle, g) + desired_final_acceleration) * abs(self.velocity) * self.mass
        
        if required_power < 0:
            self.power = 0
        else:
            self.power = required_power
        
        self.velocity = current_velocity
        



cart = TrainCart()

cart.set_power_from_velocity(np.arctan(1/10), 10, 1)
print(cart.position, cart.velocity, cart.acceleration, cart.power)
for i in range(0, 150):
    cart.do_tick(0.05, np.arctan(1/10))
    print(cart.position, cart.velocity, cart.acceleration, cart.power)


cart.set_power_from_velocity(np.arctan(1/10), -10, 1)
print(cart.position, cart.velocity, cart.acceleration, cart.power)
for i in range(0, 150):
    cart.do_tick(0.05, np.arctan(1/10))
    print(cart.position, cart.velocity, cart.acceleration, cart.power)
    

"""

class TrainTack:
    def __init__(self, dimensions_of_track = [10000, 10000], angle_of_track = np.arctan(1/10), start_carts = []):
        
        self.carts = start_carts
        self.dimensions_of_track = dimensions_of_track
        self.angle = angle_of_track
    
        
        


"""