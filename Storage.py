import pandas as pd
import numpy as np
import datetime
import math

class TrainTrack:
    def __init__(self, carts = 100, track_dimensions = [20000, 2000], mass_per_cart = 67.5 * 2170):
        
        # TODO make it so that the carts get placed in their relevant place instead of being put by default on top.
        self.carts_on_track = []# Each cart on the track will be reprisented by a number which indicates its position on the track.
        self.velocity = 0# The velocity of the track.
        self.net_force = 0
        self.carts_of_track = {"Bottom" : [], "Top" : carts}# All the carts by default start at the top.
        
        self.track_length = track_dimensions[0]
        self.track_height = track_dimensions[1]
        self.angle = np.arctan(track_dimensions[1] / track_dimensions[0])
        
        self.mass_per_cart = mass_per_cart
        
        
        self.power = 0
        
        
        self.minimal_distance = 100
        
        
        
        self.force_of_generator = 0
        self.other_power = 0
        
        
        
        
        
        self.losses = {"Friction" : 0, "Efficiency" : 0}
    
    def get_friction(self, velocity = "NaN", density_air = 1.275):
        # Todo add proper friction https://www.sciencedirect.com/science/article/pii/S0043164814003718
        g = 9.81
        
        drag_coefficient = 1.05 * (2.591 * 2.438)
        friction_coefficient = 0.01# Uit duim gezogen
        
        if velocity == "NaN":
            velocity = self.velocity
        
        
        return - len(self.carts_of_track) * np.sign(velocity) * (density_air * velocity**2 * drag_coefficient / 2 + abs(velocity) * np.cos(self.angle) * g * self.mass_per_cart * friction_coefficient)
    
    
    def get_gravity(self):
        g = 9.81
        return - np.sin(self.angle) * g * len(self.carts_on_track) * self.mass_per_cart
    
    def get_kinetic_energy_per_cart(self, velocity = "NaN"):
        if velocity == "NaN":
            return (1/2) * self.mass_per_cart * self.velocity**2
        else:
            return (1/2) * self.mass_per_cart * velocity**2
    
    def add_cart(self, location = ""):
        
        if np.sign(self.velocity) > 0 and location == "":
            location = "Bottom"
        elif np.sign(self.velocity) <= 0 and location == "":
            location = "Top"
        
        
        if len(self.carts_on_track) == 0:# The max function doesn't like empty arrays
            max_cart = 0
            min_cart = self.track_length
        else:
            max_cart = max(self.carts_on_track)
            min_cart = min(self.carts_on_track)
        
        if (location == "Top" and (self.track_length - max_cart) > self.minimal_distance) or (location == "Bottom" and min_cart > self.minimal_distance):
            
            self.velocity = np.sign(self.velocity) * np.sqrt(len(self.carts_on_track) * self.velocity**2 / (len(self.carts_on_track) + 1))# v_new = sqrt[m_intital v_initial /(m_initial + m_cart)]
            
            if location == "Top":
                if self.carts_of_track["Top"] > 0:
                    self.carts_on_track.append(self.track_length)
                    self.carts_of_track["Top"] = self.carts_of_track["Top"] - 1
                    return True
                else:
                    return False
            elif location == "Bottom":
                if self.carts_of_track["Bottom"] > 0:
                    self.carts_on_track.append(0)
                    self.carts_of_track["Bottom"] = self.carts_of_track["Bottom"] - 1
                    return True
                else:
                    return False
        
        else:
            return False
    
    def remove_cart(self, delta_time, index):
        
        
        if len(self.carts_on_track) < 1:
            return False
            energy_left_over = 0
        
        if self.carts_on_track[index] > self.track_length / 2:
            location = "Top"
        elif self.carts_on_track[index] <= self.track_length / 2:
            location = "Bottom"
        
        if len(self.carts_on_track) == 1:
            energy_left_over = self.get_kinetic_energy_per_cart()
            
            self.carts_on_track = []
            self.carts_of_track[location] = self.carts_of_track[location] + 1
        elif len(self.carts_on_track) > 1:
            energy_left_over = self.get_kinetic_energy_per_cart()
            
            self.carts_on_track.pop(index)
            self.carts_of_track[location] = self.carts_of_track[location] + 1
        
        self.other_power = self.other_power - energy_left_over / delta_time
        
    
    def do_tick(self, delta_time):
        
        self.power = self.other_power + self.force_of_generator * self.velocity# Set the power
        self.other_power = 0
        
        self.losses["Friction"] = abs(self.get_friction()) * self.velocity
        
        if len(self.carts_on_track) == 0:# Prevent devide by zero error
            acceleration = 0
            self.velocity = 0
        else:
            acceleration = (self.get_gravity() + self.get_friction() + self.force_of_generator) / (len(self.carts_on_track) * self.mass_per_cart)
        
        change_in_position = self.velocity * delta_time + 0.5 * acceleration * delta_time**2
        self.carts_on_track = [i + change_in_position for i in self.carts_on_track]# Change the position of each of the carts.
        self.velocity = self.velocity + acceleration * delta_time
        
        



