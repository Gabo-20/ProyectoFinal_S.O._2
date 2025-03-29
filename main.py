import psutil
import tkinter as tk
from tkinter import ttk, messagebox

procesos_totales = []

#Funcion para obtener los procesos activos
def obtener_procesos():
    global procesos_totales
    procesos_totales = []

    #Se itera en los procesos activos y se obtienen los datos necesarios
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            pid = proc.info['pid']
            nombre = proc.info['name']
            cpu = proc.info['cpu_percent']
            memoria_bytes = proc.info['memory_info'].rss
            memoria_mb = memoria_bytes / (1024 ** 2)
            procesos_totales.append((pid, nombre, f"{cpu:.1f}%", f"{memoria_mb:.1f} MB"))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    aplicar_filtro()

    # Actualiza la tabla cada 9 segundos
    ventana.after(9000, obtener_procesos)

# Funciones para aplicar filtro, finalizar, suspender y reanudar procesos
def aplicar_filtro():
    filtro = entry_busqueda.get().lower()
    for item in tree.get_children():
        tree.delete(item)

    for proceso in procesos_totales:
        pid, nombre, cpu, mem = proceso
        if filtro in str(pid).lower() or filtro in nombre.lower():
            tree.insert('', 'end', values=(pid, nombre, cpu, mem))

# Función para obtener el PID y nombre del proceso seleccionado
def obtener_pid_seleccionado():
    item = tree.selection()
    if not item:
        messagebox.showwarning("Advertencia", "Selecciona un proceso primero.")
        return None
    pid = int(tree.item(item, 'values')[0])
    nombre = tree.item(item, 'values')[1]
    return pid, nombre

# Funciones para registrar eventos en la consola
def log_evento(texto):
    consola.config(state='normal')
    consola.insert(tk.END, texto + '\n')
    consola.yview_moveto(1.0)
    consola.config(state='disabled')

# Funcion para finalizar proceso seleccionado
def finalizar_proceso():
    resultado = obtener_pid_seleccionado()
    if resultado:
        pid, nombre = resultado
        try:
            p = psutil.Process(pid)
            p.kill()
            log_evento(f"PID: {pid} | Nombre: {nombre} -> Se FINALIZÓ.")
            messagebox.showinfo("Éxito", f"Proceso {pid} finalizado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

#Funcion para suspender proceso seleccionado
def suspender_proceso():
    resultado = obtener_pid_seleccionado()
    if resultado:
        pid, nombre = resultado
        try:
            p = psutil.Process(pid)
            p.suspend()
            log_evento(f"PID: {pid} | Nombre: {nombre} -> Se SUSPENDIÓ.")
            messagebox.showinfo("Éxito", f"Proceso {pid} suspendido.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

#Funcion para reanudar proceso seleccionado
def reanudar_proceso():
    resultado = obtener_pid_seleccionado()
    if resultado:
        pid, nombre = resultado
        try:
            p = psutil.Process(pid)
            p.resume()
            log_evento(f"PID: {pid} | Nombre: {nombre} -> Se REANUDÓ.")
            messagebox.showinfo("Éxito", f"Proceso {pid} reanudado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# Interfaz
ventana = tk.Tk()
ventana.title("Procesos Activos")
ventana.geometry("850x600")

# Buscador
frame_busqueda = tk.Frame(ventana)
frame_busqueda.pack(pady=10)

tk.Label(frame_busqueda, text="Buscar proceso (nombre o PID):").pack(side='left')
entry_busqueda = tk.Entry(frame_busqueda)
entry_busqueda.pack(side='left', padx=5)
entry_busqueda.bind('<KeyRelease>', lambda event: aplicar_filtro())

# Tabla
columnas = ('PID', 'Nombre', 'CPU (%)', 'Memoria (MB)')
tree = ttk.Treeview(ventana, columns=columnas, show='headings')

for col in columnas:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(fill='both', expand=True, padx=10, pady=10)

# Botones
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

tk.Button(frame_botones, text="Finalizar Proceso", command=finalizar_proceso, bg="red", fg="white").pack(side='left', padx=5)
tk.Button(frame_botones, text="Suspender Proceso", command=suspender_proceso, bg="orange").pack(side='left', padx=5)
tk.Button(frame_botones, text="Reanudar Proceso", command=reanudar_proceso, bg="green", fg="white").pack(side='left', padx=5)

# Consola de eventos
frame_consola = tk.Frame(ventana)
frame_consola.pack(pady=10, fill='both', expand=True)

tk.Label(frame_consola, text="Consola de eventos:").pack(anchor='w', padx=10)

consola = tk.Text(frame_consola, height=8, bg='black', fg='lime', state='disabled')
consola.pack(fill='both', expand=True, padx=10)

obtener_procesos()

ventana.mainloop()
