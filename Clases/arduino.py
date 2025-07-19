import json
import serial
import time
from datetime import datetime

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

# Función principal para leer datos del Arduino y guardarlos en JSON local
def leer_serial_y_guardar(puerto='COM3', baudios=9600, archivo_salida="Jsons_DATA/data_sensores_local.json"):
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
                        datos_existentes = cargar_datos_existentes(archivo_salida)

                        nuevo_dato = {
                            "id": obtener_siguiente_id(datos_existentes),
                            "id_tank": mapa[sensor_code]["tank_id"],  # Aquí ya es dinámico, según el sensor
                            "sensor": sensor_code.split("/")[0],
                            "deviceId": mapa[sensor_code]["device_id"],
                            "code": sensor_code,
                            "value": valor,
                            "unit": "N/A",
                            "date": fecha,
                            "synced": False
                        }


                        datos_existentes.append(nuevo_dato)

                        with open(archivo_salida, "w", encoding="utf-8") as f:
                            json.dump(datos_existentes, f, indent=4, ensure_ascii=False)

                        print(f"✅ Guardado: {nuevo_dato}")
                        print(f"📊 Total datos en archivo: {len(datos_existentes)}")

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
