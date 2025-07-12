import json
import serial
import time
from datetime import datetime
from Clases.lista import Lista
from Clases.dataSensores import dataSensores

def cargar_mapa_dispositivos(path="Jsons_DATA/devices.json"):
    with open(path, "r", encoding="utf-8") as f:
        lista = json.load(f)
    return {d["name"]: d["id"] for d in lista}

def cargar_datos_existentes(archivo_salida):
    """Carga los datos existentes del archivo JSON"""
    try:
        with open(archivo_salida, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if contenido:
                return json.loads(contenido)
            else:
                return []
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"⚠️ Error al cargar datos existentes: {e}")
        return []

def obtener_siguiente_id(datos_existentes):
    """Obtiene el siguiente ID disponible"""
    if not datos_existentes:
        return 1
    return max(dato.get("id", 0) for dato in datos_existentes) + 1

def leer_serial_y_guardar(puerto='COM3', baudios=9600, archivo_salida="Jsons_DATA/data_sensores_local.json"):
    mapa = cargar_mapa_dispositivos()
    
    try:
        arduino = serial.Serial(puerto, baudios, timeout=2)
        time.sleep(2)
        print("📡 Conectado al puerto serial. Esperando datos...")
        
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                print(f"📨 Recibido: {linea}")
                
                if ':' in linea:
                    sensor, valor = linea.split(":")
                    if sensor in mapa:
                        try:
                            valor = float(valor)
                        except ValueError:
                            print("❌ Valor no numérico.")
                            continue
                        
                        fecha = datetime.now().isoformat()
                        
                        # Cargar datos existentes
                        datos_existentes = cargar_datos_existentes(archivo_salida)
                        
                        # Crear nuevo dato
                        nuevo_dato = {
                            "id": obtener_siguiente_id(datos_existentes),
                            "id_tank": 1,
                            "sensor": sensor,
                            "value": valor,
                            "unit": "N/A",
                            "date": fecha,
                            "synced": False
                        }
                        
                        # Agregar el nuevo dato a la lista existente
                        datos_existentes.append(nuevo_dato)
                        
                        # Guardar todos los datos (acumulativos)
                        with open(archivo_salida, "w", encoding="utf-8") as f:
                            json.dump(datos_existentes, f, indent=4, ensure_ascii=False)
                        
                        print(f"✅ Guardado: {nuevo_dato}")
                        print(f"📊 Total datos en archivo: {len(datos_existentes)}")
                    
                    else:
                        print(f"❌ Sensor desconocido: {sensor}")
                else:
                    print("❌ Formato inválido: se esperaba 'sensor:valor'")
    
    except serial.SerialException as e:
        print(f"🛑 Error de conexión serial: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario")
    finally:
        if 'arduino' in locals():
            arduino.close()
            print("🔌 Conexión serial cerrada")

if __name__ == "__main__":
    leer_serial_y_guardar()