import json
import serial
import time
from datetime import datetime
try:
    from .http_sender import HTTPSender
    HTTP_ENABLED = True
except ImportError:
    print("⚠️ HTTPSender no disponible. Funcionando solo en modo local.")
    HTTP_ENABLED = False

# Cargar mapa de sensores desde archivo JSON
def cargar_mapa_dispositivos(path="Jsons_DATA/devices.json"):
    with open(path, "r", encoding="utf-8") as f:
        lista = json.load(f)
    # El mapa tendrá como clave el 'code' (ej. "temp/1") y como valor el id del dispositivo
    return {d["code"]: d["id"] for d in lista}

# Cargar datos existentes del archivo de salida
def cargar_datos_existentes(archivo_salida):
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

# Obtener el siguiente ID disponible
def obtener_siguiente_id(datos_existentes):
    if not datos_existentes:
        return 1
    return max(dato.get("id", 0) for dato in datos_existentes) + 1

# Función para leer una sola vez los datos del Arduino
def leer_serial_una_vez(puerto='COM3', baudios=9600, archivo_salida="Jsons_DATA/data_sensores_online.json", archivo_historial="Jsons_DATA/data_sensores_local.json", timeout_lectura=10):
    mapa = cargar_mapa_dispositivos()  # Mapa: { "temp/1": 1, "hmd/1": 2, ... }
    
    try:
        arduino = serial.Serial(puerto, baudios, timeout=2)
        time.sleep(2)
        print("📡 Conectado al puerto serial. Leyendo datos...")
        
        tiempo_inicio = time.time()
        datos_leidos = 0
        
        # Leer por un tiempo limitado o hasta obtener algunos datos
        while time.time() - tiempo_inicio < timeout_lectura:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                print(f"📨 Recibido: {linea}")
                
                if ':' in linea:
                    sensor_code, valor = linea.split(":")
                    
                    if sensor_code in mapa:
                        try:
                            valor = float(valor)
                        except ValueError:
                            print("❌ Valor no numérico.")
                            continue
                        
                        fecha = datetime.now().isoformat()
                        datos_online = cargar_datos_existentes(archivo_salida)
                        datos_historial = cargar_datos_existentes(archivo_historial)
                        
                        # ID para archivo online (basado en los datos online)
                        id_online = obtener_siguiente_id(datos_online)
                        # ID para archivo historial (basado en el historial completo)
                        id_historial = obtener_siguiente_id(datos_historial)
                        
                        nuevo_dato_online = {
                            "id": id_online,
                            "id_tank": mapa[sensor_code],
                            "sensor": sensor_code.split("/")[0],
                            "deviceId": mapa[sensor_code],
                            "code": sensor_code,
                            "value": valor,
                            "unit": "N/A",
                            "date": fecha,
                            "synced": False
                        }
                        
                        nuevo_dato_historial = {
                            "id": id_historial,
                            "id_tank": mapa[sensor_code],
                            "sensor": sensor_code.split("/")[0],
                            "deviceId": mapa[sensor_code],
                            "code": sensor_code,
                            "value": valor,
                            "unit": "N/A",
                            "date": fecha,
                            "synced": False
                        }
                        
                        # Guardar en archivo online (para sincronización inmediata)
                        datos_online.append(nuevo_dato_online)
                        with open(archivo_salida, "w", encoding="utf-8") as f:
                            json.dump(datos_online, f, indent=4, ensure_ascii=False)
                        
                        # Guardar en archivo historial (registro general)
                        datos_historial.append(nuevo_dato_historial)
                        with open(archivo_historial, "w", encoding="utf-8") as f:
                            json.dump(datos_historial, f, indent=4, ensure_ascii=False)
                        
                        print(f"✅ Guardado en online: {nuevo_dato_online}")
                        print(f"✅ Guardado en historial: {nuevo_dato_historial}")
                        print(f"📊 Total datos online: {len(datos_online)} | Historial: {len(datos_historial)}")
                        datos_leidos += 1
                        
                    else:
                        print(f"❌ Sensor desconocido: {sensor_code}")
                else:
                    print("❌ Formato inválido. Se esperaba 'sensor:valor'")
            
            time.sleep(0.1)  # Pequeña pausa para no sobrecargar el CPU
        
        print(f"📋 Sesión de lectura completada. Datos leídos: {datos_leidos}")
        
    except serial.SerialException as e:
        print(f"🛑 Error de conexión serial: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if 'arduino' in locals():
            arduino.close()
            print("🔌 Conexión serial cerrada")

# Función principal para leer datos del Arduino y guardarlos en JSON local (versión continua)
def leer_serial_y_guardar(puerto='COM3', baudios=9600, archivo_salida="Jsons_DATA/data_sensores_online.json", archivo_historial="Jsons_DATA/data_sensores_local.json"):
    mapa = cargar_mapa_dispositivos()  # Mapa: { "temp/1": 1, "hmd/1": 2, ... }

    try:
        arduino = serial.Serial(puerto, baudios, timeout=2)
        time.sleep(2)
        print("📡 Conectado al puerto serial. Esperando datos...")

        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8').strip()
                print(f"📨 Recibido: {linea}")

                if ':' in linea:
                    sensor_code, valor = linea.split(":")

                    if sensor_code in mapa:
                        try:
                            valor = float(valor)
                        except ValueError:
                            print("❌ Valor no numérico.")
                            continue

                        fecha = datetime.now().isoformat()
                        datos_online = cargar_datos_existentes(archivo_salida)
                        datos_historial = cargar_datos_existentes(archivo_historial)
                        
                        # ID para archivo online
                        id_online = obtener_siguiente_id(datos_online)
                        # ID para archivo historial
                        id_historial = obtener_siguiente_id(datos_historial)

                        nuevo_dato_online = {
                            "id": id_online,
                            "id_tank": mapa[sensor_code],
                            "sensor": sensor_code.split("/")[0],
                            "deviceId": mapa[sensor_code],
                            "code": sensor_code,
                            "value": valor,
                            "unit": "N/A",
                            "date": fecha,
                            "synced": False
                        }
                        
                        nuevo_dato_historial = {
                            "id": id_historial,
                            "id_tank": mapa[sensor_code],
                            "sensor": sensor_code.split("/")[0],
                            "deviceId": mapa[sensor_code],
                            "code": sensor_code,
                            "value": valor,
                            "unit": "N/A",
                            "date": fecha,
                            "synced": False
                        }

                        # Guardar en archivo online
                        datos_online.append(nuevo_dato_online)
                        with open(archivo_salida, "w", encoding="utf-8") as f:
                            json.dump(datos_online, f, indent=4, ensure_ascii=False)
                            
                        # Guardar en archivo historial
                        datos_historial.append(nuevo_dato_historial)
                        with open(archivo_historial, "w", encoding="utf-8") as f:
                            json.dump(datos_historial, f, indent=4, ensure_ascii=False)

                        print(f"✅ Guardado en online: {nuevo_dato_online}")
                        print(f"✅ Guardado en historial: {nuevo_dato_historial}")
                        print(f"📊 Total datos online: {len(datos_online)} | Historial: {len(datos_historial)}")

                    else:
                        print(f"❌ Sensor desconocido: {sensor_code}")
                else:
                    print("❌ Formato inválido. Se esperaba 'sensor:valor'")

    except serial.SerialException as e:
        print(f"🛑 Error de conexión serial: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario.")
    finally:
        if 'arduino' in locals():
            arduino.close()
            print("🔌 Conexión serial cerrada")

# Punto de entrada
if __name__ == "__main__":
    leer_serial_y_guardar()
