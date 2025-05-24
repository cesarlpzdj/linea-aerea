import pyomo.environ as pyo
import pandas as pd
from airline_model import create_model

aviones_df = pd.read_csv('aviones.csv') 
costos_df = pd.read_csv('costos.csv') 
vuelos_df = pd.read_csv('vuelos.csv')

D = 5
M = 3
delta = 2

model = create_model(aviones_df, costos_df, vuelos_df, D, M, delta)

solver = pyo.SolverFactory('glpk')
solver.solve(model, tee=True)

# --- Resultados ---
print(f"Costo mínimo de operación: {model.obj()}")

print("\nAsignación de vuelos a aviones:")
for f in model.F:
    for a in model.A:
        for d in model.D:
            if model.x[f, a, d].value == 1:
                print(f"{f} asignado al {a} en día {d}")

print("\nEstado de operación de aviones:")
for a in model.A:
    for d in model.D:
        print(f"{a} en día {d}: {'Operativo' if model.y[a, d].value == 1 else 'Libre'}")