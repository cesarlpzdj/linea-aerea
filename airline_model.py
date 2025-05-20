import pyomo.environ as pyo
import pandas as pd
import numpy as np

aviones_df = pd.read_csv('aviones.csv') 
costos_df = pd.read_csv('costos.csv') 
vuelos_df = pd.read_csv('vuelos.csv')

model = pyo.ConcreteModel()

model.A = pyo.Set(initialize=aviones_df['Avion'])
model.F = pyo.Set(initialize=vuelos_df['Vuelo']) 
model.D = pyo.RangeSet(1, 150) # Pass this as a param, prompt for this value from UI

# Parametros
costos_df = costos_df.pivot(index='Vuelo', columns='Avion', values='Costo_Operacion')
print(costos_df)

# Variables de decision
model.x = pyo.Var(model.F, model.A, model.D, initialize=1)
model.y = pyo.Var(model.A, model.D, initialize=1)

# Funcion objetivo
def func_objetivo(m):
    return sum(sum(sum(m.x[f, a, d] * costos_df.loc[f, a] for a in m.A) for f in m.F) for d in m.D)

model.obj = pyo.Objective(rule=func_objetivo, sense=pyo.minimize)