import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class HTTPSender:
    def __init__(self):
        self.api_url = os.getenv("ADONIS_API_URL", "http://localhost:3333")
        self.endpoint = f"{self.api_url}/api/sensor-data"
        self.headers = {
            'Content-Type': 'application/json'
        }
        
    def enviar_datos_sensor(self, tank_id: int, sensor_data: dict):
        """
        Envía datos de sensor al backend de AdonisJS
        
        Args:
            tank_id: ID del tanque
            sensor_data: Diccionario con los datos del sensor
        """
        try:
            payload = {
                "tank_id": tank_id,
                "sensor": sensor_data.get("sensor"),
                "device_id": sensor_data.get("deviceId"),
                "code": sensor_data.get("code"),
                "value": sensor_data.get("value"),
                "unit": sensor_data.get("unit", "N/A"),
                "timestamp": sensor_data.get("date", datetime.now().isoformat())
            }
            
            print(f"📡 Enviando datos al backend: {payload}")
            
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Datos enviados exitosamente al backend: {response.json()}")
                return True
            else:
                print(f"❌ Error al enviar datos: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout al enviar datos al backend")
            return False
        except requests.exceptions.ConnectionError:
            print("🔌 Error de conexión con el backend")
            return False
        except Exception as e:
            print(f"❌ Error inesperado enviando datos: {e}")
            return False
    
    def enviar_lote_datos(self, datos_sensores: list):
        """
        Envía múltiples datos de sensores en lote
        
        Args:
            datos_sensores: Lista de diccionarios con datos de sensores
        """
        try:
            payload = {
                "sensor_data": datos_sensores,
                "timestamp": datetime.now().isoformat()
            }
            
            batch_endpoint = f"{self.api_url}/api/sensor-data/batch"
            
            response = requests.post(
                batch_endpoint,
                json=payload,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ Lote de {len(datos_sensores)} datos enviado exitosamente")
                return True
            else:
                print(f"❌ Error enviando lote: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando lote de datos: {e}")
            return False

# Función helper para cargar y enviar datos desde archivos JSON
def procesar_y_enviar_datos_pendientes(archivo_online="Jsons_DATA/data_sensores_online.json"):
    """
    Lee los datos pendientes del archivo JSON y los envía al backend
    """
    try:
        if not os.path.exists(archivo_online):
            print("📂 No hay archivo de datos pendientes")
            return
            
        with open(archivo_online, 'r', encoding='utf-8') as f:
            datos_pendientes = json.load(f)
            
        if not datos_pendientes:
            print("📊 No hay datos pendientes para enviar")
            return
            
        sender = HTTPSender()
        datos_enviados = 0
        datos_fallidos = 0
        
        # Agrupar datos por tanque para optimizar el envío
        datos_por_tanque = {}
        for dato in datos_pendientes:
            tank_id = dato.get('id_tank')
            if tank_id not in datos_por_tanque:
                datos_por_tanque[tank_id] = []
            datos_por_tanque[tank_id].append(dato)
        
        # Enviar datos agrupados por tanque
        for tank_id, datos_tanque in datos_por_tanque.items():
            for dato in datos_tanque:
                if sender.enviar_datos_sensor(tank_id, dato):
                    datos_enviados += 1
                else:
                    datos_fallidos += 1
        
        print(f"📊 Resumen del envío:")
        print(f"   ✅ Datos enviados: {datos_enviados}")
        print(f"   ❌ Datos fallidos: {datos_fallidos}")
        
        # Si todos los datos se enviaron correctamente, limpiar el archivo
        if datos_fallidos == 0 and datos_enviados > 0:
            with open(archivo_online, 'w', encoding='utf-8') as f:
                json.dump([], f)
            print("🧹 Archivo de datos pendientes limpiado")
        
    except Exception as e:
        print(f"❌ Error procesando datos pendientes: {e}")

if __name__ == "__main__":
    # Prueba del sistema
    sender = HTTPSender()
    
    # Datos de prueba
    dato_prueba = {
        "sensor": "temp",
        "deviceId": 1,
        "code": "temp/1", 
        "value": 24.5,
        "unit": "°C",
        "date": datetime.now().isoformat()
    }
    
    sender.enviar_datos_sensor(1, dato_prueba)
