import pandas as pd
import numpy as np
import datetime
import math

class TrainTrack:
    def __init__(self, carts  100, track_dimensions = [20000, 2000], mass_per_cart = 67.5 * 2170), power_demand = 0):
        
        # TODO make it so that the carts get placed in their relevant place instead of being put by default on top.
        self.carts_on_track = []# Each cart on the track will be reprisented by a number which indicates its position on the track.
        self.velocity = 0# The velocity of the track.
        self.net_force = 0
        self.carts_of_track = {"Bottom" : [], "Top" : carts}# All the carts by default start at the top.
        
        self.track_length = track_dimensions[0]
        self.track_height = track_dimensions[1]
        self.angle = np.arctan(track_dimensions[1] / track_dimensions[0])
        
        self.mass_per_cart = mass_per_cart
        
        self.power_demand = power_demand
        self.power = 0
        
        
        self.minimal_distance = 100
        
        
        
        self.force_of_generator = 0
        
        
        
        
        
        self.losses = {"Friction" : 0, "Efficiency" : 0}
    
    def get_friction(self, velocity = math.nan, density_air = 1.275):
        # Todo add proper friction https://www.sciencedirect.com/science/article/pii/S0043164814003718
        g = 9.81
        
        drag_coefficient = 1.05 * (2.591 * 2.438)
        friction_coefficient = 0.01# Uit duim gezogen
        
        if velocity == math.nan:
            velocity = self.velocity
        
        return len(self.carts_of_track) * np.sign(velocity) * (density_air * velocity**2 * drag_coefficient / 2 + abs(velocity) * np.cos(self.angle) * g * self.mass_per_cart * friction_coefficient)
    
    
    def get_gravity(self):
        return - np.sin(self.angle) * g * len(self.carts_on_track) * self.mass_per_cart
    
    def get_kinetic_energy_per_cart(self, velocity = math.nan):
        if velocity = math.nan:
            return (1/2) * self.mass_per_cart * self.velocity**2
        else:
            return (1/2) * self.mass_per_cart * velocity**2
    
    def add_cart(self, location = ""):
        
        if np.sign(self.velocity) > 0 and location == "":
            location = "Bottom"
        elif np.sign(self.velocity) <= 0 and location == ":
            location = "Top"
        
        
        if (location == "Top" and (self.track_length - max(self.carts_on_track)) > self.minimal_distance) or (location == "Bottom" and min(self.carts_on_track) > self.minimal_distance):
            
            self.velocity = np.sign(self.velocity) * np.sqrt(len(self.carts_on_track) self.velocity**2 / (len(self.carts_on_track) + 1))# v_new = sqrt[m_intital v_initial /(m_initial + m_cart)]
            
            if location == "Top":
                if self.carts_of_track["Top"] > 0:
                    self.carts_of_track.append(self.track_length)
                    self.carts_of_track["Top"] = self.carts_of_track["Top"] - 1
                    return True
                else:
                    return False
            elif location == "Bottom":
                if self.carts_of_track["Bottom"] > 0:
                    self.carts_of_track.append(0)
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
        elif len(self.carts_on_track) == 1:
            energy_left_over = self.get_kinetic_energy_per_cart()
            
        
        
    
    def set_force(self):
        
        
        
    
    def do_tick(self, delta_time):
        
        



