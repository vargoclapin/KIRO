from math import *

rho = 6.371*10**6
def convertirLat(phi1, phi2):
    return rho*2*pi/360*(phi1-phi2)

def convertirLon(phi1, phi2):
    return rho*cos(2*pi*2.34842/360)*2*pi/360*(phi1-phi2)

def distanceM(point1, point2):
    return abs(convertirLon(point1[0], point2[0]))+ abs(convertirLat(point1[1], point2[1]))

def distanceE(point1, point2):
    return sqrt((convertirLon(point1[0], point2[0]))**2+ (convertirLat(point1[1], point2[1]))**2)


import pandas as pd
instance = pd.read_csv("instances/instance_01.csv")

vehicules = pd.read_csv("vehicles.csv")
def reference_travel_time(f, i, j):
    x1 = instance.loc[i]["longitude"]
    x2 = instance.loc[j]["longitude"]
    y1 = instance.loc[i]["latitude"]
    y2 = instance.loc[j]["latitude"]
    sf = vehicules.loc[f-1]["speed"]
    pf = vehicules.loc[f-1]["parking_time"]
    return distanceE((x1,y1), (x2,y2))/sf + pf

def miam(f,t):
    k = 0 
    a = [vehicules.loc[f-1]["fourier_cos_0"],vehicules.loc[f-1]["fourier_cos_1"],vehicules.loc[f-1]["fourier_cos_2"],vehicules.loc[f-1]["fourier_cos_3"]]
    b = [vehicules.loc[f-1]["fourier_sin_0"],vehicules.loc[f-1]["fourier_sin_1"],vehicules.loc[f-1]["fourier_sin_2"],vehicules.loc[f-1]["fourier_sin_3"]]
    for i in range(4):
        k+= a[i]*cos(i*2*pi/86400*t) + b[i]*sin(i*2*pi/86400 * t)
    return k

def travel_time(f, i, j, t):
    return reference_travel_time(f, i, j)*miam(f,t)

def rental_cost(route):
    return vehicules.loc[route[0]-1]["rental_cost"]

def fuel_cost(route):
    cout = vehicules.loc[route[0]-1]["fuel_cost"]
    chemin = route[2]
    k=0
    for i in range(len(chemin)-1):
        x1 = instance.loc[i]["longitude"]
        x2 = instance.loc[i+1]["longitude"]
        y1 = instance.loc[i]["latitude"]
        y2 = instance.loc[i+1]["latitude"]
        k+= distanceM((x1,y1),(x2,y2))
    
    return cout*k

def radius_cost(route):
    cout = vehicules.loc[route[0]]["radius_cost"]
    chemin = route[2]
    maxi = 0
    for i in range(1,len(chemin)-1):
        for j in range(1, len(chemin)-1):
            x1 = instance.loc[i]["longitude"]
            x2 = instance.loc[j]["longitude"]
            y1 = instance.loc[i]["latitude"]
            y2 = instance.loc[j]["latitude"]
            dist=distanceE((x1,y1),(x2,y2))
            if dist>maxi:
                maxi = dist

    return cout*(0.5*maxi)**2

def cout_total(sol):
    total = 0 
    for i in sol:
        total += rental_cost(i)+ fuel_cost(i) + radius_cost(i)
    return total

#Fonction qui construit les listes des temps d'arrivee et de depart de chaque sommet
import numpy as np
def arrivees_departs(f, chemin):
    n = len(chemin)
    garer = vehicules.loc[f-1]["parking_time"]
    arrivees = np.zeros(n)
    departs = np.zeros(n)
    t = 0 
    for i in range(1,n-1):
        arrivees[i] = departs[i-1] + travel_time(f, chemin[i-1], chemin[i], t)
        departs[i] = max(arrivees[i]+garer, instance.loc[i]["window_start"])+instance.loc[i]["delivery_duration"]
        t = departs[i]
    arrivees[n] = departs[i-1] + travel_time(f, chemin[n-1], chemin[n], t)
    return arrivees, departs