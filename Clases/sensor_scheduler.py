import json
import threading
import time
from datetime import datetime
from .arduino import leer_serial_una_vez

class SensorScheduler:
    def __init__(self, puerto_serial="COM6", devices_file="Jsons_DATA/devices.json"):
        self.puerto_serial = puerto_serial
        self.devices_file = devices_file
        self.sensor_threads = {}
        self.running = False
        self.devices = []
        
    def cargar_dispositivos(self):
        """Carga los dispositivos desde el archivo JSON"""
        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                self.devices = json.load(f)
            print(f"📱 Dispositivos cargados: {len(self.devices)}")
            
            # Mostrar información de cada dispositivo
            for device in self.devices:
                interval = device.get('reading_interval', 300)
                name = device.get('name', 'Desconocido')
                code = device.get('code', 'N/A')
                print(f"   🔄 {name} ({code}): cada {interval}s ({interval/60:.1f} min)")
                
        except FileNotFoundError:
            print(f"❌ No se encontró el archivo de dispositivos: {self.devices_file}")
            self.devices = []
        except Exception as e:
            print(f"❌ Error cargando dispositivos: {e}")
            self.devices = []
    
    def crear_hilo_sensor(self, device):
        """Crea un hilo para leer un sensor específico con su intervalo"""
        def leer_sensor_periodico():
            sensor_code = device.get('code')
            interval = device.get('reading_interval', 300)
            name = device.get('name', 'Sensor')
            
            print(f"🚀 Iniciando hilo para {name} ({sensor_code}) - Intervalo: {interval}s")
            
            while self.running:
                try:
                    print(f"📊 Leyendo {name} ({sensor_code})...")
                    
                    # Usar la función existente de arduino.py pero filtrar por sensor específico
                    leer_serial_una_vez(
                        puerto=self.puerto_serial,
                        timeout_lectura=30,  # Timeout más corto para lecturas específicas
                        sensor_filter=sensor_code  # Filtrar solo este sensor
                    )
                    
                    print(f"✅ Lectura de {name} completada. Próxima en {interval}s")
                    
                except Exception as e:
                    print(f"❌ Error leyendo {name}: {e}")
                
                # Esperar el intervalo específico de este sensor
                time.sleep(interval)
        
        return threading.Thread(target=leer_sensor_periodico, daemon=True)
    
    def iniciar_programacion(self):
        """Inicia todos los hilos de sensores con sus intervalos específicos"""
        if self.running:
            print("⚠️ El programador ya está en ejecución")
            return
            
        self.cargar_dispositivos()
        
        if not self.devices:
            print("❌ No hay dispositivos para programar")
            return
        
        self.running = True
        print(f"🚀 Iniciando programador de sensores para {len(self.devices)} dispositivos...")
        
        # Crear un hilo para cada sensor
        for device in self.devices:
            sensor_code = device.get('code')
            if sensor_code:
                hilo = self.crear_hilo_sensor(device)
                self.sensor_threads[sensor_code] = hilo
                hilo.start()
        
        print(f"✅ {len(self.sensor_threads)} hilos de sensores iniciados")
        
    def detener_programacion(self):
        """Detiene todos los hilos de sensores"""
        print("🛑 Deteniendo programador de sensores...")
        self.running = False
        
        # Esperar a que todos los hilos terminen
        for sensor_code, hilo in self.sensor_threads.items():
            if hilo.is_alive():
                print(f"   ⏳ Esperando a {sensor_code}...")
                hilo.join(timeout=5)
        
        self.sensor_threads.clear()
        print("✅ Programador de sensores detenido")
    
    def obtener_estado(self):
        """Obtiene el estado actual del programador"""
        hilos_activos = sum(1 for hilo in self.sensor_threads.values() if hilo.is_alive())
        
        return {
            "running": self.running,
            "total_devices": len(self.devices),
            "active_threads": hilos_activos,
            "sensors": [
                {
                    "code": device.get('code'),
                    "name": device.get('name'),
                    "interval": device.get('reading_interval', 300),
                    "active": self.sensor_threads.get(device.get('code'), {}).is_alive() if device.get('code') in self.sensor_threads else False
                }
                for device in self.devices
            ]
        }
    
    def recargar_dispositivos(self):
        """Recarga los dispositivos y reinicia la programación"""
        print("🔄 Recargando configuración de dispositivos...")
        
        # Detener hilos actuales
        self.detener_programacion()
        
        # Recargar y reiniciar
        time.sleep(1)  # Pequeña pausa
        self.iniciar_programacion()

# Función helper para usar desde main.py
def iniciar_sensor_scheduler(puerto="COM6"):
    """Función helper para iniciar el programador desde main.py"""
    scheduler = SensorScheduler(puerto_serial=puerto)
    return scheduler
