import pyomo.environ as pyo
import pandas as pd

def create_model(aviones_df, costos_df, vuelos_df, D, M, delta):
    overlaps = {}
    # Crear diccionario de traslapes
    for i, row_i in vuelos_df.iterrows():
        vuelo_i, salida_i, llegada_i = row_i["Vuelo"], row_i["Hora_Salida"], row_i["Hora_Llegada"]
        for j, row_j in vuelos_df.iterrows():
            if i >= j: continue
            vuelo_j, salida_j, llegada_j = row_j["Vuelo"], row_j["Hora_Salida"], row_j["Hora_Llegada"]
            if (salida_i < llegada_j + delta and salida_j < llegada_i + delta):
                overlaps[(vuelo_i, vuelo_j)] = 1
            else:
                overlaps[(vuelo_i, vuelo_j)] = 0

    aviones_df = aviones_df.set_index('Avion')
    vuelos_df = vuelos_df.set_index('Vuelo')

    model = pyo.ConcreteModel()
    model.A = pyo.Set(initialize=list(aviones_df.index.map(str)))
    model.F = pyo.Set(initialize=list(vuelos_df.index.map(str))) 
    # Pass this as a param, prompt for this value from UI
    model.D = pyo.RangeSet(1, D) 

    # Parametros
    costos_df = costos_df.pivot(index='Vuelo', columns='Avion', values='Costo_Operacion')

    # Variables de decision
    model.x = pyo.Var(model.F, model.A, model.D, initialize=1, within=pyo.Binary)
    model.y = pyo.Var(model.A, model.D, initialize=1, within=pyo.Binary)

    # Funcion objetivo
    def func_objetivo(m): # Tratar Cambiar a Linear expression
        return sum(m.x[f, a, d] * costos_df.loc[f, a] for f in m.F for a in m.A for d in m.D)
    model.obj = pyo.Objective(rule=func_objetivo, sense=pyo.minimize)

    def demanda_rule(m, f, a, d): # Tratar Cambiar a Linear expression
        return m.x[f, a, d] * vuelos_df.loc[f, 'Demanda'] <= aviones_df.loc[a, 'Capacidad']
    model.demanda = pyo.Constraint(model.F, model.A, model.D, rule=demanda_rule)

    def operacion_rule(m, f, a, d):
        return m.y[a, d] >= m.x[f, a, d]
    model.operacion = pyo.Constraint(model.F, model.A, model.D, rule=operacion_rule)

    def once_per_day_rule(m, f, d):
        return sum(m.x[f, a, d] for a in m.A) == 1
    model.once = pyo.Constraint(model.F, model.D, rule=once_per_day_rule)

    def mantenimiento_rule(m, a, d):
        if d + M > len(model.D):
            return pyo.Constraint.Skip
        return sum(m.y[a, _d] for _d in range(d, d + M + 1)) <= M
    model.mantto = pyo.Constraint(model.A, model.D, rule=mantenimiento_rule)

    model.overlap_cons = pyo.ConstraintList()
    for (f1, f2), isOverlap in overlaps.items():
        if isOverlap == 1:
            for a in model.A:
                for d in model.D:
                    model.overlap_cons.add(model.x[f1, a, d] + model.x[f2, a, d] <= 1)
    return model