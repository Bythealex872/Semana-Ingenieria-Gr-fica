import sys
import subprocess
import re
from collections import deque
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

class SafeRealTimePlot(QtWidgets.QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.initUI()
            self.initData()
            self.initTimer()
        except Exception as e:
            print(f"Error de inicialización: {str(e)}")
            sys.exit(1)

    def initUI(self):
        try:
            self.setWindowTitle('Monitor de Temperatura Seguro')
            self.setGeometry(150, 150, 1000, 700)
            
            self.plot_widget = pg.PlotWidget()
            self.setCentralWidget(self.plot_widget)
            
            # Configuración de estilos segura
            self.plot_widget.setBackground('#0A0A0A')
            self.plot_widget.setTitle("Temperatura CPU", color='#FFFFFF', size='12pt')
            self.plot_widget.setLabel('left', '°C', color='#FFFFFF')
            self.plot_widget.setLabel('bottom', 'Segundos', color='#FFFFFF')
            self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
            self.plot_widget.getAxis('left').setPen(pg.mkPen('#FFFFFF'))
            self.plot_widget.getAxis('bottom').setPen(pg.mkPen('#FFFFFF'))
            
            self.plot_curve = self.plot_widget.plot(pen=pg.mkPen('#FF5555', width=1.5))
        except Exception as e:
            print(f"Error en UI: {str(e)}")
            raise

    def initData(self):
        self.max_points = 200
        self.temps = deque(maxlen=self.max_points)
        self.times = deque(maxlen=self.max_points)
        self.time_counter = 0

    def initTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.safeUpdate)
        self.timer.start(1500)  # Intervalo más seguro

    def getCpuTempSafe(self):
        try:
            result = subprocess.run(['sensors'], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True,
                                  timeout=2)
            
            for line in result.stdout.split('\n'):
                if 'Package id 0' in line:
                    match = re.search(r'\+(?P<temp>\d+\.\d+)°C', line)
                    if match:
                        return float(match.group('temp'))
            return None
        except subprocess.CalledProcessError:
            print("Error en comando sensors: Permisos o instalación incorrecta")
            return None
        except subprocess.TimeoutExpired:
            print("Timeout en lectura de sensores")
            return None
        except Exception as e:
            print(f"Error inesperado en sensor: {str(e)}")
            return None

    def safeUpdate(self):
        try:
            temp = self.getCpuTempSafe()
            if temp is not None and 0 < temp < 120:  # Filtro de seguridad
                self.temps.append(temp)
                self.times.append(self.time_counter)
                self.time_counter += 1

                self.plot_curve.setData(
                    x=list(self.times),
                    y=list(self.temps),
                    pen=pg.mkPen('#FF5555', width=1.5)
                )

                if len(self.times) > 1:
                    self.plot_widget.setXRange(
                        max(0, self.time_counter - self.max_points),
                        self.time_counter + 5
                    )
                    self.plot_widget.setYRange(
                        max(0, min(self.temps)-5),
                        max(self.temps)+5
                    )
        except Exception as e:
            print(f"Error en actualización: {str(e)}")
            self.timer.stop()

def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Configuración de paleta segura
        palette = app.palette()
        palette.setColor(palette.Window, QtGui.QColor('#1A1A1A'))
        palette.setColor(palette.WindowText, QtGui.QColor('#FFFFFF'))
        app.setPalette(palette)
        
        window = SafeRealTimePlot()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
