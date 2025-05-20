import pyomo.environ as pyo
import pandas as pd
import numpy as np

aviones_df = pd.read_csv('aviones.csv', index_col=0) 
costos_df = pd.read_csv('costos.csv') 
vuelos_df = pd.read_csv('vuelos.csv', index_col=0)
# vuelos_df = pd.read_csv('vuelos.csv', dtype={'Vuelo':str})
# vuelos_df.set_index('Vuelo', inplace=True)

model = pyo.ConcreteModel()

model.A = pyo.Set(initialize=list(aviones_df.index.map(str)))
model.F = pyo.Set(initialize=list(vuelos_df.index.map(str))) 
model.D = pyo.RangeSet(1, 150) # Pass this as a param, prompt for this value from UI

# Parametros
costos_df = costos_df.pivot(index='Vuelo', columns='Avion', values='Costo_Operacion')
#print(costos_df)

print(vuelos_df.loc['Vuelo_1', 'Demanda'])

# Variables de decision
model.x = pyo.Var(model.F, model.A, model.D, initialize=1, bounds=(0,1), within=pyo.Binary)
model.y = pyo.Var(model.A, model.D, initialize=1, bounds=(0,1), within=pyo.Binary)

# Funcion objetivo
def func_objetivo(m):
    return sum(sum(sum(m.x[f, a, d] * costos_df.loc[f, a] for a in m.A) for f in m.F) for d in m.D)
model.obj = pyo.Objective(rule=func_objetivo, sense=pyo.minimize)

def demanda_rule(m, f, a, d):
    return m.x[f, a, d] * vuelos_df.loc[f, 'Demanda'] <= aviones_df.loc[a, 'Capacidad']
model.demanda = pyo.Constraint(model.F, model.A, model.D, rule=demanda_rule)

def operacion_rule(m, f, a, d):
    return m.y[a, d] >= m.x[f, a, d]
model.operacion = pyo.Constraint(model.F, model.A, model.D, rule=operacion_rule)

def once_per_day_rule(m, f, d):
    return sum(m.x[f, a, d] for a in m.A) == 1
model.once = pyo.Constraint(model.F, model.D, rule=once_per_day_rule)

def flights_overlap(f1, f2):
    return 0 if f1['Hora_Llegada'] > f2['Hora_Salida'] else 1

# def overlap_rule(m, a, d):
#     return 