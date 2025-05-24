import pyomo.environ as pyo
import pandas as pd
from airline_model import create_model
import tkinter as tk
from tkinter import ttk, filedialog

aviones_file = None
costos_file = None
vuelos_file = None

def select_file(prompt, label_widget):
    path = filedialog.askopenfilename(
        title=prompt, 
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
    if path:
        label_widget.config(text=path)
        return path
    
def select_aviones_file():
    global aviones_file
    aviones_file = select_file("Seleccionar archivo de aviones", label_file_aviones)

def select_costos_file():
    global costos_file
    costos_file = select_file("Seleccionar archivo de costos", label_file_costos)

def select_vuelos_file():
    global vuelos_file
    vuelos_file = select_file("Seleccionar archivo de vuelos", label_file_vuelos)

def run_optimization():
    try:
        if not (aviones_file and costos_file and vuelos_file):
            text_results.delete(1.0, tk.END)
            text_results.insert(tk.END, "Por favor, seleccione todos los archivos CSV.")
            return
        
        aviones_df = pd.read_csv(aviones_file) 
        costos_df = pd.read_csv(costos_file) 
        vuelos_df = pd.read_csv(vuelos_file)

        # Parámetros del modelo
        D = int(entry_D.get())
        M = int(entry_M.get())
        delta = int(entry_delta.get())

        model = create_model(aviones_df, costos_df, vuelos_df, D, M, delta)

        solver = pyo.SolverFactory('glpk')
        solver.solve(model, tee=True)

        result_str = f"Costo mínimo de operación: ${model.obj():,.2f}\n\n"
        result_str += "Asignación de vuelos a aviones:\n"
        for f in model.F:
            result_str += f"{f}:\n"
            for d in model.D:
                result_str += f"\tDía {d}:\n"
                for a in model.A:
                    if model.x[f, a, d].value == 1:
                        result_str += f"\t\tasignado al {a}\n"
                        
        result_str += "\nEstado de operación de aviones:\n"
        for a in model.A:
            result_str += f"{a}:\n"
            for d in model.D:
                estado = 'Operativo' if model.y[a, d].value == 1 else 'Libre'
                result_str += f"\ten día {d}: {estado}\n"

        text_results.delete(1.0, tk.END)
        text_results.insert(tk.END, result_str)
    
    except Exception as e:
        text_results.delete(1.0, tk.END)
        text_results.insert(tk.END, f"Ocurrió un error: {e}")

# Ventana principal
root = tk.Tk()
root.title("Optimización de Operación de Aviones")
root.geometry("1000x800")
root.resizable(False, False)

# Ubicación de archivos CSV
frame_files = ttk.LabelFrame(root, text="Selección de Archivos CSV")
frame_files.pack(padx=10, pady=10, fill=tk.X)

# Botones y etiquetas para seleccionar los archivos
button_aviones = ttk.Button(frame_files, text="Seleccionar archivo de aviones", command=select_aviones_file)
button_aviones.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
label_file_aviones = ttk.Label(frame_files, text="No ha seleccionado archivo")
label_file_aviones.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

button_costos = ttk.Button(frame_files, text="Seleccionar archivo de costos", command=select_costos_file)
button_costos.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
label_file_costos = ttk.Label(frame_files, text="No ha seleccionado archivo")
label_file_costos.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

button_vuelos = ttk.Button(frame_files, text="Seleccionar archivo de vuelos", command=select_vuelos_file)
button_vuelos.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
label_file_vuelos = ttk.Label(frame_files, text="No ha seleccionado archivo")
label_file_vuelos.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

#Parametros de entrada
frame_params = ttk.LabelFrame(root, text="Parámetros de Entrada")
frame_params.pack(padx=10, pady=10, fill=tk.X)

label_D = ttk.Label(frame_params, text="D (días):")
label_D.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_D = ttk.Entry(frame_params, width=10)
entry_D.grid(row=0, column=1, padx=5, pady=5)
entry_D.insert(0, "5")

label_M = ttk.Label(frame_params, text="M (días sin mantenimiento):")
label_M.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_M = ttk.Entry(frame_params, width=10)
entry_M.grid(row=1, column=1, padx=5, pady=5)
entry_M.insert(0, "3")

label_delta = ttk.Label(frame_params, text="Delta (Tiempo de espera en horas):")
label_delta.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
entry_delta = ttk.Entry(frame_params, width=10)
entry_delta.grid(row=2, column=1, padx=5, pady=5)
entry_delta.insert(0, "2")

# Botón para ejecutar la optimización
frame_controls = ttk.Frame(root)
frame_controls.pack(padx=10, pady=10)

button_run = ttk.Button(frame_controls, text="Ejecutar Optimización", command=run_optimization)
button_run.pack()

# Widget de texto para mostrar los resultados
text_results = tk.Text(root, wrap="word", width=80, height=25)
text_results.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()