import json
import threading
import time
import re
from datetime import datetime
from .arduino import guardar_dato  # Tu función que guarda en Mongo/historial

class SensorScheduler:
    def __init__(self, puerto_serial="COM6", devices_file="Jsons_DATA/devices.json"):
        self.puerto_serial = puerto_serial
        self.devices_file = devices_file
        self.running = False
        self.devices = []
        self.hilo_lector = None

    def cargar_dispositivos(self):
        """Carga la configuración de sensores desde el archivo JSON."""
        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                self.devices = json.load(f)
            print(f"📱 Dispositivos cargados: {len(self.devices)}")
            for device in self.devices:
                print(f"   🔄 {device.get('name', 'Desconocido')} ({device.get('code')}): cada {device.get('reading_interval', 300)}s")
        except FileNotFoundError:
            print(f"❌ No se encontró {self.devices_file}")
            self.devices = []
        except Exception as e:
            print(f"❌ Error cargando dispositivos: {e}")
            self.devices = []

    def hilo_lectura_serial(self):
        """Hilo único que lee TODAS las lecturas de Arduino y las guarda."""
        import serial

        try:
            ser = serial.Serial(self.puerto_serial, 9600, timeout=1)
            print(f"📡 Escuchando en {self.puerto_serial}...")

            while self.running:
                try:
                    linea = ser.readline().decode(errors="ignore").strip()
                    if not linea:
                        continue

                    print(f"📨 Recibido: {linea}")

                    match = re.match(r"([^:]+):(.+)", linea)
                    if match:
                        sensor_code = match.group(1)  # ej: tmp/1 o nivel/1
                        valor = match.group(2)

                        # Guardar dato usando tu función existente
                        guardar_dato(sensor_code, valor)

                except Exception as e:
                    print(f"❌ Error en lectura serial: {e}")
                    time.sleep(1)

        except Exception as e:
            print(f"❌ No se pudo abrir {self.puerto_serial}: {e}")

    def iniciar_programacion(self):
        """Inicia el hilo único de lectura."""
        if self.running:
            print("⚠️ El programador ya está en ejecución")
            return

        self.cargar_dispositivos()
        if not self.devices:
            print("⚠️ No hay dispositivos configurados")
            return

        self.running = True
        print("🚀 Iniciando lector único de sensores...")

        self.hilo_lector = threading.Thread(target=self.hilo_lectura_serial, daemon=True)
        self.hilo_lector.start()

    def detener_programacion(self):
        """Detiene el hilo de lectura."""
        print("🛑 Deteniendo lector de sensores...")
        self.running = False
        if self.hilo_lector and self.hilo_lector.is_alive():
            self.hilo_lector.join(timeout=5)
        print("✅ Lector de sensores detenido")

    def obtener_estado(self):
        """Devuelve el estado del lector."""
        return {
            "running": self.running,
            "total_devices": len(self.devices),
            "active_threads": 1 if self.hilo_lector and self.hilo_lector.is_alive() else 0,
            "sensors": [
                {
                    "code": d.get('code'),
                    "name": d.get('name'),
                    "interval": d.get('reading_interval', 300),
                    "active": True
                }
                for d in self.devices
            ]
        }
