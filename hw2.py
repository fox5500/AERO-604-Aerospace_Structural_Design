import numpy as np
from scipy.optimize import minimize
import math

L = 10
rho = 3
W = 1000
x = 1 # x is the location where the load is applied
w = (2 * W / (math.pi * L)) * math.sqrt(1 - (x / L)**2)
c = 5



def calculate_max_bending_moment(w, L, y):
    # Calculate the maximum bending moment
    M_max = (w * L**2) / (8 * y)
    
    return M_max

def calculate_spar_mass(tw, tf, hw, hf, rho):
    # Calculate the cross-sectional area
    A = tw * hw + tf * hf
    
    # Calculate the volume
    V = A * L
    
    # Calculate the mass
    m = rho * V
    
    return m

import math

def calculate_distance_from_centroid(c, W, L):
    # Calculate the distance from centroid
    y = L / 2 - math.sqrt((L / 2)**2 - (W / (math.pi * (W / L))) * c)
    
    return y


def calculate_max_stress(tw, tf, hw, hf):
    # Calculate the moment of inertia
    I = calculate_moment_of_inertia(tw, tf, hw, hf)
    
    # Calculate the maximum bending moment
    M_max = calculate_max_bending_moment(tw, tf, hw,)
    
    # Calculate the distance from the neutral axis to the centroid
    c = calculate_distance_from_centroid(tw, tf, hw,)
    
    # Calculate the maximum stress
    sigma_max = M_max * c / I
    
    return sigma_max
    
    
def calculate_moment_of_inertia(tw, tf, hw, hf):
    # Calculate the moment of inertia about the x-axis
    Ixx = (tw * hw**3 + tf * hf**3) / 12
    
    return Ixx

def spar_mass(x):
    tw, tf, hw, hf = x
    
    # Calculate the mass of the spar
    mass = calculate_spar_mass(tw, tf, hw, hf, rho)
    
    # Calculate the maximum stress
    sigma_max = calculate_max_stress(tw, tf, hw, hf)

   
    # Calculate the moment of inertia
    Izz = calculate_moment_of_inertia(tw, tf, hw, hf)
    
    # Check the constraints
    if sigma_max > 40 or Izz < 0.1:
        return np.inf
    
    return mass

# Define the bounds for the variables
bounds = [(0.01, 10), (0.01, 10), (0.01, 10), (0.01, 10)]

# Use minimize to minimize the total mass subject to the constraints
x0 = [0.01, 0.01, 0.01, 0.01]
res = minimize(spar_mass, x0, bounds=bounds)

# Get the optimal values for tw, tf, hw, and hf
tw_opt, tf_opt, hw_opt, hf_opt = res.x
