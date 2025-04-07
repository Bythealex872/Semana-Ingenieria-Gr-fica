import subprocess
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# Configuración inicial de la gráfica
MAX_DATA_POINTS = 100
temps = deque(maxlen=MAX_DATA_POINTS)
times = deque(maxlen=MAX_DATA_POINTS)

fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_ylim(20, 100)  # Rango de temperatura esperado
ax.set_title('Monitor de Temperatura de la CPU en Tiempo Real')
ax.set_xlabel('Tiempo (últimos segundos)')
ax.set_ylabel('Temperatura (°C)')
ax.grid(True)

def get_cpu_temp():
    try:
        output = subprocess.check_output(['sensors']).decode('utf-8')
        # Buscar la línea que contiene "Package id 0"
        for line in output.split('\n'):
            if 'Package id 0' in line:
                match = re.search(r'\+(\d+\.\d+)°C', line)
                if match:
                    return float(match.group(1))
        return None
    except Exception as e:
        print("Error:", e)
        return None

def update(frame):
    temp = get_cpu_temp()
    if temp is not None:
        temps.append(temp)
        times.append(len(times))  # Usamos el índice como tiempo
        
        line.set_data(times, temps)
        ax.relim()
        ax.autoscale_view(scalex=True, scaley=False)
        ax.set_xlim(max(0, len(times)-MAX_DATA_POINTS), len(times))
    
    return line,

# Configurar la animación
ani = animation.FuncAnimation(
    fig, 
    update, 
    interval=1000,  # Actualizar cada 1000 ms (1 segundo)
    cache_frame_data=False
)

plt.show()
